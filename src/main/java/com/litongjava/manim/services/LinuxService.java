package com.litongjava.manim.services;

import java.util.List;

import com.jfinal.kit.Kv;
import com.litongjava.db.activerecord.Db;
import com.litongjava.gemini.GeminiChatRequestVo;
import com.litongjava.gemini.GeminiChatResponseVo;
import com.litongjava.gemini.GeminiClient;
import com.litongjava.gemini.GoogleGeminiModels;
import com.litongjava.linux.LinuxClient;
import com.litongjava.linux.ProcessResult;
import com.litongjava.openai.chat.ChatMessage;
import com.litongjava.tio.core.ChannelContext;
import com.litongjava.tio.core.Tio;
import com.litongjava.tio.http.common.sse.SsePacket;
import com.litongjava.tio.utils.hutool.StrUtil;
import com.litongjava.tio.utils.json.FastJson2Utils;
import com.litongjava.tio.utils.json.JsonUtils;
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
   * @param text
   * @param code
   * @param stdErr
   * @param messages
   * @param geminiChatRequestVo
   * @param channelContext
   * @return
   */
  public ProcessResult fixCodeAndRerun(final String text, String md5, String code, String stdErr, List<ChatMessage> messages, GeminiChatRequestVo geminiChatRequestVo, ChannelContext channelContext) {
    ToolVo toolVo;
    ProcessResult executeMainmCode;
    log.error("python 代码 第1次执行失败 error:{}", stdErr);

    if (channelContext != null) {
      byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("error", "Python code: 1st execution failed"));
      Tio.send(channelContext, new SsePacket("error", jsonBytes));
    }

    messages.add(new ChatMessage("model", code));
    messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
    geminiChatRequestVo.setChatMessages(messages);
    log.info("fix request 1:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

    toolVo = genManimCode(text, md5, geminiChatRequestVo);
    if (toolVo == null) {
      return null;
    }
    code = toolVo.getCode();
    log.info("code:{}", code);
    executeMainmCode = executeCode(code);
    stdErr = executeMainmCode.getStdErr();
    if (StrUtil.isBlank(executeMainmCode.getOutput())) {
      log.error("python 第2次执行失败 error:{}", stdErr);
      messages.add(new ChatMessage("model", code));
      messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
      geminiChatRequestVo.setChatMessages(messages);

      log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

      toolVo = genManimCode(text, md5, geminiChatRequestVo);
      if (toolVo == null) {
        return null;
      }
      code = toolVo.getCode();
      log.info("code:{}", code);
      executeMainmCode = executeCode(code);

      stdErr = executeMainmCode.getStdErr();
      
      if (StrUtil.isBlank(executeMainmCode.getOutput())) {
        log.error("python 第3次执行失败 error:{}", stdErr);
        messages.add(new ChatMessage("model", code));
        messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
        geminiChatRequestVo.setChatMessages(messages);

        log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

        toolVo = genManimCode(text, md5, geminiChatRequestVo);
        if (toolVo == null) {
          return null;
        }
        code = toolVo.getCode();
        log.info("code:{}", code);
        executeMainmCode = executeCode(code);

        stdErr = executeMainmCode.getStdErr();
        if (StrUtil.isBlank(executeMainmCode.getOutput())) {
          log.error("python 第4次执行失败 error:{}", stdErr);
          messages.add(new ChatMessage("model", code));
          messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
          geminiChatRequestVo.setChatMessages(messages);

          log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

          toolVo = genManimCode(text, md5, geminiChatRequestVo);
          if (toolVo == null) {
            return null;
          }
          code = toolVo.getCode();
          log.info("code:{}", code);
          executeMainmCode = executeCode(code);

          stdErr = executeMainmCode.getStdErr();
          if (StrUtil.isBlank(executeMainmCode.getOutput())) {
            log.error("python 第5次执行失败 error:{}", stdErr);
            messages.add(new ChatMessage("model", code));
            messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
            geminiChatRequestVo.setChatMessages(messages);

            log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

            toolVo = genManimCode(text, md5, geminiChatRequestVo);
            if (toolVo == null) {
              return null;
            }
            code = toolVo.getCode();
            log.info("code:{}", code);
            executeMainmCode = executeCode(code);

            stdErr = executeMainmCode.getStdErr();
            if (StrUtil.isBlank(executeMainmCode.getOutput())) {
              log.error("python 第6次执行失败 error:{}", stdErr);
              messages.add(new ChatMessage("model", code));
              messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
              geminiChatRequestVo.setChatMessages(messages);

              log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

              toolVo = genManimCode(text, md5, geminiChatRequestVo);
              if (toolVo == null) {
                return null;
              }
              code = toolVo.getCode();
              log.info("code:{}", code);
              executeMainmCode = executeCode(code);

              stdErr = executeMainmCode.getStdErr();
              if (StrUtil.isBlank(executeMainmCode.getOutput())) {
                log.error("python 第7次执行失败 error:{}", stdErr);
                messages.add(new ChatMessage("model", code));
                messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                geminiChatRequestVo.setChatMessages(messages);

                log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                toolVo = genManimCode(text, md5, geminiChatRequestVo);
                if (toolVo == null) {
                  return null;
                }
                code = toolVo.getCode();
                log.info("code:{}", code);
                executeMainmCode = executeCode(code);

                stdErr = executeMainmCode.getStdErr();
                if (StrUtil.isBlank(executeMainmCode.getOutput())) {
                  log.error("python 第8次执行失败 error:{}", stdErr);
                  messages.add(new ChatMessage("model", code));
                  messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                  geminiChatRequestVo.setChatMessages(messages);

                  log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                  toolVo = genManimCode(text, md5, geminiChatRequestVo);
                  if (toolVo == null) {
                    return null;
                  }
                  code = toolVo.getCode();
                  log.info("code:{}", code);
                  executeMainmCode = executeCode(code);

                  stdErr = executeMainmCode.getStdErr();
                  if (StrUtil.isBlank(executeMainmCode.getOutput())) {
                    log.error("python 第9次执行失败 error:{}", stdErr);
                    messages.add(new ChatMessage("model", code));
                    messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                    geminiChatRequestVo.setChatMessages(messages);

                    log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                    toolVo = genManimCode(text, md5, geminiChatRequestVo);
                    if (toolVo == null) {
                      return null;
                    }
                    code = toolVo.getCode();
                    log.info("code:{}", code);
                    executeMainmCode = executeCode(code);

                    stdErr = executeMainmCode.getStdErr();
                    if (StrUtil.isBlank(executeMainmCode.getOutput())) {
                      log.error("python 第10次执行失败 error:{}", stdErr);
                      messages.add(new ChatMessage("model", code));
                      messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
                      geminiChatRequestVo.setChatMessages(messages);

                      log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

                      toolVo = genManimCode(text, md5, geminiChatRequestVo);
                      if (toolVo == null) {
                        return null;
                      }
                      code = toolVo.getCode();
                      log.info("code:{}", code);
                      executeMainmCode = executeCode(code);

                      stdErr = executeMainmCode.getStdErr();
                      if (StrUtil.isBlank(executeMainmCode.getOutput())) {
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
        String avoidPrompt = genManaimCode(text, md5, geminiChatRequestVo);
        System.out.println(avoidPrompt);
      }
    }
    return executeMainmCode;
  }

  private ToolVo genManimCode(String topic, String md5, GeminiChatRequestVo geminiChatRequestVo) {
    String code;
    int indexOf;
    String json;
    ToolVo toolVo;
    code = genManaimCode(topic, md5, geminiChatRequestVo);

    indexOf = code.indexOf("```json");
    if (indexOf == -1) {
      log.error("输出中没有找到有效的 JSON 数据:{}", code);
      return null;
    }
    json = code.substring(indexOf + 7, code.length() - 3);
    toolVo = JsonUtils.parse(json, ToolVo.class);
    return toolVo;
  }

  public String genManaimCode(String topic, String md5, GeminiChatRequestVo geminiChatRequestVo) {
    String sql = "select python_code from ef_generate_code where md5=?";
    String pythonCode = Db.queryStr(sql, md5);
    if (pythonCode != null) {
      return pythonCode;
    }

    GeminiChatResponseVo chatResponse = GeminiClient.generate(GoogleGeminiModels.GEMINI_2_5_PRO_EXP_03_25, geminiChatRequestVo);
    String generatedText = chatResponse.getCandidates().get(0).getContent().getParts().get(0).getText();
    return generatedText;
  }

}
