package com.litongjava.manim.services;

import org.junit.Test;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.config.AdminAppConfig;
import com.litongjava.tio.boot.testing.TioBootTest;

public class MainimServiceTest {

  @Test
  public void test() {
    TioBootTest.runWith(AdminAppConfig.class);
    Aop.get(MainimService.class).index(null, "什么是向量", false, null);
  }
  
  @Test
  public void trigonometricFunctions() {
    TioBootTest.runWith(AdminAppConfig.class);
    Aop.get(MainimService.class).index(null, "生成一个三角函数讲解视频", false, null);
  }
  
  @Test
  public void getSystemPrompt() {
    String systemPrompt = Aop.get(MainimService.class).getSystemPrompt();
    System.out.println(systemPrompt);
  }

  @Test
  public void genSence() {
    TioBootTest.runWith(AdminAppConfig.class);
    Aop.get(MainimService.class).genSence("什么是向量");
  }

}
