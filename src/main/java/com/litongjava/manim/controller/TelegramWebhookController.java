package com.litongjava.manim.controller;

import org.telegram.telegrambots.meta.api.objects.Update;

import com.litongjava.annotation.RequestPath;
import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.services.BotMessageDispatherService;
import com.litongjava.tio.boot.http.TioRequestContext;
import com.litongjava.tio.http.common.HttpRequest;
import com.litongjava.tio.http.common.HttpResponse;
import com.litongjava.tio.utils.json.JacksonUtils;

@RequestPath("/telegram")
public class TelegramWebhookController {

  @RequestPath("/webhook")
  public HttpResponse handleTelegramWebhook(HttpRequest request) {
    String bodyString = request.getBodyString();
    Update update = JacksonUtils.parse(bodyString, Update.class);
    Aop.get(BotMessageDispatherService.class).index(update);
    return TioRequestContext.getResponse();
  }
}
