package com.litongjava.manim.services;

import java.util.ArrayList;
import java.util.List;

import com.litongjava.model.body.RespBodyVo;
import com.litongjava.openai.chat.OpenAiChatMessage;
import com.litongjava.openai.chat.OpenAiChatRequestVo;
import com.litongjava.openai.chat.OpenAiChatResponseVo;
import com.litongjava.openai.client.OpenAiClient;
import com.litongjava.template.PromptEngine;
import com.litongjava.tio.utils.environment.EnvUtils;
import com.litongjava.volcengine.VolcEngineConst;
import com.litongjava.volcengine.VolcEngineModels;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ManimService {

  public RespBodyVo genVideo(String topic) {
    String script = genScript(topic);
    log.info("script:{}",script);
    String sence = genSence(script);
    log.info("sence:{}",sence);
    String code = genCode(sence);
    log.info("code:{}",code);
    return RespBodyVo.ok(code);
  }

  public String genCode(String sence) {
    String systemPrompt = PromptEngine.renderToString("gen video_code.txt");
    List<OpenAiChatMessage> messages = new ArrayList<>();
    messages.add(new OpenAiChatMessage("system", systemPrompt));
    messages.add(new OpenAiChatMessage("user", sence));

    OpenAiChatMessage e = new OpenAiChatMessage("assistant", "```python\n");
    e.setPrefix(true);

    messages.add(e);

    OpenAiChatRequestVo chatRequestVo = new OpenAiChatRequestVo();
    chatRequestVo.setStop("```");

    chatRequestVo.setModel(VolcEngineModels.DEEPSEEK_R1_250120);
    chatRequestVo.setStream(false);
    chatRequestVo.setMessages(messages);
    OpenAiChatResponseVo chatResponse = generate(chatRequestVo);
    String content = chatResponse.getChoices().get(0).getMessage().getContent();
    return content;
  }

  public String genSence(String script) {
    String systemPrompt = PromptEngine.renderToString("gen_video_sence.txt");
    List<OpenAiChatMessage> messages = new ArrayList<>();
    messages.add(new OpenAiChatMessage("system", systemPrompt));
    messages.add(new OpenAiChatMessage("user", script));

    OpenAiChatMessage e = new OpenAiChatMessage("assistant", "```latex\n");
    e.setPrefix(true);

    messages.add(e);

    OpenAiChatRequestVo chatRequestVo = new OpenAiChatRequestVo();
    chatRequestVo.setStop("```");

    chatRequestVo.setModel(VolcEngineModels.DEEPSEEK_R1_250120);
    chatRequestVo.setStream(false);
    chatRequestVo.setMessages(messages);
    OpenAiChatResponseVo chatResponse = generate(chatRequestVo);
    String content = chatResponse.getChoices().get(0).getMessage().getContent();
    return content;

  }

  public String genScript(String topic) {
    String systemPrompt = PromptEngine.renderToString("gen_video_script.txt");
    List<OpenAiChatMessage> messages = new ArrayList<>();
    messages.add(new OpenAiChatMessage("system", systemPrompt));
    messages.add(new OpenAiChatMessage("user", topic));

    OpenAiChatResponseVo chatResponse = generate(messages);
    String content = chatResponse.getChoices().get(0).getMessage().getContent();
    return content;
  }

  private OpenAiChatResponseVo generate(OpenAiChatRequestVo chatRequestVo) {
    String apiKey = EnvUtils.getStr("VOLCENGINE_API_KEY");
    OpenAiChatResponseVo chatResponse = OpenAiClient.chatCompletions(VolcEngineConst.BASE_URL, apiKey, chatRequestVo);
    return chatResponse;
  }

  private OpenAiChatResponseVo generate(List<OpenAiChatMessage> messages) {
    String apiKey = EnvUtils.getStr("VOLCENGINE_API_KEY");
    OpenAiChatResponseVo chatResponse = OpenAiClient.chatCompletions(VolcEngineConst.BASE_URL, apiKey, VolcEngineModels.DEEPSEEK_R1_250120, messages);
    return chatResponse;
  }

}
