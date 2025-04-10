package com.litongjava.manim.services;

import java.util.List;

import com.jfinal.kit.Kv;
import com.litongjava.db.activerecord.Db;
import com.litongjava.db.activerecord.Row;
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
    log.error("python 代码 第1次执行失败 error:{}", stdErr);
    if (channelContext != null) {
      byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("error", "Python code: 1st execution failed"));
      Tio.send(channelContext, new SsePacket("error", jsonBytes));
    }

    ProcessResult executeMainmCode = null;
    final int maxAttempts = 10; // 最多尝试 10 次
    // 用于记录每次调用生成修复代码后的返回结果
    for (int attempt = 1; attempt <= maxAttempts; attempt++) {
      //保存错误日志
      Row row = Row.by("id", SnowflakeIdUtils.id()).set("topic", topic).set("md5", md5).set("python_code", code).set("error", stdErr);
      Db.save("ef_generate_code", row);

      // 构造用户请求消息
      messages.add(new ChatMessage("model", code));
      messages.add(new ChatMessage("user", "代码执行遇到错误,请修复,并输出修复后的代码 " + stdErr));
      geminiChatRequestVo.setChatMessages(messages);

      log.info("fix request {}: {}", attempt, JsonUtils.toSkipNullJson(geminiChatRequestVo));

      // 生成修复后的代码（ToolVo 内部封装了生成的代码）
      ToolVo toolVo = genManimCode(topic, md5, geminiChatRequestVo);
      if (toolVo == null) {
        return null;
      }
      code = toolVo.getCode();
      log.info("修复后的代码: {}", code);

      // 执行修复后的代码
      executeMainmCode = executeCode(code);
      stdErr = executeMainmCode.getStdErr();

      // 如果代码执行有输出（即成功），则根据情况做额外处理（比如构造避免提示）后直接返回结果
      if (StrUtil.isNotBlank(executeMainmCode.getOutput())) {
        // 若第一轮尝试就成功，还附加发送避免下次错误生成的提示
        if (attempt == 1) {
          messages.add(new ChatMessage("model", code));
          messages.add(new ChatMessage("user", "将这个问题写成提示词,防止你下次生成代码时再出现错误.我要添加到大模型的提示模板中,英文输出,格式 ### 【Manim Code Generation Rule: title】 详情,错误信息"));
          String final_request_json = JsonUtils.toSkipNullJson(geminiChatRequestVo);
          log.info("request: {}", final_request_json);
          String avoidPrompt = genManaimCode(topic, md5, geminiChatRequestVo);
          Row row2 = Row.by("id", SnowflakeIdUtils.id()).set("final_request_json", final_request_json).set("prompt", avoidPrompt);
          Db.save("ef_generate_code_avoid_error_prompt", row2);
        }
        return executeMainmCode;
      }
      // 如果执行失败，则记录日志，并通过 SSE 通知前端
      log.error("python 第{}次执行失败 error:{}", attempt + 1, stdErr);
      if (channelContext != null) {
        byte[] jsonBytes = FastJson2Utils.toJSONBytes(Kv.by("error", "Python code: 第" + (attempt + 1) + "次执行失败"));
        Tio.send(channelContext, new SsePacket("error", jsonBytes));
      }
    }

    // 若全部尝试后依然没有成功，就返回最后一次执行结果（可能输出为空）
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
