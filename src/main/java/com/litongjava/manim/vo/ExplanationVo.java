package com.litongjava.manim.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Accessors(chain = true)
//"voice_provider": "openai",
//"voice_id": "default_voice",
//"language": "english",
public class ExplanationVo {

  private String prompt;
  private String voice_provider = "openai";
  private String voice_id = "default_voice";
  private String language = "english";
  private String user_id;

  public ExplanationVo(String text) {
    this.prompt = text;
  }

  public ExplanationVo(String user_id, String text) {
    this.user_id = user_id;
    this.prompt = text;
  }
}
