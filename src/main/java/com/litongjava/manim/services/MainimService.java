package com.litongjava.manim.services;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.Lock;

import com.google.common.util.concurrent.Striped;
import com.jfinal.template.Template;
import com.litongjava.db.activerecord.Db;
import com.litongjava.db.activerecord.Row;
import com.litongjava.gemini.GeminiChatRequestVo;
import com.litongjava.gemini.GeminiChatResponseVo;
import com.litongjava.gemini.GeminiClient;
import com.litongjava.gemini.GeminiGenerationConfigVo;
import com.litongjava.gemini.GeminiResponseSchema;
import com.litongjava.gemini.GoogleGeminiModels;
import com.litongjava.linux.LinuxClient;
import com.litongjava.linux.ProcessResult;
import com.litongjava.openai.chat.ChatMessage;
import com.litongjava.template.PromptEngine;
import com.litongjava.tio.utils.crypto.Md5Utils;
import com.litongjava.tio.utils.hutool.FileUtil;
import com.litongjava.tio.utils.hutool.ResourceUtil;
import com.litongjava.tio.utils.hutool.StrUtil;
import com.litongjava.tio.utils.json.JsonUtils;
import com.litongjava.tio.utils.snowflake.SnowflakeIdUtils;
import com.litongjava.vo.ToolVo;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MainimService {
  private Striped<Lock> locks = Striped.lock(1024);

  public void index(String userId, String text, boolean isTelegram) {
    String generatedText = genSence(text);

    String prompt = getSystemPrompt();

    String sence = generatedText + "  \r\nThe generated subtitles and narration must use the language of this message.";
    List<ChatMessage> messages = new ArrayList<>();
    messages.add(new ChatMessage("user", sence));

    GeminiGenerationConfigVo geminiGenerationConfigVo = new GeminiGenerationConfigVo();
    //设置参数
    GeminiResponseSchema pythonCode = GeminiResponseSchema.pythonCode();
    geminiGenerationConfigVo.buildJsonValue().setResponseSchema(pythonCode);
    geminiGenerationConfigVo.setTemperature(0d);

    //请求类
    GeminiChatRequestVo geminiChatRequestVo = new GeminiChatRequestVo();
    geminiChatRequestVo.setChatMessages(messages);
    geminiChatRequestVo.setSystemPrompt(prompt);
    geminiChatRequestVo.setGenerationConfig(geminiGenerationConfigVo);

    log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

    String code = genManaimCode(text, geminiChatRequestVo);

    int indexOf = code.indexOf("```json");
    if (indexOf == -1) {
      log.error("输出中没有找到有效的 JSON 数据:{}", code);
      return;
    }
    String json = code.substring(indexOf + 7, code.length() - 3);
    ToolVo toolVo = JsonUtils.parse(json, ToolVo.class);
    code = toolVo.getCode();
    log.info("code:{}", code);
    ProcessResult executeMainmCode = executeCode(code);

    String stdErr = executeMainmCode.getStdErr();
    if (StrUtil.isNotBlank(stdErr)) {
      log.error("python 第1次执行失败 error:{}", stdErr);
      messages.add(new ChatMessage("model", code));
      messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
      geminiChatRequestVo.setChatMessages(messages);

      log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));
      toolVo = genManimCode(text, geminiChatRequestVo);
      if (toolVo == null) {
        return;
      }
      code = toolVo.getCode();
      log.info("code:{}", code);
      executeMainmCode = executeCode(code);
      stdErr = executeMainmCode.getStdErr();
      if (StrUtil.isNotBlank(stdErr)) {
        log.error("python 第2次执行失败 error:{}", stdErr);
        messages.add(new ChatMessage("model", code));
        messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
        geminiChatRequestVo.setChatMessages(messages);

        log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

        toolVo = genManimCode(text, geminiChatRequestVo);
        if (toolVo == null) {
          return;
        }
        code = toolVo.getCode();
        log.info("code:{}", code);
        executeMainmCode = executeCode(code);

        stdErr = executeMainmCode.getStdErr();
        if (StrUtil.isNotBlank(stdErr)) {
          log.error("python 第3次执行失败 error:{}", stdErr);
          messages.add(new ChatMessage("model", code));
          messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
          geminiChatRequestVo.setChatMessages(messages);

          log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

          toolVo = genManimCode(text, geminiChatRequestVo);
          if (toolVo == null) {
            return;
          }
          code = toolVo.getCode();
          log.info("code:{}", code);
          executeMainmCode = executeCode(code);

          stdErr = executeMainmCode.getStdErr();
          if (StrUtil.isNotBlank(stdErr)) {
            log.error("python 第4次执行失败 error:{}", stdErr);
            messages.add(new ChatMessage("model", code));
            messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
            geminiChatRequestVo.setChatMessages(messages);

            log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

            toolVo = genManimCode(text, geminiChatRequestVo);
            if (toolVo == null) {
              return;
            }
            code = toolVo.getCode();
            log.info("code:{}", code);
            executeMainmCode = executeCode(code);

            stdErr = executeMainmCode.getStdErr();
            if (StrUtil.isNotBlank(stdErr)) {
              log.error("python 第5次执行失败 error:{}", stdErr);
              messages.add(new ChatMessage("model", code));
              messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
              geminiChatRequestVo.setChatMessages(messages);

              log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

              toolVo = genManimCode(text, geminiChatRequestVo);
              if (toolVo == null) {
                return;
              }
              code = toolVo.getCode();
              log.info("code:{}", code);
              executeMainmCode = executeCode(code);

              stdErr = executeMainmCode.getStdErr();
              if (StrUtil.isNotBlank(stdErr)) {
                log.error("python 第6次执行失败 error:{}", stdErr);
                messages.add(new ChatMessage("model", code));
                messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                geminiChatRequestVo.setChatMessages(messages);

                log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                toolVo = genManimCode(text, geminiChatRequestVo);
                if (toolVo == null) {
                  return;
                }
                code = toolVo.getCode();
                log.info("code:{}", code);
                executeMainmCode = executeCode(code);

                stdErr = executeMainmCode.getStdErr();
                if (StrUtil.isNotBlank(stdErr)) {
                  log.error("python 第7次执行失败 error:{}", stdErr);
                  messages.add(new ChatMessage("model", code));
                  messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                  geminiChatRequestVo.setChatMessages(messages);

                  log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                  toolVo = genManimCode(text, geminiChatRequestVo);
                  if (toolVo == null) {
                    return;
                  }
                  code = toolVo.getCode();
                  log.info("code:{}", code);
                  executeMainmCode = executeCode(code);

                  stdErr = executeMainmCode.getStdErr();
                  if (StrUtil.isNotBlank(stdErr)) {
                    log.error("python 第8次执行失败 error:{}", stdErr);
                    messages.add(new ChatMessage("model", code));
                    messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                    geminiChatRequestVo.setChatMessages(messages);

                    log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                    toolVo = genManimCode(text, geminiChatRequestVo);
                    if (toolVo == null) {
                      return;
                    }
                    code = toolVo.getCode();
                    log.info("code:{}", code);
                    executeMainmCode = executeCode(code);

                    stdErr = executeMainmCode.getStdErr();
                    if (StrUtil.isNotBlank(stdErr)) {
                      log.error("python 第9次执行失败 error:{}", stdErr);
                      messages.add(new ChatMessage("model", code));
                      messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                      geminiChatRequestVo.setChatMessages(messages);

                      log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                      toolVo = genManimCode(text, geminiChatRequestVo);
                      if (toolVo == null) {
                        return;
                      }
                      code = toolVo.getCode();
                      log.info("code:{}", code);
                      executeMainmCode = executeCode(code);

                      stdErr = executeMainmCode.getStdErr();
                      if (StrUtil.isNotBlank(stdErr)) {
                        log.error("python 第10次执行失败 error:{}", stdErr);
                        messages.add(new ChatMessage("model", code));
                        messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                        geminiChatRequestVo.setChatMessages(messages);

                        log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                        toolVo = genManimCode(text, geminiChatRequestVo);
                        if (toolVo == null) {
                          return;
                        }
                        code = toolVo.getCode();
                        log.info("code:{}", code);
                        executeMainmCode = executeCode(code);

                        stdErr = executeMainmCode.getStdErr();
                        if (StrUtil.isNotBlank(stdErr)) {
                          log.error("python 第11次执行失败 error:{}", stdErr);
                        }
                      }
                    }
                  }
                }
              }
            }
          }

        } else {
          messages.add(new ChatMessage("model", code));
          messages.add(new ChatMessage("user", "将这个问题写成提示词,防止你下次生成代时再出现这边错误.我要添加到大模型的提示的模板中,英文输出" + stdErr));
          log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));
          String avoidPrompt = genManaimCode(text, geminiChatRequestVo);
          System.out.println(avoidPrompt);
        }
      }
    }
    log.info("json:{}", JsonUtils.toJson(executeMainmCode));
  }

  public String getSystemPrompt() {
    // 生成代码
    URL resource = ResourceUtil.getResource("prompts/gen_video_code_en.txt");
    StringBuilder stringBuffer = FileUtil.readURLAsString(resource);

    URL code_example_01_url = ResourceUtil.getResource("prompts/code_example_01.txt");
    StringBuilder code_example_01 = FileUtil.readURLAsString(code_example_01_url);

    URL code_example_02_url = ResourceUtil.getResource("prompts/code_example_02.txt");
    StringBuilder code_example_02 = FileUtil.readURLAsString(code_example_02_url);

    URL code_example_03_url = ResourceUtil.getResource("prompts/code_example_03.txt");
    StringBuilder code_example_03 = FileUtil.readURLAsString(code_example_03_url);

    String prompt = stringBuffer.toString() + "\r\n## complete Python code example  \r\n" + "\r\n### Example 1  \r\n" + code_example_01 + "\r\n### Example 2  \r\n" + code_example_02
        + "\r\n### Example 1  \r\n" + code_example_03;
    return prompt;
  }

  private ToolVo genManimCode(String text, GeminiChatRequestVo geminiChatRequestVo) {
    String code;
    int indexOf;
    String json;
    ToolVo toolVo;
    code = genManaimCode(text, geminiChatRequestVo);

    indexOf = code.indexOf("```json");
    if (indexOf == -1) {
      log.error("输出中没有找到有效的 JSON 数据:{}", code);
      return null;
    }
    json = code.substring(indexOf + 7, code.length() - 3);
    toolVo = JsonUtils.parse(json, ToolVo.class);
    return toolVo;
  }

  private ProcessResult executeCode(String code) {
    String apiBase = "http://13.216.69.13";
    ProcessResult executeMainmCode = LinuxClient.executeMainmCode(apiBase, "123456", code);
    return executeMainmCode;
  }

  private String genManaimCode(String topic, GeminiChatRequestVo geminiChatRequestVo) {
    GeminiChatResponseVo chatResponse = GeminiClient.generate(GoogleGeminiModels.GEMINI_2_5_PRO_EXP_03_25, geminiChatRequestVo);
    String generatedText = chatResponse.getCandidates().get(0).getContent().getParts().get(0).getText();
    return generatedText;
  }

  public String genSence(String text) {
    String md5 = Md5Utils.getMD5(text);
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
}
