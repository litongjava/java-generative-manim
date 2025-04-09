package com.litongjava.manim.services;

import java.util.HashMap;
import java.util.Map;

import com.jfinal.template.Template;
import com.litongjava.gemini.GeminiClient;
import com.litongjava.gemini.GoogleGeminiModels;
import com.litongjava.manim.vo.TranslatorTextVo;
import com.litongjava.template.PromptEngine;

public class TranslatorService {

  public String translate(TranslatorTextVo translatorTextVo) {
    String srcLang = translatorTextVo.getSrcLang();
    String destLang = translatorTextVo.getDestLang();
    String srcText = translatorTextVo.getSrcText();

    Template template = PromptEngine.getTemplate("translator_prompt.txt");
    Map<String, String> values = new HashMap<>();

    values.put("src_lang", srcLang);
    values.put("dst_lang", destLang);
    values.put("source_text", srcText);

    String prompt = template.renderToString(values);
    String response = GeminiClient.chatWithModel(GoogleGeminiModels.GEMINI_2_0_FLASH_EXP, "user", prompt);
    return response;
  }

  public String translate(String chatId, TranslatorTextVo translatorTextVo) {
    return this.translate(translatorTextVo);
  }
}
