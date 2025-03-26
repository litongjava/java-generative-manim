package com.litongjava.manim;
import com.litongjava.annotation.AComponentScan;
import com.litongjava.tio.boot.TioApplication;

@AComponentScan
public class ManimApp {

  public static void main(String[] args) {
    long start = System.currentTimeMillis();
    TioApplication.run(ManimApp.class, args);
    long end = System.currentTimeMillis();
    System.out.println((end - start) + "(ms)");
  }
}
