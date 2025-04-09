package com.litongjava.manim.controller;

import com.litongjava.annotation.RequestPath;
import com.litongjava.tio.boot.http.TioRequestContext;
import com.litongjava.tio.http.common.HttpRequest;
import com.litongjava.tio.http.common.HttpResponse;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RequestPath("/telegram")
public class TelegramWebhookController {

  @RequestPath("/webhook")
  public HttpResponse handleTelegramWebhook(HttpRequest request) {
    String bodyString = request.getBodyString();
    log.info(bodyString);
    return TioRequestContext.getResponse();
  }
}
