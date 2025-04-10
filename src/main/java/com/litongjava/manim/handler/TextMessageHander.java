package com.litongjava.manim.handler;

import com.litongjava.tio.boot.http.TioRequestContext;
import com.litongjava.tio.core.ChannelContext;
import com.litongjava.tio.core.Tio;
import com.litongjava.tio.http.common.HttpRequest;
import com.litongjava.tio.http.common.HttpResponse;
import com.litongjava.tio.http.common.sse.SsePacket;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class TextMessageHander {

  public HttpResponse send(HttpRequest httpRequest) {

    ChannelContext channelContext = httpRequest.getChannelContext();
    HttpResponse httpResponse = TioRequestContext.getResponse();

    // 设置sse请求头
    httpResponse.addServerSentEventsHeader();
    // 发送http响应包,告诉客户端保持连接
    Tio.send(channelContext, httpResponse);

    // 发送数据
    sendData(channelContext);
    // 告诉处理器不要将消息发送给客户端
    return httpResponse.setSend(false);
  }

  private void sendData(ChannelContext channelContext) {
    int i=0;
    while(true) {
      String eventName = "message";
      String data = "This is message " + i;
      i++;
      SsePacket ssePacket = new SsePacket().id(i).event(eventName).data(data.getBytes());
      // 再次向客户端发送消息
      Tio.send(channelContext, ssePacket);
      log.info("发送数据:{}", i);
      try {
        Thread.sleep(1000);
      } catch (InterruptedException e) {
        e.printStackTrace();
      }
    }
    // 手动移除连接
    // Tio.remove(channelContext, "remove sse");
  }
}
