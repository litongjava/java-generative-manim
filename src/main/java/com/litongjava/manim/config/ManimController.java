package com.litongjava.manim.config;

import com.litongjava.annotation.RequestPath;
import com.litongjava.jfinal.aop.Aop;
import com.litongjava.manim.services.ManimService;
import com.litongjava.model.body.RespBodyVo;

@RequestPath("/manim")
public class ManimController {

  public RespBodyVo video(String topic) {
    return Aop.get(ManimService.class).genVideo(topic);
  }
}
