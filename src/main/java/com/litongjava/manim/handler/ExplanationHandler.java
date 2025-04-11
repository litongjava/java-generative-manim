package com.litongjava.manim.handler;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.services.ExplanationVideoService;
import com.litongjava.manim.vo.ExplanationVo;
import com.litongjava.tio.boot.http.TioRequestContext;
import com.litongjava.tio.core.Tio;
import com.litongjava.tio.http.common.HttpRequest;
import com.litongjava.tio.http.common.HttpResponse;
import com.litongjava.tio.http.server.util.CORSUtils;
import com.litongjava.tio.utils.json.JsonUtils;
import com.litongjava.tio.utils.thread.TioThreadUtils;

public class ExplanationHandler {

  ExplanationVideoService mainimService = Aop.get(ExplanationVideoService.class);

  public HttpResponse index(HttpRequest request) {
    HttpResponse response = TioRequestContext.getResponse();
    CORSUtils.enableCORS(response);
    response.addServerSentEventsHeader();
    Tio.bSend(request.channelContext, response);
    response.setSend(false);
    String bodyString = request.getBodyString();
    ExplanationVo xplanationVo = JsonUtils.parse(bodyString, ExplanationVo.class);
    request.channelContext.setAttribute("type", "SSE");
    

    TioThreadUtils.execute(() -> {
      try {
        mainimService.index(xplanationVo, request.channelContext);
      } catch (Exception e) {
        e.printStackTrace();
      }

    });
    return response;
  }
}
