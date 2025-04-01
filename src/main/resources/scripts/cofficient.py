# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
from moviepy import AudioFileClip # Correct import for AudioFileClip
import hashlib
import manimpango # For font checking

# --- Custom Colors ---
MY_DARK_BLUE = "#0a192f"  # 深蓝色
MY_BLACK = "#000000"      # 黑色
MY_LIGHT_GRAY = "#E0E0E0" # 浅灰色
MY_DARK_GRAY = "#666666"  # 深灰色
MY_BLUE = "#58C4DD"       # 蓝色
MY_WHITE = "#FFFFFF"      # 白色
MY_YELLOW = "#FFFF00"     # 黄色
MY_ORANGE = "#FFA500"     # 橙色
MY_GOLD = "#FFD700"       # 金色
MY_RED = "#FF0000"         # 红色
MY_TEXT_COLOR_DARK_BG = MY_WHITE # 深色背景上的文本颜色
MY_TEXT_COLOR_LIGHT_BG = MY_BLACK # 浅色背景上的文本颜色
AXIS_LABEL_COLOR = MY_DARK_GRAY # 坐标轴标签颜色
HINT_TEXT_COLOR = MY_BLACK # 提示文本颜色 (浅色背景)


# --- Font Checking ---
DEFAULT_FONT = "Noto Sans CJK SC" # Preferred font
available_fonts = manimpango.list_fonts()
final_font = None

if DEFAULT_FONT in available_fonts:
    print(f"字体 '{DEFAULT_FONT}' 已找到。")
    final_font = DEFAULT_FONT
else:
    print(f"警告: 字体 '{DEFAULT_FONT}' 未找到。正在尝试备用字体...")
    fallback_fonts = ["PingFang SC", "Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    found_fallback = False
    for font in fallback_fonts:
        if font in available_fonts:
            print(f"已切换到备用字体: '{font}'")
            final_font = font
            found_fallback = True
            break
    if not found_fallback:
        print(f"警告: 未找到指定的 '{DEFAULT_FONT}' 或任何备用中文字体。将使用 Manim 默认字体，中文可能无法正确显示。")
        # final_font 保持为 None

# --- TTS Setup ---
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
    audio_file = cache_file # Assume cache hit initially

    if not os.path.exists(cache_file):
        print(f"缓存未命中，正在请求 TTS：{text[:30]}...")
        try:
            input_text = requests.utils.quote(text)
            url = f"{base_url}?token={token}&input={input_text}"

            response = requests.get(url, stream=True, timeout=60) # Added timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("TTS 请求成功，已缓存。")

        except requests.exceptions.RequestException as e:
            print(f"TTS 请求失败: {e}")
            # Fallback: Use a silent audio file of estimated duration? Or raise error?
            # For now, let's raise an error to make the issue clear.
            raise Exception(f"无法生成或获取 TTS 音频: {e}")
        except Exception as e:
            print(f"处理 TTS 响应时出错: {e}")
            raise

    # Verify the audio file exists after attempt
    if not os.path.exists(audio_file):
         raise FileNotFoundError(f"TTS 音频文件未找到或创建失败: {audio_file}")

    # Get duration
    try:
        clip = AudioFileClip(audio_file)
        duration = clip.duration
        clip.close()
        if duration is None or duration <= 0:
             print(f"警告: 获取到的音频时长无效 ({duration})，文件: {audio_file}。将使用估算时长。")
             # Estimate duration based on text length (e.g., 5 chars per second)
             estimated_duration = len(text) / 5.0
             duration = max(estimated_duration, 1.0) # Ensure at least 1 second
    except Exception as e:
        print(f"使用 moviepy 读取音频时长时出错: {e}，文件: {audio_file}。将使用估算时长。")
        estimated_duration = len(text) / 5.0
        duration = max(estimated_duration, 1.0) # Ensure at least 1 second

    tracker = CustomVoiceoverTracker(audio_file, duration)
    try:
        yield tracker
    finally:
        # pass # Keep cache
        # Clean up? Optional: os.remove(audio_file) if not needed after run
        pass


# -----------------------------
# CombinedScene：整合所有场景
# -----------------------------
class CombinedScene(MovingCameraScene):
    """
    合并所有场景的 Manim 动画，用于讲解二次函数系数的影响。
    """
    def setup(self):
        """设置场景，包括字体"""
        MovingCameraScene.setup(self)
        if final_font:
            Text.set_default(font=final_font)
        # 初始化需要在场景间共享的变量
        self.axes = None
        self.graph = None
        self.a_tracker = ValueTracker(1.0)
        self.b_tracker = ValueTracker(0.0)
        self.c_tracker = ValueTracker(0.0)
        self.func_text_group = VGroup() # 用于显示函数和系数
        self.hint_text = VGroup() # 用于显示提示信息
        self.axis_line = None # 对称轴
        self.intercept_dot = None # y轴截距点

    def construct(self):
        """构建动画场景"""
        self.play_scene_01()
        self.clear_and_reset()
        self.play_scene_02()
        # Don't clear yet, scene 3 builds on scene 2
        self.play_scene_03()
        self.clear_and_reset() # Clear before scene 4
        self.play_scene_04()
        # Don't clear yet, scene 5 builds on scene 4 (needs axes)
        self.play_scene_05()
        self.clear_and_reset()
        self.play_scene_06()
        self.wait(2) # Final wait

    def get_scene_number(self, number_str):
        """创建并定位场景编号"""
        scene_num = Text(number_str, font_size=24, color=MY_WHITE)
        scene_num.to_corner(UR, buff=0.5)
        scene_num.set_z_index(100) # Ensure it's on top
        return scene_num

    def clear_and_reset(self):
        """清除当前场景所有对象并重置相机和跟踪器"""
        # Clear updaters from tracked objects first
        if self.graph and hasattr(self.graph, 'clear_updaters'):
            self.graph.clear_updaters()
        if self.axis_line and hasattr(self.axis_line, 'clear_updaters'):
            self.axis_line.clear_updaters()
        if self.intercept_dot and hasattr(self.intercept_dot, 'clear_updaters'):
            self.intercept_dot.clear_updaters()
        # Clear updaters from text if they have them (e.g., DecimalNumber)
        for mob in self.func_text_group:
             if hasattr(mob, 'clear_updaters'):
                 mob.clear_updaters()
             # Special handling for always_redraw MathTex if used
             if isinstance(mob, Mobject) and hasattr(mob, '_original_func'):
                 self.remove(mob) # Remove always_redraw objects

        # Clear all other updaters
        for mob in self.mobjects:
            if mob is not None and hasattr(mob, 'clear_updaters'):
                mob.clear_updaters()

        # Fade out remaining mobjects
        valid_mobjects = [m for m in self.mobjects if m is not None]
        if valid_mobjects:
            all_mobjects_group = Group(*valid_mobjects)
            self.play(FadeOut(all_mobjects_group, shift=DOWN * 0.5), run_time=0.5)

        self.clear() # Manim's clear function

        # Reset camera
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        # Reset trackers to default values for next scene if needed
        self.a_tracker.set_value(1.0)
        self.b_tracker.set_value(0.0)
        self.c_tracker.set_value(0.0)
        # Reset shared mobjects
        self.axes = None
        self.graph = None
        self.func_text_group = VGroup()
        self.hint_text = VGroup()
        self.axis_line = None
        self.intercept_dot = None
        # self.wait(0.1) # Short pause after clearing

    def create_gradient_background(self, color1, color2):
        """创建渐变背景矩形"""
        bg_gradient = Rectangle(
            width=config.frame_width * 1.1, # Slightly larger to avoid edges
            height=config.frame_height * 1.1,
            stroke_width=0,
            fill_color=[color1, color2],
            fill_opacity=1
        )
        bg_gradient.set_sheen_direction(DOWN) # Gradient from top to bottom
        bg_gradient.set_z_index(-10)
        return bg_gradient

    def create_solid_background(self, color):
        """创建纯色背景矩形"""
        bg = Rectangle(
            width=config.frame_width * 1.1,
            height=config.frame_height * 1.1,
            stroke_width=0,
            fill_color=color,
            fill_opacity=1
        )
        bg.set_z_index(-10)
        return bg

    # --- Scene 1: 开场与主题引入 ---
    def play_scene_01(self):
        bg1 = self.create_gradient_background(MY_DARK_BLUE, MY_BLACK)
        scene_num_01 = self.get_scene_number("01")
        self.add(bg1, scene_num_01)

        title_math = MathTex("f(x) = ax^2 + bx + c", font_size=60, color=MY_TEXT_COLOR_DARK_BG)
        title_text = Text("探索二次函数", font_size=48, color=MY_TEXT_COLOR_DARK_BG)
        title_text2 = Text("的奥秘", font_size=48, color=MY_TEXT_COLOR_DARK_BG)
        title_group = VGroup(title_text, title_math, title_text2).arrange(RIGHT, buff=0.3)
        title_group.move_to(UP * 1.5)

        subtitle = Text("系数如何塑造抛物线？ 🤔", font_size=36, color=MY_TEXT_COLOR_DARK_BG)
        subtitle.next_to(title_group, DOWN, buff=0.5)

        # --- Voiceover & Animation ---
        voice_text_scene_01 = "大家好！欢迎来到本期视频。今天我们一起探索二次函数 f(x) = ax^2 + bx + c 的奥秘，看看它的系数 a, b, c 是如何塑造抛物线的形状和位置的。"
        with custom_voiceover_tts(voice_text_scene_01) as tracker:
            self.add_sound(tracker.audio_path)

            subtitle_voice = Text(
                voice_text_scene_01, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_voice.set_z_index(50) # Ensure subtitle is above background elements

            # Create a semi-transparent background for the subtitle
            subtitle_bg = Rectangle(
                width=subtitle_voice.width + 0.4,
                height=subtitle_voice.height + 0.4,
                fill_color=MY_BLACK,
                fill_opacity=0.6,
                stroke_width=0
            )
            subtitle_bg.move_to(subtitle_voice.get_center())
            subtitle_bg.set_z_index(subtitle_voice.z_index - 1) # Place bg behind text
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)


            # Animation Sequence
            anim_duration_intro = 2.5
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    Write(title_group, run_time=anim_duration_intro),
                    lag_ratio=0.0
                ),
                run_time=anim_duration_intro
            )

            anim_duration_subtitle = 1.5
            self.play(FadeIn(subtitle, shift=UP * 0.5, run_time=anim_duration_subtitle))

            # Highlight coefficients
            highlight_time = 0.6
            wait_time = 0.2
            math_part = title_group[1] # Get the MathTex part

            self.play(Indicate(math_part.get_part_by_tex("a"), color=MY_YELLOW, scale_factor=1.5), run_time=highlight_time)
            self.wait(wait_time)
            self.play(Indicate(math_part.get_part_by_tex("b"), color=MY_YELLOW, scale_factor=1.5), run_time=highlight_time)
            self.wait(wait_time)
            self.play(Indicate(math_part.get_part_by_tex("c"), color=MY_YELLOW, scale_factor=1.5), run_time=highlight_time)
            self.wait(wait_time)

            # Camera Zoom
            zoom_duration = 1.5
            self.play(self.camera.frame.animate.scale(1.05), run_time=zoom_duration)

            # Calculate remaining time for voiceover
            total_anim_time = anim_duration_intro + anim_duration_subtitle + 3 * (highlight_time + wait_time) + zoom_duration
            subtitle_fadeout_time = 1.0
            remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
            if remaining_wait > 0:
                self.wait(remaining_wait)

            self.play(FadeOut(subtitle_group), run_time=subtitle_fadeout_time)

        self.wait(0.5) # Pause before clearing

    # --- Scene 2: 基准抛物线与坐标系建立 ---
    def play_scene_02(self):
        bg2 = self.create_solid_background(MY_LIGHT_GRAY)
        scene_num_02 = self.get_scene_number("02").set_color(MY_BLACK) # Black number on light bg
        self.add(bg2, scene_num_02)

        # Create Axes
        self.axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 10, 2],
            x_length=8,
            y_length=6,
            axis_config={
                "stroke_color": MY_DARK_GRAY,
                "include_numbers": True,
                "decimal_number_config": {"num_decimal_places": 0, "color": AXIS_LABEL_COLOR},
            },
            x_axis_config={"color": MY_DARK_GRAY},
            y_axis_config={"color": MY_DARK_GRAY},
            tips=False,
        )
        axis_labels = self.axes.get_axis_labels(x_label="x", y_label="y").set_color(AXIS_LABEL_COLOR)

        # Base function graph
        self.a_tracker.set_value(1.0)
        self.b_tracker.set_value(0.0)
        self.c_tracker.set_value(0.0)
        self.graph = self.axes.plot(
            lambda x: self.a_tracker.get_value() * x**2 + self.b_tracker.get_value() * x + self.c_tracker.get_value(),
            x_range=[-3, 3], # Limit plot range for initial view
            color=MY_BLUE,
            stroke_width=3
        )

        # Function and coefficient text
        func_title = Text("当前函数:", font_size=30, color=MY_TEXT_COLOR_LIGHT_BG)
        func_math = MathTex("f(x) = ax^2 + bx + c", font_size=36, color=MY_TEXT_COLOR_LIGHT_BG)
        coeff_title = Text("系数:", font_size=30, color=MY_TEXT_COLOR_LIGHT_BG)
        coeff_math = MathTex("a=1, b=0, c=0", font_size=36, color=MY_TEXT_COLOR_LIGHT_BG)

        self.func_text_group = VGroup(
            VGroup(func_title, func_math).arrange(RIGHT, buff=0.2),
            VGroup(coeff_title, coeff_math).arrange(RIGHT, buff=0.2)
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        self.func_text_group.to_corner(UL, buff=0.5)

        # --- Voiceover & Animation ---
        voice_text_scene_02 = "首先，我们建立一个二维坐标系。然后，画出最基础的二次函数图像，f(x) = x^2。在这个基准函数中，系数 a 等于 1，b 等于 0，c 等于 0。"
        with custom_voiceover_tts(voice_text_scene_02) as tracker:
            self.add_sound(tracker.audio_path)

            subtitle_voice = Text(
                voice_text_scene_02, font_size=28, color=MY_BLACK, # Black text on light bg
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_voice.set_z_index(50)

            # Subtitle background for light theme
            subtitle_bg = Rectangle(
                width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4,
                fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY
            )
            subtitle_bg.move_to(subtitle_voice.get_center())
            subtitle_bg.set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            # Animation Sequence
            axes_create_time = 1.5
            graph_create_time = 1.5
            text_write_time = 2.0

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    Create(self.axes, run_time=axes_create_time),
                    Write(axis_labels, run_time=axes_create_time),
                    lag_ratio=0.0
                ),
                run_time=axes_create_time
            )
            self.play(Create(self.graph, run_time=graph_create_time))
            self.play(Write(self.func_text_group, run_time=text_write_time))

            # Calculate remaining time
            total_anim_time = axes_create_time + graph_create_time + text_write_time
            subtitle_fadeout_time = 1.0
            remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
            if remaining_wait > 0:
                self.wait(remaining_wait)

            self.play(FadeOut(subtitle_group), run_time=subtitle_fadeout_time)

        # Keep elements for Scene 3
        # self.wait(0.5)

    # --- Scene 3: 系数 'a' 的影响 ---
    def play_scene_03(self):
        # Scene 2 elements (axes, graph, func_text_group) should still be present
        scene_num_03 = self.get_scene_number("03").set_color(MY_BLACK)
        self.add(scene_num_03)

        # Ensure axes are accessible if coming directly from scene 2 setup
        if self.axes is None:
             # Recreate axes if needed (e.g., if running this scene standalone)
             print("Recreating axes for Scene 3")
             self.axes = Axes(x_range=[-4, 4, 1], y_range=[-2, 10, 2], x_length=8, y_length=6,
                              axis_config={"stroke_color": MY_DARK_GRAY, "include_numbers": True, "decimal_number_config": {"num_decimal_places": 0, "color": AXIS_LABEL_COLOR}},
                              x_axis_config={"color": MY_DARK_GRAY}, y_axis_config={"color": MY_DARK_GRAY}, tips=False)
             axis_labels = self.axes.get_axis_labels(x_label="x", y_label="y").set_color(AXIS_LABEL_COLOR)
             self.add(self.axes, axis_labels)
             # Recreate text group
             func_title = Text("当前函数:", font_size=30, color=MY_TEXT_COLOR_LIGHT_BG)
             func_math = MathTex("f(x) = ax^2 + bx + c", font_size=36, color=MY_TEXT_COLOR_LIGHT_BG)
             coeff_title = Text("系数:", font_size=30, color=MY_TEXT_COLOR_LIGHT_BG)
             coeff_math = MathTex("a=1.0, b=0.0, c=0.0", font_size=36, color=MY_TEXT_COLOR_LIGHT_BG) # Use float for consistency
             self.func_text_group = VGroup(VGroup(func_title, func_math).arrange(RIGHT, buff=0.2), VGroup(coeff_title, coeff_math).arrange(RIGHT, buff=0.2)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
             self.func_text_group.to_corner(UL, buff=0.5)
             self.add(self.func_text_group)


        # Highlight 'a' in the formula
        func_math_to_highlight = self.func_text_group[0][1] # MathTex part
        self.play(func_math_to_highlight.animate.set_color_by_tex("a", MY_ORANGE), run_time=0.5)

        # Update coefficient display to be dynamic
        coeff_math_dynamic = always_redraw(lambda: MathTex(
            f"a={self.a_tracker.get_value():.1f}", ", ", "b=0.0, ", "c=0.0",
            font_size=36, color=MY_TEXT_COLOR_LIGHT_BG
        ).move_to(self.func_text_group[1][1], aligned_edge=LEFT)) # Align with original position
        # Highlight 'a' value part
        coeff_math_dynamic.add_updater(lambda m: m.set_color_by_tex(f"a=", MY_ORANGE))

        # Replace static coefficient text with dynamic one
        self.remove(self.func_text_group[1][1]) # Remove static MathTex
        self.func_text_group[1].remove(self.func_text_group[1][1]) # Remove from VGroup structure
        self.func_text_group[1].add(coeff_math_dynamic) # Add dynamic MathTex
        self.add(coeff_math_dynamic) # Add to scene explicitly

        # Make graph dynamic
        self.remove(self.graph) # Remove static graph
        self.graph = always_redraw(lambda: self.axes.plot(
            lambda x: self.a_tracker.get_value() * x**2 + self.b_tracker.get_value() * x + self.c_tracker.get_value(),
            x_range=[-4, 4], # Wider range for updates
            color=MY_BLUE,
            stroke_width=3
            # Use discontinuities to handle a=0 case if needed, but we avoid a=0 here
        ))
        self.add(self.graph)

        # Hint text setup
        hint_text_pos = RIGHT * 3 + UP * 1.5
        self.hint_text = VGroup() # Initialize as empty VGroup

        # --- Voiceover & Animation ---
        voice_text_scene_03_part1 = "现在，我们来看看系数 'a' 的影响。保持 b 和 c 为 0。当 a 大于 1 时，比如从 1 增加到 3，抛物线开口向上，并且开口变得越来越窄。"
        with custom_voiceover_tts(voice_text_scene_03_part1) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_03_part1, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            hint1_part1 = Text("当", font_size=28, color=HINT_TEXT_COLOR)
            hint1_math = MathTex("a > 1", font_size=32, color=HINT_TEXT_COLOR)
            hint1_part2 = Text("，抛物线开口向上，", font_size=28, color=HINT_TEXT_COLOR)
            hint1_part3 = Text("且 a 越大，开口越窄。", font_size=28, color=HINT_TEXT_COLOR)
            hint1 = VGroup(
                VGroup(hint1_part1, hint1_math, hint1_part2).arrange(RIGHT, buff=0.15),
                hint1_part3
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(hint_text_pos)
            self.hint_text = hint1 # Assign to self.hint_text

            anim_a_gt_1_time = tracker.duration - 1.0 # Leave time for fade out

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(self.hint_text, run_time=1.0),
                    self.a_tracker.animate.set_value(3.0),
                    lag_ratio=0.1 # Stagger animations slightly
                ),
                run_time=anim_a_gt_1_time
            )
            self.play(FadeOut(subtitle_group), run_time=1.0)

        voice_text_scene_03_part2 = "如果 a 在 0 和 1 之间，比如从 3 减小到 0.2，抛物线开口仍然向上，但 a 越小，开口变得越宽。"
        with custom_voiceover_tts(voice_text_scene_03_part2) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_03_part2, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            hint2_part1 = Text("当", font_size=28, color=HINT_TEXT_COLOR)
            hint2_math = MathTex("0 < a < 1", font_size=32, color=HINT_TEXT_COLOR)
            hint2_part2 = Text("，抛物线开口向上，", font_size=28, color=HINT_TEXT_COLOR)
            hint2_part3 = Text("且 a 越小，开口越宽。", font_size=28, color=HINT_TEXT_COLOR)
            hint2 = VGroup(
                VGroup(hint2_part1, hint2_math, hint2_part2).arrange(RIGHT, buff=0.15),
                hint2_part3
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(hint_text_pos)

            anim_a_01_time = tracker.duration - 1.0
            self.play(
                 AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    ReplacementTransform(self.hint_text, hint2),
                    self.a_tracker.animate.set_value(0.2),
                    lag_ratio=0.0
                 ),
                 run_time=anim_a_01_time
            )
            self.hint_text = hint2 # Update self.hint_text
            self.play(FadeOut(subtitle_group), run_time=1.0)

        voice_text_scene_03_part3 = "当 a 小于 0 时，比如变为 -1，再变为 -2，抛物线的开口就反转向下了。a 的绝对值大小同样决定开口的宽窄。"
        with custom_voiceover_tts(voice_text_scene_03_part3) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_03_part3, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            hint3_part1 = Text("当", font_size=28, color=HINT_TEXT_COLOR)
            hint3_math = MathTex("a < 0", font_size=32, color=HINT_TEXT_COLOR)
            hint3_part2 = Text("，抛物线开口向下。", font_size=28, color=HINT_TEXT_COLOR)
            hint3_part3 = Text("绝对值", font_size=28, color=HINT_TEXT_COLOR)
            hint3_math2 = MathTex("|a|", font_size=32, color=HINT_TEXT_COLOR)
            hint3_part4 = Text("的大小影响开口宽度。", font_size=28, color=HINT_TEXT_COLOR)
            hint3 = VGroup(
                VGroup(hint3_part1, hint3_math, hint3_part2).arrange(RIGHT, buff=0.15),
                VGroup(hint3_part3, hint3_math2, hint3_part4).arrange(RIGHT, buff=0.15)
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(hint_text_pos)

            anim_a_neg_time = tracker.duration - 1.0
            self.play(FadeIn(subtitle_group, run_time=0.5)) # Fade in subtitle first
            self.play(ReplacementTransform(self.hint_text, hint3), run_time=0.5)
            self.hint_text = hint3 # Update self.hint_text

            # Animate a through negative values
            self.play(self.a_tracker.animate.set_value(-1.0), run_time=anim_a_neg_time / 2)
            self.play(self.a_tracker.animate.set_value(-2.0), run_time=anim_a_neg_time / 2)

            # Ensure total time matches audio
            total_anim_time_part3 = 0.5 + 0.5 + anim_a_neg_time # FadeIn + Replace + Animate a
            remaining_wait_part3 = tracker.duration - total_anim_time_part3 - 1.0
            if remaining_wait_part3 > 0:
                self.wait(remaining_wait_part3)

            self.play(FadeOut(subtitle_group), run_time=1.0)

        # Reset 'a' highlight and remove dynamic text updater before clearing
        self.play(func_math_to_highlight.animate.set_color(MY_TEXT_COLOR_LIGHT_BG), run_time=0.5) # Restore color
        coeff_math_dynamic.clear_updaters()
        self.graph.clear_updaters()
        self.remove(coeff_math_dynamic, self.graph) # Remove updater objects

        self.wait(0.5)

    # --- Scene 4: 系数 'c' 的影响 ---
    def play_scene_04(self):
        bg4 = self.create_solid_background(MY_LIGHT_GRAY)
        scene_num_04 = self.get_scene_number("04").set_color(MY_BLACK)
        self.add(bg4, scene_num_04)

        # Adjust axes range for vertical shift
        self.axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-5, 15, 2], # Adjusted y-range
            x_length=8,
            y_length=7, # Slightly taller y-axis
            axis_config={
                "stroke_color": MY_DARK_GRAY,
                "include_numbers": True,
                "decimal_number_config": {"num_decimal_places": 0, "color": AXIS_LABEL_COLOR},
            },
            x_axis_config={"color": MY_DARK_GRAY},
            y_axis_config={"color": MY_DARK_GRAY},
            tips=False,
        )
        axis_labels = self.axes.get_axis_labels(x_label="x", y_label="y").set_color(AXIS_LABEL_COLOR)
        self.add(self.axes, axis_labels)

        # Reset coefficients and trackers
        self.a_tracker.set_value(1.0)
        self.b_tracker.set_value(0.0)
        self.c_tracker.set_value(0.0) # Start c at 0

        # Function and coefficient text (similar to scene 3 setup)
        func_title = Text("当前函数:", font_size=30, color=MY_TEXT_COLOR_LIGHT_BG)
        func_math = MathTex("f(x) = ax^2 + bx + c", font_size=36, color=MY_TEXT_COLOR_LIGHT_BG)
        coeff_title = Text("系数:", font_size=30, color=MY_TEXT_COLOR_LIGHT_BG)
        # Dynamic coefficient text for 'c'
        coeff_math_dynamic = always_redraw(lambda: MathTex(
            "a=1.0, ", "b=0.0, ", f"c={self.c_tracker.get_value():.1f}",
            font_size=36, color=MY_TEXT_COLOR_LIGHT_BG
        ).move_to(self.func_text_group.get_center() if self.func_text_group else coeff_title.get_center() + DOWN*0.5 + RIGHT*1.5 , aligned_edge=LEFT)) # Adjust positioning as needed
        coeff_math_dynamic.add_updater(lambda m: m.set_color_by_tex(f"c=", MY_ORANGE)) # Highlight c value

        self.func_text_group = VGroup(
            VGroup(func_title, func_math).arrange(RIGHT, buff=0.2),
            VGroup(coeff_title, coeff_math_dynamic).arrange(RIGHT, buff=0.2) # Use dynamic here
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        self.func_text_group.to_corner(UL, buff=0.5)
        self.add(self.func_text_group) # Add the whole group
        self.add(coeff_math_dynamic) # Add the dynamic part separately for the updater

        # Highlight 'c' in the formula
        func_math_to_highlight = self.func_text_group[0][1]
        self.play(func_math_to_highlight.animate.set_color_by_tex("c", MY_ORANGE), run_time=0.5)

        # Dynamic graph
        self.graph = always_redraw(lambda: self.axes.plot(
            lambda x: self.a_tracker.get_value() * x**2 + self.b_tracker.get_value() * x + self.c_tracker.get_value(),
            x_range=[-3.8, 3.8], # Adjust range slightly if needed
            color=MY_BLUE,
            stroke_width=3
        ))
        self.add(self.graph)

        # Dynamic y-intercept dot
        self.intercept_dot = always_redraw(lambda: Dot(
            self.axes.c2p(0, self.c_tracker.get_value()), # Point (0, c)
            color=MY_RED, radius=0.08
        ))
        intercept_label = always_redraw(lambda: MathTex(
            f"(0, {self.c_tracker.get_value():.1f})", font_size=28, color=MY_RED
        ).next_to(self.intercept_dot, RIGHT, buff=0.15))
        self.add(self.intercept_dot, intercept_label)

        # Hint text setup
        hint_text_pos = RIGHT * 3 + UP * 1.5
        self.hint_text = VGroup()

        # --- Voiceover & Animation ---
        voice_text_scene_04_part1 = "接下来看系数 'c'。我们将 a 设回 1，b 保持 0。'c' 控制抛物线的垂直位置。当 c 大于 0，比如从 0 增加到 5，图像整体向上平移 c 个单位。注意看 y 轴上的截点 (0, c) 也跟着移动。"
        with custom_voiceover_tts(voice_text_scene_04_part1) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_04_part1, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            hint1_part1 = Text("系数", font_size=28, color=HINT_TEXT_COLOR)
            hint1_math_c = MathTex("c", font_size=32, color=HINT_TEXT_COLOR)
            hint1_part2 = Text("控制垂直位置。", font_size=28, color=HINT_TEXT_COLOR)
            hint1_part3 = Text("当", font_size=28, color=HINT_TEXT_COLOR)
            hint1_math_cgt0 = MathTex("c > 0", font_size=32, color=HINT_TEXT_COLOR)
            hint1_part4 = Text("，图像向上平移", font_size=28, color=HINT_TEXT_COLOR)
            hint1_math_c2 = MathTex("c", font_size=32, color=HINT_TEXT_COLOR)
            hint1_part5 = Text("单位。", font_size=28, color=HINT_TEXT_COLOR)
            hint1_part6 = Text("截距为", font_size=28, color=HINT_TEXT_COLOR)
            hint1_math_int = MathTex("(0, c)", font_size=32, color=HINT_TEXT_COLOR)
            hint1 = VGroup(
                VGroup(hint1_part1, hint1_math_c, hint1_part2).arrange(RIGHT, buff=0.15),
                VGroup(hint1_part3, hint1_math_cgt0, hint1_part4, hint1_math_c2, hint1_part5).arrange(RIGHT, buff=0.15),
                VGroup(hint1_part6, hint1_math_int).arrange(RIGHT, buff=0.15)
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(hint_text_pos)
            self.hint_text = hint1

            anim_c_gt_0_time = tracker.duration - 1.0
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(self.hint_text, run_time=1.0),
                    self.c_tracker.animate.set_value(5.0),
                    lag_ratio=0.1
                ),
                run_time=anim_c_gt_0_time
            )
            self.play(FadeOut(subtitle_group), run_time=1.0)

        voice_text_scene_04_part2 = "当 c 小于 0 时，比如从 5 减小到 -3，图像则向下平移 c 的绝对值个单位。y 轴截距同样是 (0, c)。"
        with custom_voiceover_tts(voice_text_scene_04_part2) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_04_part2, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            hint2_part1 = Text("当", font_size=28, color=HINT_TEXT_COLOR)
            hint2_math_clt0 = MathTex("c < 0", font_size=32, color=HINT_TEXT_COLOR)
            hint2_part2 = Text("，图像向下平移", font_size=28, color=HINT_TEXT_COLOR)
            hint2_math_abs_c = MathTex("|c|", font_size=32, color=HINT_TEXT_COLOR)
            hint2_part3 = Text("单位。", font_size=28, color=HINT_TEXT_COLOR)
            hint2_part4 = Text("截距变为", font_size=28, color=HINT_TEXT_COLOR)
            hint2_math_int = MathTex("(0, c)", font_size=32, color=HINT_TEXT_COLOR)
            hint2 = VGroup(
                 VGroup(hint2_part1, hint2_math_clt0, hint2_part2, hint2_math_abs_c, hint2_part3).arrange(RIGHT, buff=0.15),
                 VGroup(hint2_part4, hint2_math_int).arrange(RIGHT, buff=0.15)
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(hint_text_pos)

            anim_c_lt_0_time = tracker.duration - 1.0
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    ReplacementTransform(self.hint_text, hint2),
                    self.c_tracker.animate.set_value(-3.0),
                    lag_ratio=0.0
                ),
                run_time=anim_c_lt_0_time
            )
            self.hint_text = hint2
            self.play(FadeOut(subtitle_group), run_time=1.0)

        # Reset 'c' highlight and clear updaters
        self.play(func_math_to_highlight.animate.set_color(MY_TEXT_COLOR_LIGHT_BG), run_time=0.5)
        coeff_math_dynamic.clear_updaters()
        self.graph.clear_updaters()
        self.intercept_dot.clear_updaters()
        intercept_label.clear_updaters()
        self.remove(coeff_math_dynamic, self.graph, self.intercept_dot, intercept_label)

        self.wait(0.5)

    # --- Scene 5: 系数 'b' 的影响 ---
    def play_scene_05(self):
        bg5 = self.create_solid_background(MY_LIGHT_GRAY)
        scene_num_05 = self.get_scene_number("05").set_color(MY_BLACK)
        self.add(bg5, scene_num_05)

        # Adjust axes range for horizontal shift
        self.axes = Axes(
            x_range=[-6, 6, 1], # Wider x-range
            y_range=[-5, 10, 2], # Adjusted y-range
            x_length=10, # Wider x-axis
            y_length=6,
            axis_config={
                "stroke_color": MY_DARK_GRAY,
                "include_numbers": True,
                "decimal_number_config": {"num_decimal_places": 0, "color": AXIS_LABEL_COLOR},
            },
            x_axis_config={"color": MY_DARK_GRAY},
            y_axis_config={"color": MY_DARK_GRAY},
            tips=False,
        )
        axis_labels = self.axes.get_axis_labels(x_label="x", y_label="y").set_color(AXIS_LABEL_COLOR)
        self.add(self.axes, axis_labels)

        # Set initial state: a=1, b=0, c=2
        self.a_tracker.set_value(1.0)
        self.b_tracker.set_value(0.0) # Start b at 0
        self.c_tracker.set_value(2.0) # Start c at 2

        # Function and coefficient text
        func_title = Text("当前函数:", font_size=30, color=MY_TEXT_COLOR_LIGHT_BG)
        func_math = MathTex("f(x) = ax^2 + bx + c", font_size=36, color=MY_TEXT_COLOR_LIGHT_BG)
        coeff_title = Text("系数:", font_size=30, color=MY_TEXT_COLOR_LIGHT_BG)
        # Dynamic coefficient text for 'b'
        coeff_math_dynamic = always_redraw(lambda: MathTex(
            "a=1.0, ", f"b={self.b_tracker.get_value():.1f}", ", ", "c=2.0",
            font_size=36, color=MY_TEXT_COLOR_LIGHT_BG
        ).move_to(self.func_text_group.get_center() if self.func_text_group else coeff_title.get_center() + DOWN*0.5 + RIGHT*1.5 , aligned_edge=LEFT))
        coeff_math_dynamic.add_updater(lambda m: m.set_color_by_tex(f"b=", MY_ORANGE)) # Highlight b value

        self.func_text_group = VGroup(
            VGroup(func_title, func_math).arrange(RIGHT, buff=0.2),
            VGroup(coeff_title, coeff_math_dynamic).arrange(RIGHT, buff=0.2)
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        self.func_text_group.to_corner(UL, buff=0.5)
        self.add(self.func_text_group)
        self.add(coeff_math_dynamic)

        # Highlight 'b' in the formula
        func_math_to_highlight = self.func_text_group[0][1]
        self.play(func_math_to_highlight.animate.set_color_by_tex("b", MY_ORANGE), run_time=0.5)

        # Dynamic graph
        self.graph = always_redraw(lambda: self.axes.plot(
            lambda x: self.a_tracker.get_value() * x**2 + self.b_tracker.get_value() * x + self.c_tracker.get_value(),
            x_range=[-6, 6],
            color=MY_BLUE,
            stroke_width=3
        ))
        self.add(self.graph)

        # Symmetry axis formula
        axis_formula = MathTex("x = -\\frac{b}{2a}", font_size=36, color=MY_DARK_GRAY)
        axis_formula.next_to(self.axes, DOWN, buff=0.3).align_to(self.axes, LEFT).shift(RIGHT*0.5)

        # Dynamic symmetry axis line
        # Need to handle a=0 case if it were possible, but a=1 here.
        self.axis_line = always_redraw(lambda: DashedLine(
                self.axes.c2p(-self.b_tracker.get_value() / (2 * self.a_tracker.get_value()), self.axes.y_range[0]),
                self.axes.c2p(-self.b_tracker.get_value() / (2 * self.a_tracker.get_value()), self.axes.y_range[1]),
                dash_length=0.1,
                stroke_width=2,
                color=MY_DARK_GRAY
            ) if self.a_tracker.get_value() != 0 else VGroup() # Avoid division by zero visually
        )
        self.add(self.axis_line)

        # Hint text setup
        hint_text_pos = RIGHT * 3.5 + UP * 0 # Adjust position
        self.hint_text = VGroup()

        # --- Voiceover & Animation ---
        voice_text_scene_05_part1 = "最后来看系数 'b'。我们设置 a=1, c=2。'b' 会影响抛物线的水平位置和顶点。先看对称轴公式 x = -b / 2a。初始 b=0，对称轴是 y 轴。"
        with custom_voiceover_tts(voice_text_scene_05_part1) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_05_part1, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            # Show axis formula and initial axis
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    Write(axis_formula, run_time=2.0),
                    # Initial axis line is already added via always_redraw
                    lag_ratio=0.0
                ),
                run_time=2.0
            )

            total_anim_time = 2.0
            subtitle_fadeout_time = 1.0
            remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
            if remaining_wait > 0:
                self.wait(remaining_wait)
            self.play(FadeOut(subtitle_group), run_time=subtitle_fadeout_time)


        voice_text_scene_05_part2 = "当 a>0 且 b>0 时，比如 b 从 0 增加到 4，对称轴 x = -b/2a 向左移动，顶点也随之向左移动。"
        with custom_voiceover_tts(voice_text_scene_05_part2) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_05_part2, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            hint1_part1 = Text("当", font_size=28, color=HINT_TEXT_COLOR)
            hint1_math_a = MathTex("a > 0", font_size=32, color=HINT_TEXT_COLOR)
            hint1_part2 = Text("且", font_size=28, color=HINT_TEXT_COLOR)
            hint1_math_b = MathTex("b > 0", font_size=32, color=HINT_TEXT_COLOR)
            hint1_part3 = Text("，对称轴", font_size=28, color=HINT_TEXT_COLOR)
            hint1_math_ax = MathTex("x = -b/2a", font_size=32, color=HINT_TEXT_COLOR)
            hint1_part4 = Text("在 y 轴左侧，", font_size=28, color=HINT_TEXT_COLOR)
            hint1_part5 = Text("顶点向左移动。", font_size=28, color=HINT_TEXT_COLOR)
            hint1 = VGroup(
                VGroup(hint1_part1, hint1_math_a, hint1_part2, hint1_math_b).arrange(RIGHT, buff=0.15),
                VGroup(hint1_part3, hint1_math_ax, hint1_part4).arrange(RIGHT, buff=0.15),
                hint1_part5
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(hint_text_pos)
            self.hint_text = hint1

            anim_b_gt_0_time = tracker.duration - 1.0
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(self.hint_text, run_time=1.0),
                    self.b_tracker.animate.set_value(4.0),
                    lag_ratio=0.1
                ),
                run_time=anim_b_gt_0_time
            )
            self.play(FadeOut(subtitle_group), run_time=1.0)


        voice_text_scene_05_part3 = "当 a>0 且 b<0 时，比如 b 从 4 减小到 -4，对称轴移动到 y 轴右侧，顶点也向右移动。"
        with custom_voiceover_tts(voice_text_scene_05_part3) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_05_part3, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_LIGHT_GRAY, fill_opacity=0.8, stroke_width=1, stroke_color=MY_DARK_GRAY).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            hint2_part1 = Text("当", font_size=28, color=HINT_TEXT_COLOR)
            hint2_math_a = MathTex("a > 0", font_size=32, color=HINT_TEXT_COLOR)
            hint2_part2 = Text("且", font_size=28, color=HINT_TEXT_COLOR)
            hint2_math_b = MathTex("b < 0", font_size=32, color=HINT_TEXT_COLOR)
            hint2_part3 = Text("，对称轴在 y 轴右侧，", font_size=28, color=HINT_TEXT_COLOR)
            hint2_part4 = Text("顶点向右移动。", font_size=28, color=HINT_TEXT_COLOR)
            hint2 = VGroup(
                VGroup(hint2_part1, hint2_math_a, hint2_part2, hint2_math_b).arrange(RIGHT, buff=0.15),
                hint2_part3,
                hint2_part4
            ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(hint_text_pos)

            anim_b_lt_0_time = tracker.duration - 1.0
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    ReplacementTransform(self.hint_text, hint2),
                    self.b_tracker.animate.set_value(-4.0),
                    lag_ratio=0.0
                ),
                run_time=anim_b_lt_0_time
            )
            self.hint_text = hint2
            self.play(FadeOut(subtitle_group), run_time=1.0)

        # Reset 'b' highlight and clear updaters
        self.play(func_math_to_highlight.animate.set_color(MY_TEXT_COLOR_LIGHT_BG), run_time=0.5)
        coeff_math_dynamic.clear_updaters()
        self.graph.clear_updaters()
        self.axis_line.clear_updaters()
        self.remove(coeff_math_dynamic, self.graph, self.axis_line, axis_formula) # Remove formula too

        self.wait(0.5)

    # --- Scene 6: 综合演示与总结 ---
    def play_scene_06(self):
        bg6 = self.create_gradient_background(MY_DARK_BLUE, MY_BLACK)
        scene_num_06 = self.get_scene_number("06") # White number on dark bg
        self.add(bg6, scene_num_06)

        summary_title = Text("总结 ✨", font_size=48, color=MY_GOLD)
        summary_title.to_edge(UP, buff=1.0)

        # --- Manual Summary List ---
        summary_items_text = [
            ("系数 ", MathTex("a", color=MY_ORANGE), "：决定开口方向 (", MathTex("a>0", color=MY_BLUE), " 向上, ", MathTex("a<0", color=MY_RED), " 向下) 和开口大小 (", MathTex("|a|", color=MY_ORANGE), " 越大越窄)。"),
            ("系数 ", MathTex("c", color=MY_ORANGE), "：决定抛物线与 y 轴的交点 ", MathTex("(0, c)", color=MY_RED), "，控制垂直平移。"),
            ("系数 ", MathTex("b", color=MY_ORANGE), "：与 ", MathTex("a", color=MY_ORANGE), " 共同决定对称轴 ", MathTex("x = -\\frac{b}{2a}", color=MY_DARK_GRAY), " 和顶点位置，影响水平位置。")
        ]

        summary_list_group = VGroup()
        item_font_size = 32
        line_buff = 0.5 # Line spacing
        item_color = MY_WHITE

        for item_parts in summary_items_text:
            line_vgroup = VGroup()
            for part in item_parts:
                if isinstance(part, str):
                    line_vgroup.add(Text(part, font_size=item_font_size, color=item_color))
                elif isinstance(part, MathTex):
                    # Ensure MathTex parts also have appropriate size
                    part.set_font_size(item_font_size * 1.1) # Slightly larger for math
                    line_vgroup.add(part)
            # Arrange parts horizontally
            line_vgroup.arrange(RIGHT, buff=0.15)
            summary_list_group.add(line_vgroup)

        # Arrange lines vertically
        summary_list_group.arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
        summary_list_group.next_to(summary_title, DOWN, buff=0.8)
        # Center the list horizontally
        summary_list_group.move_to(ORIGIN + DOWN * 0.5)


        # --- Voiceover & Animation ---
        voice_text_scene_06 = "好了，让我们来总结一下：系数 a 决定抛物线的开口方向和胖瘦；系数 c 决定图像的垂直位置，也就是它与 y 轴的交点；而系数 b 则与 a 一起，共同决定了对称轴和顶点的位置，从而影响图像的水平位置。希望这个视频能帮助你更好地理解二次函数！"
        with custom_voiceover_tts(voice_text_scene_06) as tracker:
            self.add_sound(tracker.audio_path)
            subtitle_voice = Text(voice_text_scene_06, font_size=28, color=MY_WHITE, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5).set_z_index(50)
            subtitle_bg = Rectangle(width=subtitle_voice.width + 0.4, height=subtitle_voice.height + 0.4, fill_color=MY_BLACK, fill_opacity=0.6, stroke_width=0).move_to(subtitle_voice.get_center()).set_z_index(subtitle_voice.z_index - 1)
            subtitle_group = VGroup(subtitle_bg, subtitle_voice)

            # Animation Sequence
            title_fade_time = 1.0
            list_write_time_per_item = (tracker.duration - title_fade_time - 1.0) / len(summary_list_group) # Distribute time
            list_write_time_per_item = max(list_write_time_per_item, 1.5) # Ensure minimum time per item

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(summary_title, run_time=title_fade_time),
                    lag_ratio=0.0
                ),
                run_time=title_fade_time
            )

            # Animate list items one by one
            for i, item in enumerate(summary_list_group):
                 # Calculate run_time for this item, ensuring total doesn't exceed available time
                 current_item_run_time = min(list_write_time_per_item, tracker.duration - self.renderer.time - 1.5) # Leave buffer
                 current_item_run_time = max(current_item_run_time, 0.1) # Minimum run time

                 # Use Write for Text parts and FadeIn for MathTex parts within the item VGroup
                 anims = []
                 for sub_part in item:
                     if isinstance(sub_part, Text):
                         anims.append(Write(sub_part))
                     else: # MathTex or other VMobject
                         anims.append(FadeIn(sub_part))

                 if anims:
                     self.play(AnimationGroup(*anims, lag_ratio=0.1), run_time=current_item_run_time)
                 else:
                     self.wait(current_item_run_time) # Wait if no anims somehow


            # Calculate remaining time
            total_anim_time = self.renderer.time # Get current time from renderer
            subtitle_fadeout_time = 1.0
            remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
            if remaining_wait > 0:
                self.wait(remaining_wait)

            self.play(FadeOut(subtitle_group), run_time=subtitle_fadeout_time)

        self.wait(1) # Final pause


# --- Main execution block ---
if __name__ == "__main__":
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 30
    config.output_file = "CombinedScene"
    # Use a relative path for portability, #(output_video) will be replaced
    config.media_dir = "./#(output_video)"
    config.disable_caching = True # Disable caching as requested

    # Set background color for the whole rendering process (optional, can be overridden by scenes)
    # config.background_color = MY_BLACK

    scene = CombinedScene()
    scene.render()
    print("Scene rendering finished.")
    print(f"Output video should be in: {os.path.abspath(config.media_dir)}")