package com.litongjava.manim.services;

import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.api.objects.chat.Chat;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.vo.TranslatorTextVo;
import com.litongjava.telegram.can.TelegramClientCan;
import com.litongjava.telegram.utils.SendMessageUtils;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class BotTranslateService {

  public void index(Update update) {
    String text = update.getMessage().getText();
    Chat chat = update.getMessage().getChat();
    Long chatIdLong = chat.getId();

    // 根据文本内容判断语言方向
    String srcLang;
    String destLang;
    if (containsChinese(text)) {
      srcLang = "Chinese";
      destLang = "English";
    } else {
      srcLang = "English";
      destLang = "Chinese";
    }

    // 构造翻译请求对象
    TranslatorTextVo translatorTextVo = new TranslatorTextVo();
    translatorTextVo.setSrcText(text);
    translatorTextVo.setSrcLang(srcLang);
    translatorTextVo.setDestLang(destLang);

    String responseText;
    try {
      // 调用翻译服务获取翻译结果
      responseText = Aop.get(TranslatorService.class).translate(chatIdLong.toString(), translatorTextVo);
    } catch (Exception e) {
      log.error("Exception", e);
      responseText = "Exception: " + e.getMessage();
    }

    // 构造 Markdown 格式的消息，将翻译结果发送回用户
    SendMessage markdown = SendMessageUtils.markdown(chatIdLong, responseText);
    TelegramClientCan.execute(markdown);
  }

  /**
   * 判断输入文本是否包含中文字符
   *
   * @param text 输入的文本
   * @return 若包含中文字符，返回 true；否则返回 false
   */
  private boolean containsChinese(String text) {
    if (text == null || text.isEmpty()) {
      return false;
    }
    // 使用正则表达式判断是否含有中文字符
    return text.matches(".*[\\u4e00-\\u9fa5]+.*");
  }
}