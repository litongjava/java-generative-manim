package com.litongjava.manim.bots;

import java.util.List;

import org.telegram.telegrambots.meta.api.objects.Update;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.services.BotMessageDispatherService;
import com.litongjava.manim.services.StartService;
import com.litongjava.telegram.bot.service.GetChatIdService;
import com.litongjava.telegram.utils.ChatType;
import com.litongjava.telegram.utils.LongPollingMultiThreadUpdateConsumer;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MyAmazingBot extends LongPollingMultiThreadUpdateConsumer {
  @Override
  public void consume(Update update) {
    if (update.hasMessage() && update.getMessage().hasText()) {
      String receivedText = update.getMessage().getText();
      log.info("Received text message: {}", receivedText);

      // 根据指令进行路由分发
      if ("/get_chat_id".equals(receivedText)) {
        Aop.get(GetChatIdService.class).index(update);
      } else if ("/start".equals(receivedText)) {
        Aop.get(StartService.class).index(update);
      } else if ("/about".equals(receivedText)) {
        Aop.get(StartService.class).about(update);
      } else {
        // 仅当消息来源为私聊时，调用翻译服务处理文本
        if (update.getMessage().getChat().getType().equals(ChatType.chat_private)) {
          Aop.get(BotMessageDispatherService.class).index(update);
        }
      }
    }
  }

  @Override
  public void consumeGroup(List<Update> arg0) {
    for (Update update : arg0) {
      this.consume(update);
    }
  }
}