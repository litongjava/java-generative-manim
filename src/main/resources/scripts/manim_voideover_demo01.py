from manim import *
from custom_voiceover import custom_voiceover_tts  # 导入自定义 voiceover 模块


class CombinedScene(Scene):
    def construct(self):
        # 使用自定义 voiceover 上下文管理器
        with custom_voiceover_tts("今天天天气怎么样") as tracker:
            # 将生成的音频添加到场景中播放
            self.add_sound(tracker.audio_path)
            # 同时展示一段文字，动画时长与旁白音频保持一致
            text_obj = Text("今天天天气怎么样", font_size=36)
            text_obj.to_edge(DOWN)
            self.play(Write(text_obj), run_time=tracker.duration)
            self.wait(1)


if __name__ == "__main__":
    # 基本配置
    config.pixel_height = 1080  # 设置分辨率高
    config.pixel_width = 1920  # 设置分辨率宽
    config.frame_rate = 30  # 设置帧率
    config.output_file = "CombinedScene"  # 指定输出文件名
    config.media_dir = "05"  # 输出目录

    scene = CombinedScene()
    scene.render()
    print("Scene rendering finished.")