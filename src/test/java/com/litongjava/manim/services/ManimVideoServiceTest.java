package com.litongjava.manim.services;

import org.junit.Test;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.config.AdminAppConfig;
import com.litongjava.manim.vo.ExplanationVo;
import com.litongjava.tio.boot.testing.TioBootTest;

public class ManimVideoServiceTest {

  @Test
  public void test_Kjeldahl() {
    TioBootTest.runWith(AdminAppConfig.class);
    ExplanationVo explanationVo = new ExplanationVo("Chemistry - Kjeldahl Method");
    Aop.get(MainimService.class).index(explanationVo, false, null);
  }

  @Test
  public void test_light() {
    TioBootTest.runWith(AdminAppConfig.class);
    ExplanationVo explanationVo = new ExplanationVo("generate a video about refraction of light");
    explanationVo.setLanguage("English");
    Aop.get(MainimService.class).index(explanationVo, false, null);
  }

  @Test
  public void trigonometricFunctions() {
    TioBootTest.runWith(AdminAppConfig.class);
    ExplanationVo explanationVo = new ExplanationVo("生成一个三角函数讲解视频");
    Aop.get(MainimService.class).index(explanationVo, false, null);
  }

  @Test
  public void getSystemPrompt() {
    TioBootTest.runWith(AdminAppConfig.class);
    String systemPrompt = Aop.get(MainimService.class).getSystemPrompt();
    System.out.println(systemPrompt);
  }

  @Test
  public void genSence() {
    TioBootTest.runWith(AdminAppConfig.class);
    Aop.get(MainimService.class).genSence("什么是向量");
  }

}
