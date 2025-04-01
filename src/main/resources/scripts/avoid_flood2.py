# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
# Note: Importing DARK_GRAY directly is often preferred if only a few specific colors are needed
# from manim.utils.color.XKCD import DARK_GRAY
# Or rely on the standard colors like DARK_GRAY if available in the version
from moviepy import AudioFileClip # Correct import for AudioFileClip
import hashlib
import manimpango # For font checking

# --- Font Checking ---
DEFAULT_FONT = "Noto Sans CJK SC" # Example CJK font
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

# --- Custom Colors ---
MY_DARK_BLUE = "#000033"
MY_LIGHT_BLUE = "#6495ED"
MY_WHITE = "#FFFFFF"
MY_LIGHT_YELLOW = "#FFFFE0"
MY_LIGHT_GRAY = "#EEEEEE"
MY_DARK_GRAY = "#333333" # Using a hex code for consistency
MY_BLUE = "#007BFF"
MY_LIGHT_BLUE_FILL = "#ADD8E6"
MY_RED = "#FF0000"
MY_ORANGE = "#FFA500"
MY_YELLOW_E = "#FFF9C4" # Light yellow for highlighting
MY_BLACK = "#000000"
MY_GRID_BLUE = "#E0F2F7"
# Define DARK_GRAY if not imported or built-in
if "DARK_GRAY" not in globals():
    DARK_GRAY = "#A9A9A9" # Standard dark gray hex

# --- TTS Setup ---
CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class CustomVoiceoverTracker:
    def __init__(self, audio_path, duration):
        self.audio_path = audio_path
        self.duration = duration

def get_cache_filename(text):
    # Use a subdirectory for cache files to keep the main directory clean
    cache_subdir = os.path.join(CACHE_DIR, "audio_files")
    os.makedirs(cache_subdir, exist_ok=True)
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(cache_subdir, f"{text_hash}.mp3")


@contextmanager
def custom_voiceover_tts(text, token="123456", base_url="https://uni-ai.fly.dev/api/manim/tts"):
    cache_file = get_cache_filename(text)

    if os.path.exists(cache_file):
        audio_file = cache_file
        print(f"Using cached TTS audio: {cache_file}") # Debugging
    else:
        input_text = requests.utils.quote(text)
        url = f"{base_url}?token={token}&input={input_text}"
        print(f"Requesting TTS from: {url}") # Debugging
        try:
            response = requests.get(url, stream=True, timeout=60) # Added timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.RequestException as e:
             # Provide more context in the error message
             raise Exception(f"TTS API request failed for URL {url}. Error: {e}")

        # Check content type before writing
        content_type = response.headers.get('Content-Type', '').lower()
        print(f"Response Content-Type: {content_type}") # Debugging
        if 'audio' not in content_type:
            # Try to read some text to see the error message from the API
            error_text = response.text[:500] # Read first 500 chars
            raise Exception(f"TTS API did not return audio. Status: {response.status_code}. URL: {url}. Response text: {error_text}")

        try:
            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"TTS audio saved to: {cache_file}") # Debugging
        except Exception as e:
            # Clean up potentially corrupted cache file
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                    print(f"Removed potentially corrupted cache file: {cache_file}")
                except OSError as oe:
                    print(f"Error removing corrupted cache file {cache_file}: {oe}")
            raise Exception(f"Failed to write TTS audio to file {cache_file}: {e}")

        audio_file = cache_file

    # Verify the audio file is valid before getting duration
    try:
        # Ensure the file has non-zero size before trying to open
        if os.path.getsize(audio_file) == 0:
            raise ValueError("Audio file is empty.")
        clip = AudioFileClip(audio_file)
        duration = clip.duration
        clip.close() # Close the clip to release the file handle
        if duration is None or duration <= 0:
             raise ValueError(f"Audio clip has invalid duration: {duration}")
        print(f"Audio duration: {duration} seconds") # Debugging
    except Exception as e:
        # If duration check fails, delete the invalid cache file
        print(f"Error processing audio file {audio_file}: {e}. Deleting cache file.")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except OSError as oe:
                print(f"Error removing invalid cache file {cache_file}: {oe}")
        # Re-raise the exception to stop the process
        raise Exception(f"Failed to process audio file {audio_file}: {e}. Cache file removed.")


    tracker = CustomVoiceoverTracker(audio_file, duration)
    try:
        yield tracker
    finally:
        # pass # Keep cache for reuse
        # Explicitly close if needed, though context manager should handle MoviePy clip closure
        pass


# -----------------------------
# CombinedScene：整合所有场景
# -----------------------------
class CombinedScene(MovingCameraScene):
    """
    合并所有场景的 Manim 动画，讲解设计洪水推求方法。
    """
    def setup(self):
        MovingCameraScene.setup(self)
        if final_font:
            Text.set_default(font=final_font)
        # else: Use Manim default font

    def construct(self):
        # --- 场景〇：开场与标题 ---
        self.play_scene_00()
        self.clear_and_reset()

        # --- 场景一：典型洪水过程线的条件 ---
        self.play_scene_01()
        self.clear_and_reset()

        # --- 场景二：设计洪水计算步骤 - 概述 ---
        self.play_scene_02()
        self.clear_and_reset()

        # --- 场景三：可视化步骤概要 - 频率计算与缩放 ---
        self.play_scene_03()
        self.clear_and_reset()

        # --- 场景四：总结与结束 ---
        self.play_scene_04()
        # No need to clear_and_reset after the last scene if the video ends there

    def get_scene_number(self, number_str):
        """创建并定位场景编号"""
        scene_num = Text(number_str, font_size=24, color=MY_WHITE)
        scene_num.to_corner(UR, buff=0.5)
        return scene_num

    def clear_and_reset(self):
        """清除当前场景所有对象并重置相机"""
        # Need to handle potential None objects if added/removed dynamically
        valid_mobjects = [m for m in self.mobjects if m is not None]
        # Clear updaters from all valid mobjects
        for mob in valid_mobjects:
             # Check if the object has updaters before trying to clear
             if hasattr(mob, 'clear_updaters') and callable(mob.clear_updaters):
                 mob.clear_updaters()

        all_mobjects_group = Group(*valid_mobjects) # Use Group for mixed types
        if all_mobjects_group: # Check if the group is not empty
            self.play(FadeOut(all_mobjects_group, shift=DOWN * 0.5), run_time=0.5)

        self.clear() # Clears mobjects list
        self.camera.frame.move_to(ORIGIN)
        # Ensure frame size is reset based on current config, not potentially stale values
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        # self.wait(0.1) # Short pause after clearing

    def create_gradient_background(self, color_a, color_b):
        """创建垂直渐变背景"""
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            # Use fill_color with a list and gradient_direction
            fill_color=[color_a, color_b],
            fill_opacity=1
        )
        # Explicitly set gradient direction if needed (Manim might default correctly)
        # bg.set_sheen_direction(DOWN) # Or UP, LEFT, RIGHT
        bg.set_z_index(-10)
        return bg

    def play_scene_00(self):
        """场景〇：开场与标题"""
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        bg0 = self.create_gradient_background(MY_DARK_BLUE, MY_LIGHT_BLUE)
        scene_num_00 = self.get_scene_number("00")
        self.add(bg0, scene_num_00)

        title = Text("设计洪水推求方法", font_size=60, color=MY_WHITE)
        title.move_to(UP * 1.5)
        subtitle = Text("典型过程线选择与计算步骤", font_size=40, color=MY_LIGHT_YELLOW)
        subtitle.next_to(title, DOWN, buff=0.5)

        voice_text_00 = "大家好！本视频将为您详解设计洪水的推求方法，重点介绍典型洪水过程线的选择条件与详细计算步骤。"

        with custom_voiceover_tts(voice_text_00) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_00, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            # Add a semi-transparent background for better readability
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_BLACK, fill_color=MY_BLACK,
                fill_opacity=0.6, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)


            # Animation sequence
            anim_duration_title = 1.5
            anim_duration_subtitle = 2.0 # FadeIn is generally faster than Write for Text
            total_anim_time = anim_duration_title + anim_duration_subtitle

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(title, shift=UP*0.2, run_time=anim_duration_title),
                    lag_ratio=0.0
                ),
                run_time=anim_duration_title
            )
            # Use FadeIn for subtitle as well, Write is for VMobjects
            self.play(FadeIn(subtitle, shift=UP*0.2, run_time=anim_duration_subtitle))

            # Wait for audio to finish, considering animation time and fade out time
            wait_time = tracker.duration - total_anim_time - 1.0 # 1.0s for fade out
            if wait_time > 0:
                self.wait(wait_time)

            self.play(FadeOut(subtitle_group), run_time=1.0)

        self.wait(1) # Pause before clearing

    def play_scene_01(self):
        """场景一：典型洪水过程线的条件 - 修正布局和动画"""
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        bg1 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_LIGHT_GRAY, fill_opacity=1, stroke_width=0).set_z_index(-10)
        scene_num_01 = self.get_scene_number("01").set_color(MY_DARK_GRAY) # Adjust color for light bg
        self.add(bg1, scene_num_01)

        question = Text("1. 由流量资料推求设计洪水选择的典型洪水过程线应具备什么条件？", font_size=36, color=MY_DARK_GRAY)
        question.to_edge(UP, buff=1.0).align_to(LEFT, LEFT).shift(RIGHT * 1.0)

        answer_title = Text("答案要点：", font_size=32, color=MY_DARK_GRAY, weight=BOLD)
        answer_title.next_to(question, DOWN, buff=0.8).align_to(question, LEFT)

        # --- Create Answer Points Graphics (Keep definitions) ---
        point_scale = 0.6 # Controls the size of the mini-graphs
        axes_config = {
            "x_range": [0, 10, 2], "y_range": [0, 8, 2],
            "x_length": 3 * point_scale, "y_length": 2 * point_scale,
            "axis_config": {"include_numbers": False, "include_tip": False, "stroke_color": MY_DARK_GRAY, "stroke_width": 2},
        }
        label_config = {"font_size": 24 * point_scale, "color": MY_DARK_GRAY}

        # Point 1: Peak High, Large Volume
        axes1 = Axes(**axes_config) # Position later
        curve1_func = lambda t: 7 * np.exp(-((t - 5)**2) / 4)
        curve1 = axes1.plot(curve1_func, x_range=[1, 9], color=MY_BLUE, stroke_width=3*point_scale)
        area1 = axes1.get_area(curve1, x_range=[1, 9], color=MY_LIGHT_BLUE_FILL, opacity=0.6)
        peak_dot1 = Dot(axes1.input_to_graph_point(5, curve1), color=MY_ORANGE, radius=0.05*point_scale)
        labels1 = VGroup(
            axes1.get_x_axis_label(MathTex("T", **label_config)),
            axes1.get_y_axis_label(MathTex("Q", **label_config)).shift(LEFT*0.3*point_scale)
        )
        graphic1 = VGroup(axes1, curve1, area1, labels1, peak_dot1)
        text1 = Text("峰高量大", font_size=28*point_scale, color=MY_DARK_GRAY)
        point1 = VGroup(graphic1, text1).arrange(DOWN, buff=0.3*point_scale)

        # Point 2: Representative
        axes2 = Axes(**axes_config) # Position later
        grey_curves = VGroup()
        params = [(4, 1.5, 0.8), (6, 2.5, 1.2), (5.5, 2, 0.6)]
        for p in params:
            c = axes2.plot(lambda t: p[2]*7 * np.exp(-((t - p[0])**2) / p[1]), x_range=[1, 9], color=DARK_GRAY, stroke_width=1.5*point_scale, stroke_opacity=0.5)
            grey_curves.add(c)
        curve2_rep = axes2.plot(lambda t: 6.5 * np.exp(-((t - 5.2)**2) / 3), x_range=[1, 9], color=MY_BLUE, stroke_width=3*point_scale)
        labels2 = VGroup(
             axes2.get_x_axis_label(MathTex("T", **label_config)),
             axes2.get_y_axis_label(MathTex("Q", **label_config)).shift(LEFT*0.3*point_scale)
        )
        graphic2 = VGroup(axes2, grey_curves, labels2) # Representative curve added later in animation
        text2 = Text("具有代表性", font_size=28*point_scale, color=MY_DARK_GRAY)
        point2 = VGroup(graphic2, text2).arrange(DOWN, buff=0.3*point_scale)

        # Point 3: Concentrated Peak Shape
        axes3 = Axes(**axes_config) # Position later
        curve3_sharp = axes3.plot(lambda t: 7 * np.exp(-((t - 5)**2) / 1.5), x_range=[1, 9], color=MY_BLUE, stroke_width=3*point_scale) # Sharp
        curve3_flat = axes3.plot(lambda t: 5 * np.exp(-((t - 5)**2) / 8), x_range=[1, 9], color=DARK_GRAY, stroke_width=2*point_scale) # Flat
        arrow3 = Arrow(axes3.c2p(4, 5), axes3.c2p(5, 7), buff=0, color=MY_ORANGE, stroke_width=3*point_scale, max_tip_length_to_length_ratio=0.2)
        labels3 = VGroup(
             axes3.get_x_axis_label(MathTex("T", **label_config)),
             axes3.get_y_axis_label(MathTex("Q", **label_config)).shift(LEFT*0.3*point_scale)
        )
        graphic3 = VGroup(axes3, curve3_sharp, curve3_flat, labels3, arrow3)
        text3 = Text("峰形集中", font_size=28*point_scale, color=MY_DARK_GRAY)
        point3 = VGroup(graphic3, text3).arrange(DOWN, buff=0.3*point_scale)

        # Point 4: Peak Late
        axes4 = Axes(**axes_config) # Position later
        curve4_func = lambda t: 7 * np.exp(-((t - 7)**2) / 3) # Peak at t=7 (late)
        curve4 = axes4.plot(curve4_func, x_range=[2, 10], color=MY_BLUE, stroke_width=3*point_scale)
        center_time = 6 # Midpoint of x_range [2, 10]
        center_line = DashedLine(axes4.c2p(center_time, 0), axes4.c2p(center_time, 8), color=MY_DARK_GRAY, stroke_width=1.5*point_scale, dash_length=0.1*point_scale)
        peak_dot4 = Dot(axes4.input_to_graph_point(7, curve4), color=MY_ORANGE, radius=0.05*point_scale)
        arrow4_start = axes4.c2p(center_time + 0.5, 4)
        arrow4_end = axes4.c2p(7 - 0.2, 6.5)
        arrow4 = Arrow(start=arrow4_start, end=arrow4_end, buff=0, color=MY_ORANGE, stroke_width=3*point_scale, max_tip_length_to_length_ratio=0.2)
        labels4 = VGroup(
             axes4.get_x_axis_label(MathTex("T", **label_config)),
             axes4.get_y_axis_label(MathTex("Q", **label_config)).shift(LEFT*0.3*point_scale)
        )
        graphic4 = VGroup(axes4, curve4, center_line, labels4, peak_dot4, arrow4)
        text4 = Text("洪峰偏后", font_size=28*point_scale, color=MY_DARK_GRAY)
        point4 = VGroup(graphic4, text4).arrange(DOWN, buff=0.3*point_scale)

        # Arrange all points with increased buffer
        answer_points = VGroup(point1, point2, point3, point4).arrange(RIGHT, buff=1.8) # Increased buff significantly
        answer_points.next_to(answer_title, DOWN, buff=0.8).scale(1.0 / point_scale) # Scale back up

        # --- Animation ---
        voice_text_01 = "那么，选择典型洪水过程线需要满足哪些条件呢？主要有四点：一，峰高量大，代表洪水强度和总体积都比较显著。二，具有代表性，能反映该流域洪水的一般特性。三，峰形集中，洪水涨落迅速。四，洪峰偏后，峰现时间相对整个过程靠后一些。"

        with custom_voiceover_tts(voice_text_01) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_01, font_size=28, color=MY_DARK_GRAY,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_WHITE, fill_color=MY_WHITE,
                fill_opacity=0.7, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)

            # Animate Question and Title
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(question, shift=DOWN*0.2, run_time=1.5),
                    lag_ratio=0.0
                ),
                run_time=1.5
            )
            self.play(FadeIn(answer_title, shift=DOWN*0.2, run_time=1.0))

            # Camera pan down to answer area - Adjust zoom/position
            # Pan down less, zoom out slightly less to give more space
            target_center = answer_points.get_center() + UP * 0.5 # Slightly higher center
            target_height = config.frame_height * 0.9 # Zoom out less
            self.play(self.camera.frame.animate.move_to(target_center).set(height=target_height), run_time=1.0)

            # Animate each point sequentially
            point_intro_time = 1.0 # Time to fade in text + create graph base
            highlight_anim_time = 0.8
            wait_between_points = 0.5
            total_points_anim_time = 0

            # Point 1 Animation
            self.play(FadeIn(text1), Create(axes1), Create(labels1), run_time=point_intro_time)
            self.play(Create(curve1), Create(area1), FadeIn(peak_dot1), run_time=0.8)
            self.play(Indicate(peak_dot1, scale_factor=1.5, color=MY_RED),
                      ShowPassingFlash(area1.copy().set_color(MY_YELLOW_E), time_width=0.5),
                      run_time=highlight_anim_time)
            self.wait(wait_between_points)
            total_points_anim_time += point_intro_time + 0.8 + highlight_anim_time + wait_between_points

            # Point 2 Animation
            self.play(FadeIn(text2), Create(axes2), Create(labels2), Create(grey_curves), run_time=point_intro_time)
            self.play(ReplacementTransform(grey_curves, curve2_rep), run_time=highlight_anim_time)
            graphic2.add(curve2_rep) # Add blue curve to the group
            self.wait(wait_between_points)
            total_points_anim_time += point_intro_time + highlight_anim_time + wait_between_points

            # Point 3 Animation
            self.play(FadeIn(text3), Create(axes3), Create(labels3), Create(curve3_sharp), Create(curve3_flat), run_time=point_intro_time)
            self.play(Create(arrow3), run_time=0.5)
            self.play(Indicate(arrow3, color=MY_RED), Indicate(curve3_sharp, color=MY_ORANGE), run_time=highlight_anim_time - 0.2)
            self.wait(wait_between_points)
            total_points_anim_time += point_intro_time + 0.5 + (highlight_anim_time - 0.2) + wait_between_points

            # Point 4 Animation
            self.play(FadeIn(text4), Create(axes4), Create(labels4), Create(curve4), Create(center_line), FadeIn(peak_dot4), run_time=point_intro_time)
            self.play(Create(arrow4), run_time=0.5)
            self.play(Indicate(peak_dot4, scale_factor=1.5, color=MY_RED), Indicate(arrow4, color=MY_RED), run_time=highlight_anim_time - 0.2)
            self.wait(wait_between_points)
            total_points_anim_time += point_intro_time + 0.5 + (highlight_anim_time - 0.2) + wait_between_points


            # Wait for audio, considering animation time and fade out
            anim_q_title = 1.5 + 1.0
            anim_cam_pan = 1.0
            total_anim_time = anim_q_title + anim_cam_pan + total_points_anim_time

            wait_time = tracker.duration - total_anim_time - 1.0 # 1.0s for fade out
            if wait_time > 0:
                self.wait(wait_time)

            self.play(FadeOut(subtitle_group), run_time=1.0)

        # Reset camera before clearing
        self.play(self.camera.frame.animate.move_to(ORIGIN).set(width=config.frame_width, height=config.frame_height), run_time=0.5)
        self.wait(0.5) # Pause before clearing

    def play_scene_02(self):
        """场景二：设计洪水计算步骤 - 概述 - 修正布局和高亮"""
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        bg2 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_LIGHT_GRAY, fill_opacity=1, stroke_width=0).set_z_index(-10)
        scene_num_02 = self.get_scene_number("02").set_color(MY_DARK_GRAY)
        self.add(bg2, scene_num_02)

        question = Text("2. 试述由流量资料推求设计洪水计算步骤。", font_size=36, color=MY_DARK_GRAY)
        question.to_edge(UP, buff=1.0).align_to(LEFT, LEFT).shift(RIGHT * 1.0)

        steps_title = Text("计算步骤要点：", font_size=32, color=MY_DARK_GRAY, weight=BOLD)
        steps_title.next_to(question, DOWN, buff=0.8).align_to(question, LEFT)

        # --- Manually Create Numbered List ---
        steps_text = [
            "按年最大值法选样",
            "资料可靠性、一致性、代表性审查",
            "特大洪水频率处理",
            "峰、量频率计算",
            "分析计算安全修正值",
            "查算设计洪峰和设计洪量",
            "频率计算成果合理性检验",
            "选择典型洪水",
            "同倍比或同频率缩放得出设计洪水过程线"
        ]
        steps_list_group = VGroup()
        item_font_size = 28
        num_color = MY_BLUE
        text_color = MY_DARK_GRAY
        line_buff = 0.6 # Increased line spacing significantly
        num_text_buff = 0.2 # Space between number and text

        for i, item_text in enumerate(steps_text):
            max_text_width = config.frame_width - 3
            num = Text(f"{i+1}.", font_size=item_font_size, color=num_color, weight=BOLD)
            text = Text(item_text, font_size=item_font_size, color=text_color, width=max_text_width)
            # Align number's top to text's top
            line = VGroup(num, text).arrange(RIGHT, buff=num_text_buff, aligned_edge=UP)
            steps_list_group.add(line)

        # Arrange list items vertically, left-aligned with increased buffer
        steps_list_group.arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
        steps_list_group.next_to(steps_title, DOWN, buff=0.5).align_to(steps_title, LEFT)

        # --- Animation ---
        voice_text_02 = "接下来，我们概述一下由流量资料推求设计洪水的计算步骤。这通常包括：一，按年最大值法选样；二，审查资料的可靠性、一致性和代表性；三，处理特大洪水的频率；四，进行洪峰和洪量的频率计算；五，分析计算安全修正值；六，查算得到设计洪峰和设计洪量；七，检验频率计算成果的合理性；八，选择典型的洪水过程线；最后一步，九，通过同倍比或同频率缩放，得到最终的设计洪水过程线。"

        with custom_voiceover_tts(voice_text_02) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_02, font_size=28, color=MY_DARK_GRAY,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_WHITE, fill_color=MY_WHITE,
                fill_opacity=0.7, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)

            # Animate Question and Title
            self.play(
                 AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(question, shift=DOWN*0.2, run_time=1.5),
                    lag_ratio=0.0
                 ),
                 run_time=1.5
            )
            self.play(FadeIn(steps_title, shift=DOWN*0.2, run_time=1.0))

            # Camera pan down slightly to fit list
            list_bottom_y = steps_list_group.get_bottom()[1]
            target_center_y = (steps_title.get_top()[1] + list_bottom_y) / 2
            required_height = (steps_title.get_top()[1] - list_bottom_y) + 2 * 1.0 # Add buffer
            target_height = max(required_height, config.frame_height * 0.8) # Adjust zoom if needed

            self.play(self.camera.frame.animate.move_to(np.array([0, target_center_y, 0])).set(height=target_height), run_time=0.8)


            # Animate list items sequentially
            item_anims = []
            total_items = len(steps_list_group)
            estimated_item_reveal_time = max(5.0, tracker.duration - 6.0)
            per_item_delay = estimated_item_reveal_time / total_items
            per_item_runtime = min(0.5, per_item_delay * 0.8)

            current_anim_time = 0
            for item in steps_list_group:
                # Highlight effect - Using Succession of Create and FadeOut
                highlight_rect = SurroundingRectangle(
                    item, buff=0.05, color=MY_ORANGE,
                    fill_color=MY_YELLOW_E, fill_opacity=0.5,
                    stroke_width=1, stroke_color=MY_ORANGE
                ).set_z_index(item.z_index - 1)

                highlight_duration = per_item_delay * 0.6
                create_time = highlight_duration * 0.4
                fade_time = highlight_duration * 0.6

                highlight_anim = Succession(
                    Create(highlight_rect, run_time=create_time),
                    FadeOut(highlight_rect, run_time=fade_time)
                )

                item_anims.append(
                    AnimationGroup(
                        FadeIn(item, shift=UP*0.1, run_time=per_item_runtime),
                        Succession( # Start highlight slightly after text appears
                            Wait(per_item_runtime * 0.2),
                            highlight_anim
                        ),
                        lag_ratio=0
                    )
                )
                current_anim_time += per_item_delay

            # Play animations with calculated lag
            # Adjust lag_ratio based on the total duration of the inner AnimationGroup
            inner_anim_duration = per_item_runtime + per_item_runtime * 0.2 + highlight_duration
            self.play(LaggedStart(*item_anims, lag_ratio=per_item_delay / inner_anim_duration),
                      run_time=current_anim_time)


            # Wait for audio
            total_anim_time = 1.5 + 1.0 + 0.8 + current_anim_time
            wait_time = tracker.duration - total_anim_time - 1.0 # 1.0s for fade out
            if wait_time > 0:
                self.wait(wait_time)

            self.play(FadeOut(subtitle_group), run_time=1.0)

        # Reset camera before clearing
        self.play(self.camera.frame.animate.move_to(ORIGIN).set(width=config.frame_width, height=config.frame_height), run_time=0.5)
        self.wait(1.0) # Pause before clearing

    def play_scene_03(self):
        """场景三：可视化步骤概要 - 频率计算与缩放"""
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        bg3 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_GRID_BLUE, fill_opacity=1, stroke_width=0).set_z_index(-10)
        scene_num_03 = self.get_scene_number("03").set_color(MY_DARK_GRAY)
        self.add(bg3, scene_num_03)

        # --- Left Side: Frequency Calculation ---
        left_center = LEFT * (config.frame_width / 4) + UP * 0.5
        axes_freq = Axes(
            x_range=[0, 10, 2], y_range=[0, 1, 0.2], # Q/W vs P
            x_length=5, y_length=3,
            axis_config={"include_numbers": True, "stroke_color": MY_DARK_GRAY, "stroke_width": 2},
            # Corrected y_axis_config with correct key 'num_decimal_places'
            y_axis_config={
                "decimal_number_config": {
                    "num_decimal_places": 1
                }
            },
        ).move_to(left_center)

        # Simplified P-III like curve (decreasing)
        freq_curve_func = lambda x: np.exp(-0.5 * x) * 0.9 + 0.05 if x > 0 else 1.0 # Avoid log(0) or div by zero if x can be 0
        freq_curve = axes_freq.plot(freq_curve_func, x_range=[0.5, 9], color=MY_BLUE, stroke_width=3)

        # Design point (e.g., P=1% or 0.01, find corresponding Q)
        # For this fake curve, let's pick a point visually, say P=0.1
        design_p = 0.1
        # Find x for P=0.1 => 0.1 = exp(-0.5*x)*0.9 + 0.05 => 0.05 = exp(-0.5*x)*0.9 => 0.05/0.9 = exp(-0.5*x)
        # ln(0.05/0.9) = -0.5*x => x = -2 * ln(0.05/0.9) approx 5.78
        design_q = -2 * np.log(0.05 / 0.9) # Calculate Q for P=0.1
        design_point_coord = axes_freq.c2p(design_q, design_p)
        design_dot = Dot(design_point_coord, color=MY_RED, radius=0.08)

        # Lines to axes - Manually create DashedLine
        point_on_x = axes_freq.c2p(design_q, 0)
        point_on_y = axes_freq.c2p(0, design_p)
        v_line = DashedLine(point_on_x, design_point_coord, dash_length=0.1, color=MY_DARK_GRAY)
        h_line = DashedLine(point_on_y, design_point_coord, dash_length=0.1, color=MY_DARK_GRAY)
        dashed_lines = VGroup(v_line, h_line)


        # Labels
        q_label = axes_freq.get_x_axis_label(MathTex("Q \\text{ or } W", font_size=28, color=MY_DARK_GRAY), edge=DOWN, direction=DOWN)
        p_label = axes_freq.get_y_axis_label(MathTex("P", font_size=28, color=MY_DARK_GRAY), edge=LEFT, direction=LEFT)
        # Use f-string for dynamic label value
        design_q_label_tex = f"Q_p \\approx {design_q:.1f}"
        design_q_label = MathTex(design_q_label_tex, font_size=32, color=MY_RED).next_to(point_on_x, DOWN, buff=0.2)
        design_p_label_tex = f"P = {design_p:.1f}" # Example: P=0.1
        design_p_label = MathTex(design_p_label_tex, font_size=32, color=MY_RED).next_to(point_on_y, LEFT, buff=0.2)

        freq_title = Text("步骤 4 & 6：频率计算确定设计值", font_size=28, color=MY_DARK_GRAY)
        freq_title.next_to(axes_freq, UP, buff=0.5)

        left_group = VGroup(axes_freq, freq_curve, design_dot, dashed_lines, q_label, p_label, design_q_label, design_p_label, freq_title)

        # --- Right Side: Typical Selection & Scaling ---
        right_center = RIGHT * (config.frame_width / 4) + UP * 0.5
        # Adjust y_range dynamically based on calculated Qp
        y_max_right = np.ceil(design_q) + 1
        axes_scale = Axes(
            x_range=[0, 10, 2], y_range=[0, y_max_right, 2], # T vs Q, adjusted y_range
            x_length=5, y_length=3,
            axis_config={"include_numbers": False, "include_tip": False, "stroke_color": MY_DARK_GRAY, "stroke_width": 2},
             # No specific axis configs needed here if axis_config covers it
        ).move_to(right_center)

        # Typical hydrograph (blue)
        typical_func = lambda t: 5 * np.exp(-((t - 5)**2) / 4) # Lower peak than Qp
        typical_curve = axes_scale.plot(typical_func, x_range=[1, 9], color=MY_BLUE, stroke_width=3)
        typical_peak_t = 5 # t-value where the peak occurs
        typical_peak_y = typical_func(typical_peak_t) # Peak is at t=5, value is 5

        # Design peak flow level (Qp) - use value from left side
        design_qp_value = design_q # Use the calculated Qp

        design_qp_line = DashedLine(
            axes_scale.c2p(0, design_qp_value),
            axes_scale.c2p(10, design_qp_value),
            color=MY_RED, stroke_width=2, dash_length=0.15
        )
        design_qp_label_tex = f"Q_p \\approx {design_qp_value:.1f}"
        design_qp_label = MathTex(design_qp_label_tex, font_size=32, color=MY_RED).next_to(design_qp_line.get_right(), RIGHT, buff=0.2)

        # Scaling factor
        scale_factor = design_qp_value / typical_peak_y if typical_peak_y != 0 else 1 # Avoid division by zero

        # Scaled hydrograph (red/orange) - create target shape for Transform
        scaled_func = lambda t: scale_factor * typical_func(t) # Define the scaled function
        scaled_curve_target_shape = axes_scale.plot(scaled_func, x_range=[1, 9], color=MY_ORANGE, stroke_width=3)


        # Labels
        t_label_scale = axes_scale.get_x_axis_label(MathTex("T", font_size=28, color=MY_DARK_GRAY), edge=DOWN, direction=DOWN)
        q_label_scale = axes_scale.get_y_axis_label(MathTex("Q", font_size=28, color=MY_DARK_GRAY), edge=LEFT, direction=LEFT)
        typical_label = Text("典型过程线 (未缩放)", font_size=24, color=MY_BLUE).next_to(typical_curve, UP, buff=0.1, aligned_edge=LEFT).shift(RIGHT*0.5)

        # Create the scaled label BUT DON'T position it yet
        scaled_label = Text("设计洪水过程线", font_size=24, color=MY_ORANGE)

        scale_title = Text("步骤 8 & 9：选择典型并缩放至设计值", font_size=28, color=MY_DARK_GRAY)
        scale_title.next_to(axes_scale, UP, buff=0.5)

        right_group = VGroup(axes_scale, typical_curve, design_qp_line, design_qp_label, t_label_scale, q_label_scale, typical_label, scale_title)
        # scaled_label added during animation

        # --- Animation ---
        voice_text_03 = "我们来可视化关键的两个步骤。首先，通过频率分析（如P-III型曲线），根据设计频率（例如P等于0.1），确定对应的设计洪峰流量Qp和设计洪量W。然后，选择一条具有代表性的典型洪水过程线。最后，采用同倍比放大法，将典型过程线的洪峰值放大到我们计算得到的设计洪峰Qp，从而得到最终的设计洪水过程线。"

        with custom_voiceover_tts(voice_text_03) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_03, font_size=28, color=MY_DARK_GRAY,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_WHITE, fill_color=MY_WHITE,
                fill_opacity=0.7, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)

            # Animate subtitle and left side (Frequency)
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(freq_title, run_time=1.0),
                    Create(axes_freq, run_time=1.5),
                    Create(freq_curve, run_time=1.5),
                    FadeIn(q_label), FadeIn(p_label),
                    lag_ratio=0.1
                ),
                run_time=2.5
            )
            self.play(
                Create(dashed_lines),
                FadeIn(design_dot),
                Write(design_q_label),
                Write(design_p_label),
                run_time=1.5
            )
            self.wait(1.0) # Pause on frequency part

            # Camera pan to right side (Scaling)
            # Pan smoothly, maybe slight zoom out to ensure fit
            target_center = right_center + DOWN * 0.5 # Adjust center slightly
            target_height = config.frame_height * 0.9
            self.play(self.camera.frame.animate.move_to(target_center).set(height=target_height), run_time=1.0)


            # Animate right side
            self.play(
                FadeIn(scale_title, run_time=1.0),
                Create(axes_scale, run_time=1.5),
                Create(typical_curve, run_time=1.5),
                FadeIn(typical_label),
                FadeIn(t_label_scale), FadeIn(q_label_scale),
                lag_ratio=0.1,
                run_time=2.0
            )
            self.play(
                Create(design_qp_line),
                Write(design_qp_label),
                run_time=1.0
            )

            # Scaling animation using Transform
            # Calculate peak coordinates of the *final* scaled curve
            scaled_peak_t = typical_peak_t # Peak t-value remains the same
            scaled_peak_y = scaled_func(scaled_peak_t)
            scaled_peak_screen_coord = axes_scale.c2p(scaled_peak_t, scaled_peak_y)

            # Position the label relative to the calculated screen coordinate
            scaled_label.next_to(scaled_peak_screen_coord, DOWN, buff=0.2)

            self.play(
                Transform(typical_curve, scaled_curve_target_shape), # Transform original curve into target shape
                FadeIn(scaled_label), # Fade in the correctly positioned label
                run_time=2.0
            )
            # Add the final objects to the group for cleanup
            # The transformed object replaces the original in the scene's mobjects list automatically
            # We need to update our right_group manually if we want to fade it out later
            right_group.remove(typical_curve) # Remove original from group
            # Use the variable holding the transformed curve
            right_group.add(scaled_curve_target_shape, scaled_label)


            # Wait for audio
            # Recalculate timings
            anim_left = 2.5 + 1.5 + 1.0
            anim_pan = 1.0
            anim_right_setup = 2.0 + 1.0
            anim_scale = 2.0
            total_anim_time = anim_left + anim_pan + anim_right_setup + anim_scale

            wait_time = tracker.duration - total_anim_time - 1.0 # 1.0s for fade out
            if wait_time > 0:
                self.wait(wait_time)

            self.play(FadeOut(subtitle_group), run_time=1.0)

        # Reset camera before clearing
        self.play(self.camera.frame.animate.move_to(ORIGIN).set(width=config.frame_width, height=config.frame_height), run_time=0.5)
        self.wait(1.0) # Pause before clearing


    def play_scene_04(self):
        """场景四：总结与结束"""
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        bg4 = self.create_gradient_background(MY_DARK_BLUE, MY_LIGHT_BLUE)
        scene_num_04 = self.get_scene_number("04")
        self.add(bg4, scene_num_04)

        summary_title = Text("总结回顾", font_size=48, color=MY_WHITE, weight=BOLD)
        summary_title.move_to(UP * 2.5)

        point1_text = "典型洪水选择标准：峰高量大、代表性、峰形集中、洪峰偏后。"
        point2_text = "设计洪水计算流程：数据准备 → 频率分析 → 典型选择 → 过程线缩放。"
        end_text = "感谢观看！"

        point1 = Text(point1_text, font_size=32, color=MY_LIGHT_YELLOW, width=config.frame_width - 4) # Allow wrapping
        point1.next_to(summary_title, DOWN, buff=0.8)

        point2 = Text(point2_text, font_size=32, color=MY_LIGHT_YELLOW, width=config.frame_width - 4) # Allow wrapping
        point2.next_to(point1, DOWN, buff=0.5)

        ending = Text(end_text, font_size=36, color=MY_WHITE)
        ending.to_edge(DOWN, buff=1.0)

        # --- Animation ---
        voice_text_04 = "总结一下，选择典型洪水过程线需关注峰高量大、代表性、峰形集中和洪峰偏后四个条件。设计洪水的计算流程则主要包括数据准备、频率分析、典型选择和过程线缩放这几个关键环节。感谢您的观看！"

        with custom_voiceover_tts(voice_text_04) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_04, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_BLACK, fill_color=MY_BLACK,
                fill_opacity=0.6, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)


            # Animate title and points
            anim_title_dur = 1.0
            anim_p1_dur = 2.5 # Using FadeIn
            anim_p2_dur = 2.5
            anim_end_dur = 1.0
            # Calculate when ending text should appear based on voice
            time_before_ending_text = tracker.duration - anim_end_dur - 1.5 # Time before "感谢观看" starts in voice, plus buffer

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(summary_title, shift=UP*0.2, run_time=anim_title_dur),
                    lag_ratio=0.0
                ),
                run_time=anim_title_dur
            )
            self.play(FadeIn(point1, shift=UP*0.1, run_time=anim_p1_dur))
            self.play(FadeIn(point2, shift=UP*0.1, run_time=anim_p2_dur))

            # Wait until it's time for the ending text based on voiceover
            current_anim_time = anim_title_dur + anim_p1_dur + anim_p2_dur
            wait_before_ending = time_before_ending_text - current_anim_time
            if wait_before_ending > 0:
                self.wait(wait_before_ending)

            # Animate ending text and fade out subtitle simultaneously
            self.play(
                FadeIn(ending, run_time=anim_end_dur),
                FadeOut(subtitle_group, run_time=1.0) # Fade out subtitle
            )

            # Wait for any remaining audio duration
            wait_after_ending = tracker.duration - (current_anim_time + max(0, wait_before_ending) + anim_end_dur)
            if wait_after_ending > 0:
                 self.wait(wait_after_ending)


        # Final fade out or zoom out
        self.wait(1.5)
        # Use self.mobjects directly as Group might cause issues if scene state changed unexpectedly
        final_elements_to_fade = Group(*[m for m in self.mobjects if m is not None])
        if final_elements_to_fade: # Check if there's anything to fade
             self.play(FadeOut(final_elements_to_fade), run_time=1.5)
        self.wait(0.5)


# --- Main execution block ---
if __name__ == "__main__":
    # Basic configuration
    config.pixel_height = 1080  # Set resolution height
    config.pixel_width = 1920   # Set resolution width
    config.frame_rate = 30      # Set frame rate
    config.output_file = "CombinedScene"  # Specify output filename
    config.disable_caching = True # Disable caching

    # Set output directory (using placeholder)
    config.media_dir = "./#(output_video)" # Java will replace #(output_video)

    # Ensure the directory exists (Manim might do this, but good practice)
    # The placeholder part will be handled by the calling Java program
    # os.makedirs("./output_video_placeholder", exist_ok=True) # Example if running directly

    print(f"Starting Manim rendering...")
    print(f"Output directory set to: {config.media_dir}")
    print(f"Output file name: {config.output_file}.mp4")
    if final_font:
         print(f"Using font: {final_font}")
    else:
         print(f"Using Manim default font.")

    scene = CombinedScene()
    scene.render()
    print("Scene rendering finished.")
    # The actual path depends on where the Java program replaces the placeholder
    print(f"Video likely saved in a subdirectory within: {config.media_dir}")