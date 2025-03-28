# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
from moviepy import AudioFileClip
import hashlib

# 自定义颜色
MY_DARK_BLUE = "#1E3A8A"  # 深蓝色
MY_LIGHT_GRAY = "#F3F4F6"  # 浅灰色
MY_MEDIUM_GRAY = "#D1D5DB"  # 中灰色
MY_GOLD = "#F59E0B"  # 金色
MY_ORANGE = "#F97316"  # 橙色
MY_RED = "#DC2626"  # 红色
MY_WHITE = "#FFFFFF"  # 白色
MY_BLACK = "#000000"  # 黑色

CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


class CustomVoiceoverTracker:
    def __init__(self, audio_path, duration):
        self.audio_path = audio_path
        self.duration = duration


def get_cache_filename(text):
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}.mp3")


@contextmanager
def custom_voiceover_tts(text, token="123456", base_url="https://uni-ai.fly.dev/api/manim/tts"):
    cache_file = get_cache_filename(text)

    if os.path.exists(cache_file):
        audio_file = cache_file
    else:
        input_text = requests.utils.quote(text)
        url = f"{base_url}?token={token}&input={input_text}"

        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"TTS 接口错误: {response.status_code} - {response.text}")

        with open(cache_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        audio_file = cache_file

    clip = AudioFileClip(audio_file)
    duration = clip.duration
    clip.close()

    tracker = CustomVoiceoverTracker(audio_file, duration)
    try:
        yield tracker
    finally:
        pass  # 根据需要决定是否清理缓存


# -----------------------------
# CombinedScene：整合所有场景并添加字幕和音频
# -----------------------------
class CombinedScene(MovingCameraScene):
    """
    合并所有场景的 Manim 动画，用于讲解如何求解函数 f(x)=x^2 的切线方程。
    """

    def construct(self):
        self.scene_time_tracker = ValueTracker(0)
        # --- 场景一：欢迎介绍与星空背景 ---
        self.play_scene_01()
        self.clear_and_reset()

    def get_scene_number(self, number_str):
        """创建并定位场景编号"""
        scene_num = Text(number_str, font_size=24, color=MY_WHITE)
        scene_num.to_corner(UR, buff=0.5)
        return scene_num

    def clear_and_reset(self):
        """清除当前场景所有对象并重置相机"""
        valid_mobjects = [m for m in self.mobjects if m is not None]
        all_mobjects = Group(*valid_mobjects)
        for mob in self.mobjects:
            if mob is not None:
                mob.clear_updaters()
        if all_mobjects:
            self.play(FadeOut(all_mobjects, shift=DOWN * 0.5), run_time=0.5)
        self.clear()
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        self.scene_time_tracker.set_value(0)
        # self.wait(0.5)

    def star_updater(self, star, dt):
        """更新星星透明度，实现闪烁效果"""
        base_opacity = getattr(star, "base_opacity", 0.5)
        frequency = getattr(star, "frequency", 0.5)
        phase = getattr(star, "phase", 0)
        current_time = self.scene_time_tracker.get_value()
        opacity_variation = 0.4 * np.sin(2 * PI * frequency * current_time + phase)
        target_opacity = np.clip(base_opacity + opacity_variation, 0.1, 0.9)
        star.set_opacity(target_opacity)

    def play_scene_01(self):
        self.scene_time_tracker.set_value(0)

        # 背景和星空
        bg1 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=MY_DARK_BLUE,
            fill_opacity=1.0,
            stroke_width=0
        )
        bg1.set_z_index(-10)
        self.add(bg1)

        stars = VGroup()
        num_stars = 200
        for _ in range(num_stars):
            x_pos = np.random.uniform(-config.frame_width / 2, config.frame_width / 2)
            y_pos = np.random.uniform(-config.frame_height / 2, config.frame_height / 2)
            star_dot = Dot(point=[x_pos, y_pos, 0], radius=0.02, color=MY_WHITE)
            star_dot.base_opacity = np.random.uniform(0.3, 0.7)
            star_dot.frequency = np.random.uniform(0.3, 0.8)
            star_dot.phase = np.random.uniform(0, 2 * PI)
            star_dot.set_opacity(star_dot.base_opacity)
            stars.add(star_dot)
        stars.add_updater(self.star_updater)
        self.add(stars)

        scene_num_01 = self.get_scene_number("01")
        scene_num_01.set_z_index(10)
        self.add(scene_num_01)

        title = Text("大家好，欢迎来到本期数学讲解视频 👋", font_size=48, color=MY_WHITE)
        title.shift(UP * 2.5)
        subtitle_part1 = Text("如何求解函数", font_size=36, color=MY_WHITE)
        subtitle_part2 = MathTex("f(x)=x^2", font_size=42, color=MY_ORANGE)
        subtitle_part3 = Text("的切线方程 🤔", font_size=36, color=MY_WHITE)
        subtitle = VGroup(subtitle_part1, subtitle_part2, subtitle_part3).arrange(RIGHT, buff=0.2)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 提前加载旁白音频，获得音频时长
        voice_text = "大家好，欢迎来到本期数学讲解视频。本期我们将讲解如何求解函数 f(x) 等于 x 平方的切线方程。"
        with custom_voiceover_tts(voice_text) as tracker:
            # 立即开始播放声音
            self.add_sound(tracker.audio_path, time_offset=0)

            # 同时显示屏幕底部的完整字幕，与音频完全同步显示
            subtitle_voice = Text(
                voice_text,
                font_size=32,
                color=MY_WHITE,
                width=config.frame_width - 2,  # 使用width实现自动换行
                should_center=True,  # 字幕居中
            )
            subtitle_voice.to_edge(DOWN, buff=0.5)

            # 同时开始：声音播放 + 底部字幕 + 动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),  # 字幕快速淡入
                    FadeIn(title, shift=UP * 0.5, run_time=1.5),  # 标题动画
                    lag_ratio=0.0  # 同步进行，不延迟
                ),
                run_time=1.5  # 动画总体控制在1.5秒以内
            )

            # 开始副标题的动画 (在声音继续播放时)
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_part1, shift=RIGHT * 0.2),
                    Write(subtitle_part2),
                    FadeIn(subtitle_part3, shift=LEFT * 0.2),
                    lag_ratio=0.2  # 微小延迟让动画更加流畅
                ),
                run_time=2.0
            )

            # 上述动画累计1.5 + 2.0 = 3.5秒，此时若声音没播放完，继续等待声音完成
            elapsed_time = 3.5
            remaining_time = tracker.duration - elapsed_time - 1.0  # 减去后续字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 最后字幕淡出
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)


# --- Main execution block ---
if __name__ == "__main__":
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 30
    config.output_file = "CombinedScene"
    config.media_dir = "06"
    config.disable_caching = True
    scene = CombinedScene()
    scene.render()
    print("Scene rendering finished.")
