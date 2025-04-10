package com.litongjava.manim.services;

import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.api.objects.chat.Chat;

import com.litongjava.jfinal.aop.Aop;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class BotMainimService {

  public void index(Update update) {
    String text = update.getMessage().getText();
    Chat chat = update.getMessage().getChat();
    Long chatIdLong = chat.getId();

    try {
      Aop.get(MainimService.class).index(chatIdLong.toString(), text, true, null);
    } catch (Exception e) {
      log.error("Exception", e);
    }
  }
}
