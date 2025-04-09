package com.litongjava.manim.services;

import org.junit.Test;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.tio.utils.environment.EnvUtils;

public class MainimServiceTest {

  @Test
  public void test() {
    EnvUtils.load();
    Aop.get(MainimService.class).index(null, "什么是向量", false);
  }

}
