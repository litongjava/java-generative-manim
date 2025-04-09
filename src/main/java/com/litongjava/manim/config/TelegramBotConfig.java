package com.litongjava.manim.config;

import org.telegram.telegrambots.longpolling.TelegramBotsLongPollingApplication;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;

import com.litongjava.annotation.AConfiguration;
import com.litongjava.annotation.Initialization;
import com.litongjava.hook.HookCan;
import com.litongjava.manim.bots.MyAmazingBot;
import com.litongjava.tio.utils.environment.EnvUtils;

@AConfiguration
public class TelegramBotConfig {

  @Initialization
  public void config() {
    //非生产环境使用长轮询,生产环境使用WebHook模式
    if(!EnvUtils.isProd()) {
      // 在此填写您的 Bot Token
      String botAuthToken = EnvUtils.getStr("telegram.bot.token");
      // 创建TelegramBotsLongPollingApplication实例，用于管理长轮询Bot的注册与启动
      TelegramBotsLongPollingApplication botsApplication = new TelegramBotsLongPollingApplication();

      try {
        // 注册自定义Bot
        MyAmazingBot updatesConsumer = new MyAmazingBot();
        botsApplication.registerBot(botAuthToken, updatesConsumer);
      } catch (TelegramApiException e) {
        e.printStackTrace();
      }

      // 在应用关闭时调用botsApplication的close方法
      HookCan.me().addDestroyMethod(() -> {
        try {
          botsApplication.unregisterBot(botAuthToken);
          botsApplication.close();
        } catch (Exception e) {
          e.printStackTrace();
        }
      });
    }

  }
}