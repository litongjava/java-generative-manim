package com.litongjava.manim.config;

import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient;
import org.telegram.telegrambots.meta.generics.TelegramClient;

import com.litongjava.annotation.AConfiguration;
import com.litongjava.annotation.Initialization;
import com.litongjava.telegram.can.TelegramClientCan;
import com.litongjava.tio.utils.environment.EnvUtils;

@AConfiguration
public class TelegramClientConfig {

  @Initialization
  public void config() {
    // 创建TelegramClient实例（使用OkHttp实现）
    String botAuthToken = EnvUtils.getStr("telegram.bot.token");
    TelegramClient telegramClient = new OkHttpTelegramClient(botAuthToken);
    TelegramClientCan.main = telegramClient;
  }
}
