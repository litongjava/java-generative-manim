package com.litongjava.manim.services;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;

import com.jfinal.template.Template;
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
import com.litongjava.tio.utils.hutool.FileUtil;
import com.litongjava.tio.utils.hutool.ResourceUtil;
import com.litongjava.tio.utils.hutool.StrUtil;
import com.litongjava.tio.utils.json.JsonUtils;
import com.litongjava.vo.ToolVo;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MainimService {

  public void index(String userId, String text, boolean isTelegram) {
    String generatedText = genSence(text);

    // 生成代码
    URL resource = ResourceUtil.getResource("prompts/gen_video_code_en.txt");
    StringBuilder prompt = FileUtil.readURLAsString(resource);

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
    geminiChatRequestVo.setSystemPrompt(prompt.toString());
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
    // 生成场景
    Template template = PromptEngine.getTemplate("gen_video_sence_en.txt");
    String prompt = template.renderToString();

    text += "  \r\nplease reply use this message language";
    List<ChatMessage> messages = new ArrayList<>();
    messages.add(new ChatMessage("user", text));

    GeminiChatRequestVo geminiChatRequestVo = new GeminiChatRequestVo();
    geminiChatRequestVo.setChatMessages(messages);
    geminiChatRequestVo.setSystemPrompt(prompt);

    log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

    GeminiChatResponseVo chatResponse = GeminiClient.generate(GoogleGeminiModels.GEMINI_2_0_FLASH, geminiChatRequestVo);
    String generatedText = chatResponse.getCandidates().get(0).getContent().getParts().get(0).getText();
    return generatedText;
  }
}
