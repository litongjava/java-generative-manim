package com.litongjava.manim.services;

import org.telegram.telegrambots.meta.api.objects.Update;

import com.litongjava.jfinal.aop.Aop;

public class BotMessageDispatherService {

  public void index(Update update) {
    //Aop.get(BotTranslateService.class).index(update);
    Aop.get(BotMainimService.class).index(update);
  }
}
