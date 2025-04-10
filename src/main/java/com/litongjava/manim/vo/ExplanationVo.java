package com.litongjava.manim.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Accessors(chain = true)
public class ExplanationVo {
  private String prompt;
  private String voice_provider;
  private String voice_id;
  private String language;
  private String user_id;
}
