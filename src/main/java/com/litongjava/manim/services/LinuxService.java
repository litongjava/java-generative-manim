package com.litongjava.manim.services;

import java.io.File;
import java.io.IOException;
import java.util.List;

import com.jfinal.kit.Kv;
import com.litongjava.db.activerecord.Db;
import com.litongjava.db.activerecord.Row;
import com.litongjava.gemini.GeminiChatRequestVo;
import com.litongjava.gemini.GeminiChatResponseVo;
import com.litongjava.gemini.GeminiClient;
import com.litongjava.gemini.GeminiGenerationConfigVo;
import com.litongjava.gemini.GoogleGeminiModels;
import com.litongjava.linux.LinuxClient;
import com.litongjava.linux.ProcessResult;
import com.litongjava.openai.chat.ChatMessage;
import com.litongjava.tio.core.ChannelContext;
import com.litongjava.tio.core.Tio;
import com.litongjava.tio.http.common.sse.SsePacket;
import com.litongjava.tio.utils.hutool.FileUtil;
import com.litongjava.tio.utils.hutool.StrUtil;
import com.litongjava.tio.utils.json.FastJson2Utils;
import com.litongjava.tio.utils.json.JsonUtils;
import com.litongjava.tio.utils.snowflake.SnowflakeIdUtils;
import com.litongjava.vo.ToolVo;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class LinuxService {

  /**
   * run code
   * @param code
   * @return
   */
  public ProcessResult executeCode(String code) {
    String apiBase = "http://13.216.69.13";
    ProcessResult executeMainmCode = LinuxClient.executeMainmCode(apiBase, "123456", code);
    return executeMainmCode;
  }

  /**
   * 最多共会运行时10次
   * @param topic
   * @param code
   * @param stdErr
   * @param messages
   * @param geminiChatRequestVo
   * @param channelContext
   * @return
   */
  public ProcessResult fixCodeAndRerun(final String topic, String md5, String code, String stdErr, List<ChatMessage> messages, GeminiChatRequestVo geminiChatRequestVo, ChannelContext channelContext) {
    // 初始错误日志和 SSE 提示
    log.error("python 代码 第1次执行失败:{}", stdErr);
    if (channelContext != null) {
      byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("progress", "Python code: 1st execution failed"));
      Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
    }

    ProcessResult executeMainmCode = null;
    final int maxAttempts = 10; // 最多尝试 10 次
    // 用于记录每次调用生成修复代码后的返回结果
    for (int attempt = 1; attempt <= maxAttempts; attempt++) {
      //保存错误日志
      //Row row = Row.by("id", SnowflakeIdUtils.id()).set("topic", topic).set("md5", md5).set("python_code", code).set("error", stdErr);
      //Db.save("ef_generate_error_code", row);

      // 构造用户请求消息
      messages.add(new ChatMessage("model", code));
      messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
      geminiChatRequestVo.setChatMessages(messages);

      //log.info("fix request {}: {}", attempt, JsonUtils.toSkipNullJson(geminiChatRequestVo));
      String info = "start fix code " + attempt;
      log.info(info);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info", info));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }
      code = genManaimCode(topic, md5, geminiChatRequestVo);

      info = "finish fix code " + attempt;
      log.info(info);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info", info));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }
      if (code == null) {
        return null;
      }
      //log.info("修复后的代码: {}", code);

      // 执行修复后的代码
      String message = "start run code " + attempt;
      log.info(message);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info", info));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }
      executeMainmCode = executeCode(code);
      stdErr = executeMainmCode.getStdErr();

      message = "run finished " + attempt;
      log.info(message);

      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info ", message));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }

      messages.add(new ChatMessage("model", code));
      messages.add(new ChatMessage("user",
          "将这个问题写成提示词,防止你下次生成代码时再出现错误.我要添加到大模型的提示模板中,英文输出,不用输出代码,格式 ### 【Manim Code Generation Rule: title】 1.Problem Description  2.Reason 3. Correct Practice (Must Follow) 4. Code Example"));
      geminiChatRequestVo.setChatMessages(messages);

      message = "start generate avoid prompt " + attempt;
      log.info(message);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info ", message));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }
      String avoidPrompt = genAvoidPromptCode(geminiChatRequestVo);

      message = "finish generate avoid prompt " + attempt;
      log.info(message);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info ", message));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }

      message = "start save to ef_generate_code_avoid_error_prompt " + attempt;
      log.info(message);
      String final_request_json = JsonUtils.toJson(geminiChatRequestVo);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info ", message));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }

      Row row2 = Row.by("id", SnowflakeIdUtils.id()).set("final_request_json", final_request_json).set("prompt", avoidPrompt);
      Db.save("ef_generate_code_avoid_error_prompt", row2);

      message = "finish save to ef_generate_code_avoid_error_prompt " + attempt;
      log.info(message);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info ", message));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }

      //支持下次生成
      messages.add(new ChatMessage("model", avoidPrompt));

      // 如果代码执行有输出（即成功），则根据情况做额外处理（比如构造避免提示）后直接返回结果
      if (StrUtil.isNotBlank(executeMainmCode.getOutput())) {
        String value = "success " + attempt;
        log.info(value);
        if (channelContext != null) {
          byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("info ", value));
          Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
        }
        log.info("生成成功:{}:", executeMainmCode.getOutput());
        return executeMainmCode;
      }
      // 如果执行失败，则记录日志，并通过 SSE 通知前端
      log.error("python 第{}次执行失败 error:{}", attempt + 1, stdErr);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("error", "Python code: 第" + (attempt + 1) + "次执行失败"));
        Tio.bSend(channelContext, new SsePacket("progress", jsonBytes));
      }
    }
    // 若全部尝试后依然没有成功，就返回最后一次执行结果（可能输出为空）
    return executeMainmCode;
  }

  private String genAvoidPromptCode(GeminiChatRequestVo geminiChatRequestVo) {
    GeminiChatResponseVo chatResponse = null;
    GeminiGenerationConfigVo geminiGenerationConfigVo = new GeminiGenerationConfigVo();
    //设置参数
    geminiGenerationConfigVo.setTemperature(0d);
    geminiChatRequestVo.setGenerationConfig(geminiGenerationConfigVo);

    try {
      chatResponse = GeminiClient.generate(GoogleGeminiModels.GEMINI_2_5_PRO_PREVIEW_03_25, geminiChatRequestVo);
    } catch (Exception e) {
      log.error("Faile to generate code", e);
      return null;
    }

    String generatedText = chatResponse.getCandidates().get(0).getContent().getParts().get(0).getText();
    return generatedText;
  }

  public String genManaimCode(String topic, String md5, GeminiChatRequestVo geminiChatRequestVo) {
    String sql = "select python_code from ef_generate_code where md5=?";
    String pythonCode = Db.queryStr(sql, md5);
    if (pythonCode != null) {
      return pythonCode;
    }

    GeminiChatResponseVo chatResponse = null;
    GeminiGenerationConfigVo geminiGenerationConfigVo = new GeminiGenerationConfigVo();
    //设置参数
    //GeminiResponseSchema pythonCodeSchema = GeminiResponseSchema.pythonCode();
    //geminiGenerationConfigVo.buildJsonValue().setResponseSchema(pythonCodeSchema);

    geminiGenerationConfigVo.setTemperature(0d);
    geminiChatRequestVo.setGenerationConfig(geminiGenerationConfigVo);

    try {
      //chatResponse = GeminiClient.generate(GoogleGeminiModels.GEMINI_2_5_PRO_EXP_03_25, geminiChatRequestVo);
      chatResponse = GeminiClient.generate(GoogleGeminiModels.GEMINI_2_5_PRO_PREVIEW_03_25, geminiChatRequestVo);
    } catch (Exception e) {
      log.error("Faile to generate code:{}", JsonUtils.toJson(geminiChatRequestVo), e);
      return null;
    }

    String generatedText = chatResponse.getCandidates().get(0).getContent().getParts().get(0).getText();

    String code = null;
    int indexOf = generatedText.indexOf("```python");

    if (indexOf == -1) {
      if (generatedText.startsWith("{") && generatedText.endsWith("}")) {
        code = generatedText;

        ToolVo toolVo = null;
        try {
          toolVo = JsonUtils.parse(code.trim(), ToolVo.class);
        } catch (Exception e) {
          log.error("Failed to parse Json:{}", code);
          return null;
        }
        return toolVo.getCode();
      } else {
        log.error("No valid JSON data found in the output.:{}", generatedText);
        return null;
      }
    } else {
      int lastIndexOf = generatedText.lastIndexOf("```");
      log.info("index:{},{}", indexOf, lastIndexOf);
      if (lastIndexOf > 9) {
        try {
          code = generatedText.substring(indexOf + 9, lastIndexOf);
        } catch (Exception e) {
          log.error("generated text:{}", generatedText, e);
          return null;
        }
      } else {
        try {
          code = generatedText.substring(indexOf + 9);
        } catch (Exception e) {
          log.error("generated text:{}", generatedText, e);
          return null;
        }
      }
      new File("script").mkdirs();
      try {
        String path = "script/" + SnowflakeIdUtils.id() + ".py";
        log.info("code file:{}", path);
        FileUtil.writeString(code, path, "UTF-8");
      } catch (IOException e) {
        e.printStackTrace();
      }
      return code;
    }

  }
}
