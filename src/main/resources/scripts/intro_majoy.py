# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
from moviepy import AudioFileClip # Correct import for AudioFileClip
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
MY_BLUE_D = BLUE_D # Manim's Blue D
MY_TEAL_E = TEAL_E # Manim's Teal E
MY_GRAY_B = GRAY_B # Manim's Gray B
MY_BLUE_C = BLUE_C # Manim's Blue C
MY_BLUE_A = BLUE_A # Manim's Blue A
MY_BEIGE = "#F5F5DC" # 米色

# 检查并创建 TTS 缓存目录
CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class CustomVoiceoverTracker:
    """Tracks the audio file path and duration for voiceover."""
    def __init__(self, audio_path, duration):
        self.audio_path = audio_path
        self.duration = duration

def get_cache_filename(text):
    """Generates a unique filename based on the hash of the text."""
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}.mp3")

@contextmanager
def custom_voiceover_tts(text, token="123456", base_url="https://uni-ai.fly.dev/api/manim/tts"):
    """
    Context manager for handling TTS requests, caching, and providing audio info.
    Uses a simple token for authorization (replace with actual secure method if needed).
    """
    cache_file = get_cache_filename(text)

    if os.path.exists(cache_file):
        audio_file = cache_file
        # print(f"Using cached TTS audio: {cache_file}")
    else:
        # print(f"Requesting TTS for: {text[:50]}...")
        try:
            input_text = requests.utils.quote(text)
            url = f"{base_url}?token={token}&input={input_text}"

            response = requests.get(url, stream=True, timeout=60) # Added timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            audio_file = cache_file
            # print(f"TTS audio saved to: {cache_file}")

        except requests.exceptions.RequestException as e:
            print(f"TTS API request failed: {e}")
            # Fallback: create a dummy tracker with 0 duration? Or raise exception?
            # For now, let's raise an exception to halt execution if TTS fails
            raise Exception(f"TTS API Error: {e}") from e
        except Exception as e:
            print(f"An error occurred during TTS processing: {e}")
            raise # Re-raise other exceptions

    # Get duration using moviepy
    try:
        with AudioFileClip(audio_file) as clip:
             duration = clip.duration
    except Exception as e:
        print(f"Error reading audio file duration ({audio_file}): {e}")
        # Fallback or error handling: maybe delete corrupted cache file?
        if os.path.exists(cache_file):
            os.remove(cache_file)
        raise Exception(f"Failed to get audio duration: {e}") from e

    tracker = CustomVoiceoverTracker(audio_file, duration)
    try:
        yield tracker
    finally:
        # Optional: Clean up resources if needed, though cache is usually kept
        pass

# -----------------------------
# CombinedScene：整合所有场景并添加字幕和音频
# -----------------------------
class CombinedScene(MovingCameraScene):
    """
    Manim scene combining multiple sub-scenes to present information
    about Chongqing Jiaotong University's majors, with voiceover and subtitles.
    """
    def construct(self):
        # --- 场景〇：开场标题 ---
        self.play_scene_00()
        self.clear_and_reset()

        # --- 场景一：港口航道与海岸工程 - 关键年份 ---
        self.play_scene_01()
        self.clear_and_reset()

        # --- 场景二：港口航道与海岸工程 - 学分要求 ---
        self.play_scene_02()
        self.clear_and_reset()

        # --- 场景三：港口航道与海岸工程 - 专业核心课程 ---
        self.play_scene_03()
        self.clear_and_reset()

        # --- 场景四：港口航道与海岸工程 - 特定课程信息 ---
        self.play_scene_04()
        self.clear_and_reset()

        # --- 场景五：水利水电工程 - 关键年份与荣誉 ---
        self.play_scene_05()
        self.clear_and_reset()

        # --- 场景六：水利水电工程 - 学分构成 ---
        self.play_scene_06()
        self.clear_and_reset()

        # --- 场景七：水利水电工程 - 专业核心课程 ---
        self.play_scene_07()
        self.clear_and_reset()

        # --- 场景八：自主发展计划 - 美育 ---
        self.play_scene_08()
        self.clear_and_reset()

        # --- 场景九：结束画面 ---
        self.play_scene_09()
        self.clear_and_reset()

        self.wait(1) # Final wait before ending

    def get_scene_number(self, number_str):
        """Creates and positions the scene number label."""
        scene_num = Text(number_str, font_size=24, color=MY_WHITE, font="思源黑体 CN")
        scene_num.to_corner(UR, buff=0.5)
        scene_num.set_z_index(10) # Ensure it's above the background
        return scene_num

    def create_background(self, color=MY_BLACK, opacity=1.0, gradient_colors=None, gradient_direction=None):
        """Creates a background rectangle."""
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_opacity=opacity
        )
        if gradient_colors:
            bg.set_fill(color=gradient_colors, opacity=opacity)
            # Default gradient direction if not specified (e.g., top-left to bottom-right)
            if gradient_direction is None:
                 gradient_direction = np.array([1, -1, 0]) # Example: diagonal
            # Manim's gradient handling might be direct in fill_color or need shaders
            # For simple linear gradients, providing a list of colors to fill_color often works.
            # Let's assume fill_color=[color1, color2] works for basic linear gradients.
            # If more complex gradients are needed, explore shader options.
            # Note: Manim CE v0.19 might handle gradients differently. Testing needed.
            # Using fill_color list is a common approach.
        else:
            bg.set_fill(color=color, opacity=opacity)

        bg.set_z_index(-10) # Ensure background is behind everything
        return bg

    def clear_and_reset(self):
        """Clears all mobjects from the scene and resets the camera."""
        # Gather all mobjects, filtering out None if any somehow exist
        valid_mobjects = [m for m in self.mobjects if m is not None]

        # Clear updaters from all mobjects before fading out
        for mob in valid_mobjects:
             # Check if the mobject has the clear_updaters method
             if hasattr(mob, 'clear_updaters') and callable(mob.clear_updaters):
                 mob.clear_updaters()

        # Create a group of valid mobjects to fade out
        if valid_mobjects:
            all_mobjects_group = Group(*valid_mobjects)
            self.play(FadeOut(all_mobjects_group, shift=DOWN * 0.5), run_time=0.5)

        # Use self.clear() which is the standard way to remove mobjects
        self.clear()

        # Reset camera position and zoom
        self.camera.frame.move_to(ORIGIN)
        # Use config attributes for frame dimensions
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        # self.wait(0.2) # Short pause after reset

    def play_scene_00(self):
        """Scene 0: Opening Title"""
        # Background: Blue-Green Gradient
        bg0 = self.create_background(gradient_colors=[MY_BLUE_D, MY_TEAL_E], gradient_direction=np.array([1, -1, 0])) # Top-left to bottom-right
        self.add(bg0)

        # Main Title
        title = Text("重庆交通大学 专业信息速览", font_size=60, color=MY_WHITE, font="思源黑体 CN Bold")
        title.move_to(UP * 1.0)

        # Subtitle
        subtitle = Text("港口航道与海岸工程 & 水利水电工程", font_size=40, color=MY_LIGHT_GRAY, font="思源黑体 CN")
        subtitle.next_to(title, DOWN, buff=0.5)

        # Voiceover and Animation Synchronization
        voice_text_scene_00 = "欢迎观看重庆交通大学专业信息速览。本期我们将聚焦港口航道与海岸工程以及水利水电工程这两个特色专业。"
        with custom_voiceover_tts(voice_text_scene_00) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_00,
                font_size=32,
                color=MY_WHITE,
                width=config.frame_width - 2,
                should_center=True,
                font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            # Animate title and subtitle while voiceover plays
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=2.0),
                    lag_ratio=0.0 # Start simultaneously
                ),
                run_time=2.0 # Duration of the longest animation (Write title)
            )
            self.play(FadeIn(subtitle, shift=DOWN * 0.5, run_time=1.5))

            # Wait for the remaining voiceover duration
            elapsed_time = 2.0 + 1.5 # Time spent on title and subtitle animations
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time for subtitle
            if remaining_time > 0:
                self.wait(remaining_time)

            # Fade out the voiceover subtitle
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1) # Pause before clearing

    def play_scene_01(self):
        """Scene 1: Port & Waterway Eng. - Key Years"""
        bg1 = self.create_background(color=MY_GRAY_B)
        self.add(bg1)
        scene_num_01 = self.get_scene_number("01")
        self.add(scene_num_01)

        # Title
        title = Text("港口航道与海岸工程", font_size=48, color=MY_WHITE, font="思源黑体 CN Bold")
        title.to_edge(UP, buff=1.0)

        # Left Content (2009)
        year_left = Text("2009年", font_size=36, color=MY_GOLD, weight=BOLD, font="思源黑体 CN")
        event_left = Text("评为国家级特色专业", font_size=32, color=MY_WHITE, font="思源黑体 CN")
        content_left = VGroup(year_left, event_left).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        content_left.next_to(title, DOWN, buff=1.0).shift(LEFT * 3.5)

        # Right Content (2017)
        year_right = Text("2017年", font_size=36, color=MY_GOLD, weight=BOLD, font="思源黑体 CN")
        event_right = Text("通过全国工程教育专业认证复评", font_size=32, color=MY_WHITE, font="思源黑体 CN")
        content_right = VGroup(year_right, event_right).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        content_right.next_to(title, DOWN, buff=1.0).shift(RIGHT * 3.5)

        # Voiceover and Animation
        voice_text_scene_01 = "首先来看港口航道与海岸工程。2009年，该专业被评为国家级特色专业。到了2017年，它成功通过了全国工程教育专业认证的复评。"
        with custom_voiceover_tts(voice_text_scene_01) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_01, font_size=32, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5),
                    lag_ratio=0.0
                ),
                run_time=1.5
            )

            # Animate content groups
            self.play(FadeIn(content_left, shift=LEFT * 2), run_time=1.0)
            self.wait(0.5) # Slight delay before the next item
            self.play(FadeIn(content_right, shift=RIGHT * 2), run_time=1.0)

            # Wait for remaining audio
            elapsed_time = 1.5 + 1.0 + 0.5 + 1.0 # Title + left + wait + right
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_02(self):
        """Scene 2: Port & Waterway Eng. - Credit Requirement"""
        bg2 = self.create_background(color=MY_GRAY_B)
        self.add(bg2)
        scene_num_02 = self.get_scene_number("02")
        self.add(scene_num_02)

        # Question Text
        question = Text("最低毕业学分要求？ 🤔", font_size=48, color=MY_BLUE_C, font="思源黑体 CN")
        question.move_to(UP * 0.5)

        # Answer Text
        answer = Text("180 学分", font_size=72, color=MY_WHITE, weight=BOLD, font="思源黑体 CN")
        answer.next_to(question, DOWN, buff=0.8)

        # Voiceover and Animation
        voice_text_scene_02 = "那么，港口航道与海岸工程专业的最低毕业学分要求是多少呢？答案是 180 学分。"
        with custom_voiceover_tts(voice_text_scene_02) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_02, font_size=32, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(question, run_time=1.5), # Increased run_time for Write
                    lag_ratio=0.0
                ),
                run_time=1.5
            )
            self.play(GrowFromCenter(answer), run_time=1.0)

            # Wait for remaining audio
            elapsed_time = 1.5 + 1.0 # Question + Answer
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_03(self):
        """Scene 3: Port & Waterway Eng. - Core Courses"""
        bg3 = self.create_background(color=MY_GRAY_B)
        self.add(bg3)
        scene_num_03 = self.get_scene_number("03")
        self.add(scene_num_03)

        # Title
        title = Text("专业核心课程 📚", font_size=48, color=MY_WHITE, font="思源黑体 CN Bold")
        title.to_edge(UP, buff=1.0)

        # Bulleted List
        courses = [
            "渠化工程",
            "港口规划与布置",
            "航道整治",
            "工程项目管理",
            "港口与海岸水工建筑物"
        ]
        course_list = BulletedList(
            *courses,
            dot_color=MY_WHITE,
            buff=0.4,
            font_size=36,
            font="思源黑体 CN"
        )
        course_list.set_color(MY_WHITE)
        course_list.next_to(title, DOWN, buff=0.8).align_to(title, LEFT).shift(RIGHT*1) # Align left

        # Voiceover and Animation
        voice_text_scene_03 = "该专业的核心课程包括：渠化工程、港口规划与布置、航道整治、工程项目管理，以及港口与海岸水工建筑物。"
        with custom_voiceover_tts(voice_text_scene_03) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_03, font_size=32, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.0),
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # Animate list items
            # Calculate run_time per item to fit within audio duration minus title/fadeout
            total_list_anim_time = max(0.5, tracker.duration - 1.0 - 1.0 - 0.5) # Ensure at least 0.5s, subtract title, fadeout, buffer
            run_time_per_item = total_list_anim_time / len(courses)

            self.play(
                AnimationGroup(
                    *[FadeIn(item, shift=UP * 0.2) for item in course_list],
                    lag_ratio=0.6 # Adjust lag for better pacing
                ),
                run_time=total_list_anim_time # Total time for list animation
            )

            # Wait if animation finished before audio
            elapsed_time = 1.0 + total_list_anim_time
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_04(self):
        """Scene 4: Port & Waterway Eng. - Specific Course Info"""
        bg4 = self.create_background(color=MY_GRAY_B)
        self.add(bg4)
        scene_num_04 = self.get_scene_number("04")
        self.add(scene_num_04)

        # Upper Content
        course_name_upper = Text("水工钢筋混凝土结构综合实践", font_size=36, color=MY_WHITE, font="思源黑体 CN")
        course_term = Text("第 5 学期 开设", font_size=40, color=MY_GOLD, weight=BOLD, font="思源黑体 CN")
        content_upper = VGroup(course_name_upper, course_term).arrange(DOWN, buff=0.3)
        content_upper.move_to(UP * 1.5)

        # Lower Content
        course_name_lower = Text("数学建模课程代码", font_size=36, color=MY_WHITE, font="思源黑体 CN")
        course_code = Text("19210919", font_size=48, color=MY_GOLD, weight=BOLD, font="思源黑体 CN")
        content_lower = VGroup(course_name_lower, course_code).arrange(DOWN, buff=0.3)
        content_lower.move_to(DOWN * 1.5)

        # Voiceover and Animation
        voice_text_scene_04 = "具体来看，“水工钢筋混凝土结构综合实践”这门课在第 5 学期开设。而“数学建模”课程的代码是 19210919。" # Shortened for clarity
        with custom_voiceover_tts(voice_text_scene_04) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_04, font_size=32, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            self.play(FadeIn(subtitle_voice, run_time=0.5))

            # Animate content groups sequentially
            self.play(FadeIn(content_upper), run_time=1.0)
            self.wait(0.5) # Pause between items
            self.play(FadeIn(content_lower), run_time=1.0)

            # Wait for remaining audio
            elapsed_time = 0.5 + 1.0 + 0.5 + 1.0 # Subtitle + upper + wait + lower
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_05(self):
        """Scene 5: Hydraulic & Hydroelectric Eng. - Key Year & Honors"""
        # Background: Light blue, maybe add subtle texture later if needed
        bg5 = self.create_background(color=MY_BLUE_A, opacity=0.8) # Slightly transparent blue
        self.add(bg5)
        scene_num_05 = self.get_scene_number("05")
        self.add(scene_num_05)

        # Title
        title = Text("水利水电工程 🌊", font_size=48, color=MY_WHITE, font="思源黑体 CN Bold")
        title.to_edge(UP, buff=1.0)

        # Year Identifier
        year = Text("2013年", font_size=40, color=MY_GOLD, weight=BOLD, font="思源黑体 CN")
        year.next_to(title, DOWN, buff=0.6)

        # Honors List
        honor1 = Text("入选教育部‘卓越工程师教育培养计划’试点专业", font_size=32, color=MY_WHITE, font="思源黑体 CN")
        honor2 = Text("入选重庆市‘三特行动计划’首批特色专业建设点", font_size=32, color=MY_WHITE, font="思源黑体 CN")
        honors_list = VGroup(honor1, honor2).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        honors_list.next_to(year, DOWN, buff=0.6)

        # Voiceover and Animation
        voice_text_scene_05 = "接下来了解水利水电工程专业。2013年是重要的一年，该专业入选了教育部的“卓越工程师教育培养计划”试点，并成为重庆市“三特行动计划”的首批特色专业建设点。"
        with custom_voiceover_tts(voice_text_scene_05) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_05, font_size=32, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5),
                    lag_ratio=0.0
                ),
                run_time=1.5
            )
            self.play(FadeIn(year), run_time=0.5)

            # Animate honors list
            self.play(FadeIn(honor1, shift=UP * 0.2), run_time=1.0)
            self.play(FadeIn(honor2, shift=UP * 0.2), run_time=1.0)

            # Wait for remaining audio
            elapsed_time = 1.5 + 0.5 + 1.0 + 1.0 # Title + year + honor1 + honor2
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_06(self):
        """Scene 6: Hydraulic & Hydroelectric Eng. - Credit Composition"""
        bg6 = self.create_background(color=MY_BLUE_A, opacity=0.8) # Keep background
        self.add(bg6)
        scene_num_06 = self.get_scene_number("06")
        self.add(scene_num_06)

        # Keep the title from the previous scene if desired, or recreate if needed
        title = Text("水利水电工程 🌊", font_size=48, color=MY_WHITE, font="思源黑体 CN Bold")
        title.to_edge(UP, buff=1.0)
        self.add(title) # Add title statically

        # Total Credits Info
        label_total = Text("总学分", font_size=36, color=MY_WHITE, font="思源黑体 CN")
        value_total = Text("166 + 10 学分", font_size=60, color=MY_GOLD, weight=BOLD, font="思源黑体 CN") # Highlight +10
        credits_total = VGroup(label_total, value_total).arrange(DOWN, buff=0.3)
        credits_total.move_to(UP * 0.5)

        # Graduation Design Credits Info
        label_design = Text("毕业设计", font_size=36, color=MY_WHITE, font="思源黑体 CN")
        value_design = Text("12 学分", font_size=60, color=MY_GOLD, weight=BOLD, font="思源黑体 CN")
        credits_design = VGroup(label_design, value_design).arrange(DOWN, buff=0.3)
        credits_design.next_to(credits_total, DOWN, buff=1.0)

        # Voiceover and Animation
        voice_text_scene_06 = "水利水电工程的总学分要求是 166 加 10 学分。其中，毕业设计占 12 学分。"
        with custom_voiceover_tts(voice_text_scene_06) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_06, font_size=32, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            self.play(FadeIn(subtitle_voice, run_time=0.5))

            # Animate credit info
            self.play(GrowFromCenter(credits_total), run_time=1.0)
            self.play(FadeIn(credits_design), run_time=1.0)

            # Wait for remaining audio
            elapsed_time = 0.5 + 1.0 + 1.0 # Subtitle + total + design
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_07(self):
        """Scene 7: Hydraulic & Hydroelectric Eng. - Core Courses"""
        bg7 = self.create_background(color=MY_BLUE_A, opacity=0.8) # Keep background
        self.add(bg7)
        scene_num_07 = self.get_scene_number("07")
        self.add(scene_num_07)

        # Title
        title = Text("专业核心课程 🏗️", font_size=48, color=MY_WHITE, font="思源黑体 CN Bold")
        title.to_edge(UP, buff=1.0)

        # Bulleted List
        courses = [
            "工程水文与水资源综合利用",
            "水工建筑物",
            "水电站",
            "水利工程施工与管理"
        ]
        course_list = BulletedList(
            *courses,
            dot_color=MY_WHITE,
            buff=0.4,
            font_size=36,
            font="思源黑体 CN"
        )
        course_list.set_color(MY_WHITE)
        course_list.next_to(title, DOWN, buff=0.8).align_to(title, LEFT).shift(RIGHT*1)

        # Voiceover and Animation
        voice_text_scene_07 = "水利水电工程的核心课程主要有：工程水文与水资源综合利用、水工建筑物、水电站，以及水利工程施工与管理。"
        with custom_voiceover_tts(voice_text_scene_07) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_07, font_size=32, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.0),
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # Animate list items
            total_list_anim_time = max(0.5, tracker.duration - 1.0 - 1.0 - 0.5)
            run_time_per_item = total_list_anim_time / len(courses)

            self.play(
                AnimationGroup(
                    *[FadeIn(item, shift=UP * 0.2) for item in course_list],
                    lag_ratio=0.6
                ),
                run_time=total_list_anim_time
            )

            # Wait if animation finished before audio
            elapsed_time = 1.0 + total_list_anim_time
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_08(self):
        """Scene 8: Self-Development Plan - Aesthetic Education"""
        bg8 = self.create_background(color=MY_BEIGE) # Neutral beige background
        self.add(bg8)
        scene_num_08 = self.get_scene_number("08")
        # Adjust scene number color for beige background if needed
        scene_num_08.set_color(MY_BLACK) # Change to black for better contrast
        self.add(scene_num_08)

        # Title
        title = Text("自主发展计划（第二课堂）", font_size=48, color=MY_BLACK, font="思源黑体 CN Bold") # Black text
        title.to_edge(UP, buff=1.5)

        # Content
        label = Text("美育 🎨", font_size=40, color=MY_BLUE_C, font="思源黑体 CN") # Blue label
        practice = Text("美育实践", font_size=40, color=MY_BLACK, weight=BOLD, font="思源黑体 CN") # Black text
        content = VGroup(label, practice).arrange(DOWN, buff=0.4)
        content.next_to(title, DOWN, buff=1.0)

        # Optional Icon (Example: Paintbrush)
        # try:
        #     # Ensure you have the SVG file or use a built-in Mobject
        #     # icon = SVGMobject("path/to/paintbrush.svg").scale(0.5)
        #     icon = Circle(radius=0.3, color=MY_ORANGE, fill_opacity=1).next_to(content, RIGHT, buff=0.5) # Placeholder icon
        # except:
        #     icon = None # Handle cases where icon loading fails
        #     print("Warning: Icon could not be loaded/created.")

        # Voiceover and Animation
        voice_text_scene_08 = "在自主发展计划，也就是第二课堂中，美育实践是其中的一个重要组成部分。"
        with custom_voiceover_tts(voice_text_scene_08) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_08, font_size=32, color=MY_BLACK, # Black subtitle on beige
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5),
                    lag_ratio=0.0
                ),
                run_time=1.5
            )
            # Animate content and icon (if exists)
            anim_group = [FadeIn(content, run_time=1.0)]
            # if icon:
            #     anim_group.append(FadeIn(icon, run_time=1.0))
            self.play(AnimationGroup(*anim_group, lag_ratio=0.0)) # Play simultaneously

            # Wait for remaining audio
            elapsed_time = 1.5 + 1.0 # Title + Content/Icon
            remaining_time = tracker.duration - elapsed_time - 1.0 # Subtract fade out time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_09(self):
        """Scene 9: Ending Screen"""
        # Background: Restore initial gradient or use a new ending background
        bg9 = self.create_background(gradient_colors=[MY_BLUE_D, MY_TEAL_E], gradient_direction=np.array([1, -1, 0]))
        self.add(bg9)
        # Optional: Scene number "09" or hide it
        # scene_num_09 = self.get_scene_number("09")
        # self.add(scene_num_09)

        # Ending Text
        end_text = Text("专业信息速览完毕 ✨", font_size=48, color=MY_WHITE, font="思源黑体 CN")
        end_text.move_to(ORIGIN + UP * 0.5)

        # Optional: Further info text
        info_text = Text("更多详细信息请查询官方网站", font_size=28, color=MY_LIGHT_GRAY, font="思源黑体 CN")
        info_text.next_to(end_text, DOWN, buff=0.8)

        # Voiceover and Animation
        voice_text_scene_09 = "本次重庆交通大学港口航道与海岸工程、水利水电工程的专业信息速览到此结束。感谢您的观看！"
        with custom_voiceover_tts(voice_text_scene_09) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text_scene_09, font_size=32, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True, font="思源黑体 CN"
            ).to_edge(DOWN, buff=0.5)

            # Animate ending text
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    FadeIn(end_text, run_time=1.5),
                    lag_ratio=0.0
                ),
                run_time=1.5
            )
            self.play(FadeIn(info_text, run_time=1.0))

            # Optional: Camera zoom out slightly
            self.play(self.camera.frame.animate.scale(1.1), run_time=tracker.duration - 1.5 - 1.0 - 1.0) # Scale during remaining time

            # Wait for remaining audio (if scaling animation is shorter)
            elapsed_time = 1.5 + 1.0 # End text + info text
            # Adjust remaining time calculation based on whether scaling animation runs concurrently or after
            # Assuming scaling runs for the rest of the audio duration after text appears:
            remaining_time = 0 # Already accounted for in scaling run_time

            if remaining_time > 0:
                 self.wait(remaining_time)

            # Fade out subtitle before final wait
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        # Final pause before the scene ends
        self.wait(2)
        # Fade out the entire scene content
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)


# --- Main execution block ---
if __name__ == "__main__":
    # Basic configuration
    config.pixel_height = 1080  # Set resolution height
    config.pixel_width = 1920   # Set resolution width
    config.frame_rate = 30      # Set frame rate
    config.output_file = "CombinedScene"  # Specify output filename
    config.disable_caching = True # Disable caching

    # Set output directory - #(output_video) will be replaced by the Java program
    config.media_dir = "./#(output_video)"

    # Ensure the directory exists
    if config.media_dir == "./#(output_video)":
        # If the placeholder is still there, create a default directory for local testing
        default_output_dir = "./manim_videos"
        print(f"Warning: Output directory placeholder '#(output_video)' detected. Using default: '{default_output_dir}'")
        config.media_dir = default_output_dir
        os.makedirs(config.media_dir, exist_ok=True)
    else:
        # If it's a specific path, ensure it exists
        os.makedirs(config.media_dir, exist_ok=True)


    # Set default font for Text objects if needed globally
    # config.font = "思源黑体 CN" # Example: Set default font

    # Create and render the scene
    scene = CombinedScene()
    scene.render()
    print(f"Scene rendering finished. Output saved in: {config.media_dir}")