package com.litongjava.manim.services;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.Lock;

import com.google.common.util.concurrent.Striped;
import com.jfinal.kit.Kv;
import com.jfinal.template.Template;
import com.litongjava.db.activerecord.Db;
import com.litongjava.db.activerecord.Row;
import com.litongjava.gemini.GeminiChatRequestVo;
import com.litongjava.gemini.GeminiChatResponseVo;
import com.litongjava.gemini.GeminiClient;
import com.litongjava.gemini.GoogleGeminiModels;
import com.litongjava.jfinal.aop.Aop;
import com.litongjava.linux.ProcessResult;
import com.litongjava.manim.vo.ExplanationVo;
import com.litongjava.openai.chat.ChatMessage;
import com.litongjava.template.PromptEngine;
import com.litongjava.tio.core.ChannelContext;
import com.litongjava.tio.core.Tio;
import com.litongjava.tio.http.common.sse.SsePacket;
import com.litongjava.tio.http.server.util.SseEmitter;
import com.litongjava.tio.utils.SystemTimer;
import com.litongjava.tio.utils.crypto.Md5Utils;
import com.litongjava.tio.utils.hutool.FileUtil;
import com.litongjava.tio.utils.hutool.ResourceUtil;
import com.litongjava.tio.utils.hutool.StrUtil;
import com.litongjava.tio.utils.json.FastJson2Utils;
import com.litongjava.tio.utils.json.JsonUtils;
import com.litongjava.tio.utils.snowflake.SnowflakeIdUtils;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MainimService {
  private Striped<Lock> locks = Striped.lock(1024);
  private LinuxService linuxService = Aop.get(LinuxService.class);
  private String video_server_name = "https://manim.collegebot.ai";

  public void index(ExplanationVo xplanationVo, ChannelContext channelContext) {
    String user_id = xplanationVo.getUser_id();
    String prompt = xplanationVo.getPrompt();
    String language = xplanationVo.getLanguage();
    long start = SystemTimer.currTime;
    String videoUrl = this.index(user_id, prompt, language, false, channelContext);
    long end = SystemTimer.currTime;
    if (videoUrl != null) {
      Row row = Row.by("id", SnowflakeIdUtils.id()).set("video_url", videoUrl).set("title", prompt).set("language", language)
          //
          .set("voice_id", xplanationVo.getVoice_id()).set("user_id", user_id).set("elapsed", (end - start));
      Db.save("ef_ugvideo", row);
    }
  }

  public String index(String userId, final String topic, String language, boolean isTelegram, ChannelContext channelContext) {
    String md5 = Md5Utils.getMD5(topic);

    String sql = "select video_url from ef_generate_code where md5=? and language=?";
    String output = Db.queryStr(sql, md5, language);

    if (output != null) {
      log.info("hit cache ef_generate_code");
      String url = video_server_name + output;
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("url", url));
        SsePacket ssePacket = new SsePacket("main", jsonBytes);
        Tio.bSend(channelContext, ssePacket);
        SseEmitter.closeSeeConnection(channelContext);
      }
      return url;

    }

    //    String generatedText = genSence(topic, md5);
    //    if (channelContext != null) {
    //      byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("sence", generatedText));
    //      SsePacket ssePacket = new SsePacket("sence", jsonBytes);
    //      Tio.bSend(channelContext, ssePacket);
    //    }

    String prompt = getSystemPrompt();

    String sence = topic + "  \r\nThe generated subtitles and narration must use the " + language;
    List<ChatMessage> messages = new ArrayList<>();
    messages.add(new ChatMessage("user", sence));

    //请求类
    GeminiChatRequestVo geminiChatRequestVo = new GeminiChatRequestVo();
    geminiChatRequestVo.setChatMessages(messages);
    geminiChatRequestVo.setSystemPrompt(prompt);

    // log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

    String value = "Start generate python code";
    log.info("value:{}", value);

    if (channelContext != null) {
      byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info", value));
      SsePacket ssePacket = new SsePacket("progress", jsonBytes);
      Tio.bSend(channelContext, ssePacket);
    }

    String code = linuxService.genManaimCode(topic, md5, geminiChatRequestVo);
    if (code == null) {
      String info = "Failed to generate python code";
      log.info(info);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("error", info));
        SsePacket ssePacket = new SsePacket("error", jsonBytes);
        Tio.bSend(channelContext, ssePacket);
        SseEmitter.closeSeeConnection(channelContext);
      }
    }

    if (channelContext != null) {
      byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("python_code", code));
      SsePacket ssePacket = new SsePacket("python_code", jsonBytes);
      Tio.bSend(channelContext, ssePacket);
    }

    //log.info("code:{}", code);
    ProcessResult executeMainmCode = linuxService.executeCode(code);

    String stdErr = executeMainmCode.getStdErr();

    if (StrUtil.isBlank(executeMainmCode.getOutput())) {
      executeMainmCode = linuxService.fixCodeAndRerun(topic, md5, code, stdErr, messages, geminiChatRequestVo, channelContext);
    }

    if (executeMainmCode != null && StrUtil.isNotBlank(executeMainmCode.getOutput())) {
      output = executeMainmCode.getOutput();
      String url = video_server_name + output;
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("url", url));
        SsePacket ssePacket = new SsePacket("main", jsonBytes);
        Tio.bSend(channelContext, ssePacket);
      }

      Row row = Row.by("id", SnowflakeIdUtils.id());
      row.set("topic", topic).set("md5", md5);
      row.set("video_url", output).set("language", language);
      Db.save("ef_generate_code", row);
    }
    log.info("result:{}", output);
    SseEmitter.closeSeeConnection(channelContext);
    return output;
  }

  public String genSence(String text, String md5) {
    String sql = "select sence_prompt from ef_generate_sence where md5=?";
    String generatedText = Db.queryStr(sql, md5);
    if (generatedText != null) {
      log.info("Cache Hit ef_generate_sence");
      return generatedText;
    }

    Lock lock = locks.get(md5);
    lock.lock();

    try {
      // 生成场景
      Template template = PromptEngine.getTemplate("gen_video_sence_en.txt");
      String prompt = template.renderToString();

      String userMessageText = text + " \r\nplease reply use this message language.If English is involved, use English vocabulary instead of Pinyin.";
      List<ChatMessage> messages = new ArrayList<>();
      messages.add(new ChatMessage("user", userMessageText));

      GeminiChatRequestVo geminiChatRequestVo = new GeminiChatRequestVo();
      geminiChatRequestVo.setChatMessages(messages);
      geminiChatRequestVo.setSystemPrompt(prompt);

      log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

      GeminiChatResponseVo chatResponse = GeminiClient.generate(GoogleGeminiModels.GEMINI_2_0_FLASH, geminiChatRequestVo);
      generatedText = chatResponse.getCandidates().get(0).getContent().getParts().get(0).getText();
      Row row = Row.by("id", SnowflakeIdUtils.id()).set("topic", text).set("md5", md5).set("sence_prompt", generatedText);
      Db.save("ef_generate_sence", row);
      return generatedText;
    } finally {
      lock.unlock();
    }

  }

  public String genSence(String topic) {
    return this.genSence(topic, Md5Utils.getMD5(topic));
  }

  public String getSystemPrompt() {
    // 生成代码
    URL resource = ResourceUtil.getResource("prompts/gen_video_code_en.txt");
    StringBuilder stringBuffer = FileUtil.readURLAsString(resource);

    String sql = "select prompt from ef_generate_code_avoid_error_prompt";
    List<String> prompts = Db.queryListString(sql);
    if (prompts != null && prompts.size() > 0) {
      for (String string : prompts) {
        stringBuffer.append(string).append("\r\n");
      }
    }
    URL code_example_01_url = ResourceUtil.getResource("prompts/code_example_01.txt");
    StringBuilder code_example_01 = FileUtil.readURLAsString(code_example_01_url);

    URL code_example_02_url = ResourceUtil.getResource("prompts/code_example_02.txt");
    StringBuilder code_example_02 = FileUtil.readURLAsString(code_example_02_url);

    URL code_example_03_url = ResourceUtil.getResource("prompts/code_example_03.txt");
    StringBuilder code_example_03 = FileUtil.readURLAsString(code_example_03_url);

    String prompt = stringBuffer.toString() + "\r\n## complete Python code example  \r\n" + "\r\n### Example 1  \r\n" + code_example_01 + "\r\n### Example 2  \r\n" + code_example_02
        + "\r\n### Example 3  \r\n" + code_example_03;
    return prompt;
  }
}
