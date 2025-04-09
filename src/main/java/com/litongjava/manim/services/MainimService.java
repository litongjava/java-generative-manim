package com.litongjava.manim.services;

import java.util.ArrayList;
import java.util.List;

import com.jfinal.template.Template;
import com.litongjava.gemini.GeminiChatRequestVo;
import com.litongjava.gemini.GeminiChatResponseVo;
import com.litongjava.gemini.GeminiClient;
import com.litongjava.gemini.GoogleGeminiModels;
import com.litongjava.openai.chat.ChatMessage;
import com.litongjava.template.PromptEngine;
import com.litongjava.tio.utils.json.JsonUtils;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MainimService {

  public void index(String userId, String text, boolean isTelegram) {
    String generatedText = genSence(text);
    String code = genManaimCode(text, generatedText);
    log.info("code:{}", code);
  }

  private String genManaimCode(String topic, String sence) {
    // 生成代码
    Template template = PromptEngine.getTemplate("gen_video_code_en.txt");
    String prompt = template.renderToString();

    sence += "  \r\nThe generated subtitles and narration must use the language of this message.";
    List<ChatMessage> messages = new ArrayList<>();
    messages.add(new ChatMessage("user", sence));

    GeminiChatRequestVo geminiChatRequestVo = new GeminiChatRequestVo();
    geminiChatRequestVo.setChatMessages(messages);
    geminiChatRequestVo.setSystemPrompt(prompt);

    log.info("request:{}", JsonUtils.toSkipNullJson(geminiChatRequestVo));

    GeminiChatResponseVo chatResponse = GeminiClient.generate(GoogleGeminiModels.GEMINI_2_0_FLASH_EXP, geminiChatRequestVo);
    String generatedText = chatResponse.getCandidates().get(0).getContent().getParts().get(0).getText();
    return generatedText;
  }

  public String genSence(String text) {
    // 生成场景
    Template template = PromptEngine.getTemplate("gen_video_sence_en.txt");
    String prompt = template.renderToString();

    text += "please reply use this message language";
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
