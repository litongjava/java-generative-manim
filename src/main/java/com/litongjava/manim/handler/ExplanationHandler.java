package com.litongjava.manim.handler;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.services.MainimService;
import com.litongjava.manim.vo.ExplanationVo;
import com.litongjava.tio.boot.http.TioRequestContext;
import com.litongjava.tio.http.common.HttpRequest;
import com.litongjava.tio.http.common.HttpResponse;
import com.litongjava.tio.utils.json.JsonUtils;

public class ExplanationHandler {

  public HttpResponse index(HttpRequest request) {
    HttpResponse response = TioRequestContext.getResponse();
    response.addServerSentEventsHeader();
    response.setSend(false);
    String bodyString = request.getBodyString();
    ExplanationVo xplanationVo = JsonUtils.parse(bodyString, ExplanationVo.class);
    Aop.get(MainimService.class).index(xplanationVo, request.channelContext);
    return response;
  }
}
