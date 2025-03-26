package com.litongjava.manim.services;

import org.junit.Test;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.model.body.RespBodyVo;
import com.litongjava.template.PromptEngine;
import com.litongjava.tio.utils.environment.EnvUtils;

public class ManimServiceTest {

  @Test
  public void test() {
    EnvUtils.load();
    String topic = PromptEngine.renderToString("video_question_1.txt");
    RespBodyVo genVideo = Aop.get(ManimService.class).genVideo(topic);
  }

  @Test
  public void genSence() {
    EnvUtils.load();
    String script = PromptEngine.renderToString("video_script_1.txt");
    String sence = Aop.get(ManimService.class).genSence(script);
    System.out.println(sence);
  }
  
  @Test
  public void genCode() {
    EnvUtils.load();
    String script = PromptEngine.renderToString("video_sence_1.txt");
    String sence = Aop.get(ManimService.class).genCode(script);
    System.out.println(sence);
  }

}
