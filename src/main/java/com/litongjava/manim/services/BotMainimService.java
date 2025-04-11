package com.litongjava.manim.services;

import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.api.objects.chat.Chat;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.vo.ExplanationVo;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class BotMainimService {

  public void index(Update update) {
    String text = update.getMessage().getText();
    Chat chat = update.getMessage().getChat();
    Long chatIdLong = chat.getId();

    ExplanationVo explanationVo = new ExplanationVo(chatIdLong.toString(), text);
    try {
      Aop.get(ExplanationVideoService.class).index(explanationVo, true, null);
    } catch (Exception e) {
      log.error("Exception", e);
    }
  }
}
