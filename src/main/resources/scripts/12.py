# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
import hashlib
from moviepy import AudioFileClip # Correct import for AudioFileClip
import manimpango # For font checking

# --- Custom Colors ---
MY_LIGHT_GRAY = "#DDDDDD"
MY_WHITE = "#FFFFFF"
MY_DARK_GRAY = "#555555"
MY_BLACK = "#000000"
MY_DARK_BLUE = "#00008B"
MY_RED_STR = "FF0000" # Hex code without # for LaTeX color
MY_GREEN_STR = "008000"
MY_BLUE_STR = "0000FF"
MY_RED = "#" + MY_RED_STR
MY_GREEN = "#" + MY_GREEN_STR
MY_BLUE = "#" + MY_BLUE_STR
MY_YELLOW_HIGHLIGHT = "#FFFFE0" # For formula highlight background
MY_ORANGE = "#FFA500" # For (7x5) cubes
MY_CYAN = "#00FFFF" # For (5x2) cubes
MY_GRAY_CUBE = "#808080" # Final cube color
MY_LIGHT_BLUE_BG = "#E0EFFF" # Scene 4 background

# --- Font Check ---
DEFAULT_FONT = "Noto Sans CJK SC" # Or another preferred CJK font
final_font = None
available_fonts = manimpango.list_fonts()
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

# --- TTS Caching Setup ---
CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class CustomVoiceoverTracker:
    """Tracks audio path and duration for TTS."""
    def __init__(self, audio_path, duration):
        self.audio_path = audio_path
        self.duration = duration

def get_cache_filename(text):
    """Generates a unique filename based on the text hash."""
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}.mp3")

@contextmanager
def custom_voiceover_tts(text, token="123456", base_url="https://uni-ai.fly.dev/api/manim/tts"):
    """
    Fetches TTS audio, caches it, and provides path and duration.
    Usage: with custom_voiceover_tts("text") as tracker: ...
    """
    cache_file = get_cache_filename(text)
    audio_file = cache_file  # Initialize audio_file

    if os.path.exists(cache_file):
        print(f"Using cached TTS for: {text[:30]}...")
    else:
        print(f"Requesting TTS for: {text[:30]}...")
        try:
            # URL encode the input text to handle special characters
            input_text_encoded = requests.utils.quote(text)
            url = f"{base_url}?token={token}&input={input_text_encoded}"

            response = requests.get(url, stream=True, timeout=60)  # Added timeout
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            audio_file = cache_file
            print("TTS downloaded and cached.")

        except requests.exceptions.RequestException as e:
            print(f"TTS API request failed: {e}")
            # Fallback: create a dummy tracker with zero duration
            tracker = CustomVoiceoverTracker(None, 0)
            yield tracker
            return  # Exit context manager

    # Ensure audio file exists before processing with MoviePy
    if audio_file and os.path.exists(audio_file):
        try:
            clip = AudioFileClip(audio_file)
            duration = clip.duration
            clip.close()
            print(f"Audio duration: {duration:.2f}s")
            tracker = CustomVoiceoverTracker(audio_file, duration)
        except Exception as e:
            print(f"Error processing audio file {audio_file}: {e}")
            # Fallback if audio file is corrupted or invalid
            tracker = CustomVoiceoverTracker(None, 0)
    else:
        # Fallback if audio file was not created or found
        print(f"TTS audio file not found or not created: {audio_file}")
        tracker = CustomVoiceoverTracker(None, 0)

    try:
        yield tracker
    finally:
        # No cleanup needed here as we are caching
        pass

# --- Custom TeX Template for colorbox/color ---
# Needed for \colorbox and \color[HTML]
# DO NOT include \documentclass here!
color_support_template = TexTemplate(
    preamble=r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage[HTML]{xcolor} % Enable HTML colors and \color / \colorbox
\usepackage{graphicx}
% Add other necessary packages here if needed
"""
)

# --- Combined Scene ---
class CombinedScene(ThreeDScene): # Inherit from ThreeDScene for 3D capabilities

    # Store final objects to carry over if needed (e.g., for comparison)
    final_cubes_s2 = None
    final_axes_s2 = None
    final_labels_s2 = None
    final_dim_labels_s2 = None
    final_cubes_s3 = None
    final_axes_s3 = None
    final_labels_s3 = None
    final_dim_labels_s3 = None

    def setup(self):
        # Set default font if found
        if final_font:
            Text.set_default(font=final_font)
        # Set default TexTemplate for the scene if needed globally
        # Tex.set_default(tex_template=color_support_template)
        # MathTex.set_default(tex_template=color_support_template)
        # Or pass it individually where needed

        # Initial camera setup for 3D scene (can be overridden in scenes)
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES) # Start looking straight down

    def construct(self):
        self.play_scene_01()
        self.clear_and_reset() # Custom clear for 3D

        self.play_scene_02()
        self.clear_and_reset()

        self.play_scene_03()
        self.clear_and_reset()

        self.play_scene_04()
        self.clear_and_reset()

        # Final message
        self.set_camera_orientation(phi=0, theta=-PI/2) # Reset to 2D-like view
        final_message = Text("动画结束，感谢观看！ 😄", font_size=48, color=MY_BLACK)
        # Use a 2D background for the final message
        bg_final = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_LIGHT_BLUE_BG, fill_opacity=1, stroke_width=0).set_z_index(-10)
        # Add fixed in frame mobjects for 2D overlays in 3D scene
        self.add_fixed_in_frame_mobjects(bg_final)
        self.add_fixed_in_frame_mobjects(final_message) # Make message fixed

        self.play(FadeIn(final_message))
        self.wait(2)

    def get_scene_number(self, number_str):
        """Creates and positions the scene number, fixed to the frame."""
        scene_num = Text(number_str, font_size=24, color=MY_DARK_GRAY)
        scene_num.to_corner(UR, buff=0.3)
        scene_num.set_z_index(20) # Ensure above other elements
        # For 3D scenes, make it fixed in frame
        self.add_fixed_in_frame_mobjects(scene_num)
        return scene_num

    def create_gradient_background(self, color1, color2):
        """Creates a gradient background fixed to the frame."""
        # Create a 2D rectangle and add it as a fixed-in-frame mobject
        bg = Rectangle(
            width=config.frame_width * 2, # Make larger to avoid edge issues during rotation
            height=config.frame_height * 2,
            stroke_width=0,
            fill_opacity=1
        )
        # Apply gradient fill using list of colors (default is vertical DOWN)
        # Use set_fill which accepts a list for gradient
        bg.set_fill(color=[color1, color2], opacity=1)
        # Manually set the gradient direction if needed (e.g., vertical)
        # bg.set_sheen_direction(DOWN) # Default is DOWN
        bg.set_z_index(-10)
        # Add fixed in frame so it doesn't move with 3D camera
        self.add_fixed_in_frame_mobjects(bg)
        return bg

    def clear_and_reset(self):
        """Clears all mobjects and resets the camera for a new scene."""
        # *** FIX: Access fixed_in_frame_mobjects via self.camera ***
        all_mobs_to_clear = list(self.mobjects) + list(self.camera.fixed_in_frame_mobjects)

        # Clear updaters from all mobjects
        for mob in all_mobs_to_clear:
            # Check if the mobject exists and has updaters before clearing
            if mob is not None and hasattr(mob, 'get_updaters') and mob.get_updaters():
                mob.clear_updaters()

        # Fade out all mobjects (including fixed ones temporarily)
        # Use Group for potentially mixed object types
        valid_mobs = [m for m in all_mobs_to_clear if m is not None]
        if valid_mobs:
            self.play(FadeOut(Group(*valid_mobs)), run_time=0.5)

        # Clear the lists
        self.mobjects.clear()
        # *** FIX: Clear fixed_in_frame_mobjects via self.camera ***
        self.camera.fixed_in_frame_mobjects.clear()

        # Reset camera for 3D scene to a default state
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES) # Reset to top-down view
        # Reset zoom/distance and center
        self.move_camera(frame_center=ORIGIN, zoom=1.0, added_anims=[]) # Use move_camera to reset zoom

        self.wait(0.1)

    # --- Scene Implementations ---
    def play_scene_01(self):
        """Scene 1: Title and Problem Introduction"""
        scene_num = self.get_scene_number("01")
        bg = self.create_gradient_background(MY_LIGHT_GRAY, MY_WHITE)

        title = Text("图形化证明：乘法结合律", font_size=48, color=MY_BLACK)
        title.move_to(UP * 2)

        # Formula with colored numbers - requires custom TeX template
        # Use the STR versions of colors (without #) for LaTeX
        formula_str = r"{\color[HTML]{%s} 7} \times {\color[HTML]{%s} 5} \times {\color[HTML]{%s} 2} = {\color[HTML]{%s} 7} \times ({\color[HTML]{%s} 5} \times {\color[HTML]{%s} 2})" % (
            MY_RED_STR, MY_GREEN_STR, MY_BLUE_STR, MY_RED_STR, MY_GREEN_STR, MY_BLUE_STR
        )
        # Pass the custom template here
        formula = MathTex(formula_str, font_size=42, color=MY_DARK_BLUE, tex_template=color_support_template)
        formula.next_to(title, DOWN, buff=0.8)

        # Add elements as fixed in frame for this 2D-like scene
        self.add_fixed_in_frame_mobjects(title)
        self.add_fixed_in_frame_mobjects(formula)

        voice_text_01 = "大家好！本期视频，我们将用图形化的方式来证明乘法的结合律。具体来说，我们要证明 7 乘以 5 再乘以 2，等于 7 乘以 5 乘以 2 的积。"
        with custom_voiceover_tts(voice_text_01) as tracker:
            audio_duration = tracker.duration if tracker.audio_path else 0
            if tracker.audio_path and audio_duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("Warning: Scene 1 TTS failed or has zero duration.")

            subtitle_voice = Text(voice_text_01, font_size=32, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5)
            self.add_fixed_in_frame_mobjects(subtitle_voice) # Fixed subtitle

            anim_title_duration = 1.5
            anim_formula_delay = 0.5
            anim_formula_duration = 1.0
            fade_out_duration = 1.0
            # Calculate total animation time BEFORE fade out
            total_anim_duration_planned = anim_title_duration + anim_formula_delay + anim_formula_duration

            # Use FadeIn for Text as Write might cause issues
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5), # Subtitle appears first
                    FadeIn(title, shift=UP*0.2), # Use FadeIn for title
                    lag_ratio=0.0
                ),
                run_time=anim_title_duration
            )
            self.wait(anim_formula_delay)
            # Use Write for MathTex as it's a VMobject
            self.play(Write(formula), run_time=anim_formula_duration)

            # Calculate wait time based on audio duration vs animation time
            if audio_duration > 0:
                elapsed_time = total_anim_duration_planned
                time_for_fadeout = fade_out_duration
                remaining_time = audio_duration - elapsed_time - time_for_fadeout
                if remaining_time > 0:
                    self.wait(remaining_time)
            else:
                # If no audio, just wait a bit after animations
                self.wait(2.0)

            # Fade out the voiceover subtitle
            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)

        self.wait(1)


    def play_scene_02(self):
        """Scene 2: (7x5) x 2 Visualization"""
        scene_num = self.get_scene_number("02")
        bg = self.create_gradient_background(MY_LIGHT_GRAY, MY_WHITE)

        initial_phi = 75 * DEGREES
        initial_theta = -45 * DEGREES
        initial_distance = 15
        self.set_camera_orientation(phi=initial_phi, theta=initial_theta, distance=initial_distance)

        left_zone_x = -config.frame_width / 4
        right_zone_x = config.frame_width / 4

        # --- Left Text & Formulas (Fixed in Frame) ---
        text_title = Text("计算方式一：先算 7 × 5", font_size=30, color=MY_BLACK)
        text_title.move_to([left_zone_x, 3, 0]).align_to([-config.frame_width/2 + 1, 0, 0], LEFT)
        formula_s2_1_str = r"({\color[HTML]{%s} 7} \times {\color[HTML]{%s} 5}) \times {\color[HTML]{%s} 2}" % (MY_RED_STR, MY_GREEN_STR, MY_BLUE_STR)
        formula_s2_1 = MathTex(formula_s2_1_str, font_size=36, color=MY_DARK_BLUE, tex_template=color_support_template)
        formula_s2_1.next_to(text_title, DOWN, buff=0.5, aligned_edge=LEFT)
        formula_s2_2_str = r"{\color[HTML]{%s} 7} \times {\color[HTML]{%s} 5} = 35" % (MY_RED_STR, MY_GREEN_STR)
        formula_s2_2 = MathTex(formula_s2_2_str, font_size=36, color=MY_BLACK, tex_template=color_support_template)
        formula_s2_2.next_to(formula_s2_1, DOWN, buff=0.5, aligned_edge=LEFT)
        formula_s2_3_str = r"= 35 \times {\color[HTML]{%s} 2} = 70" % MY_BLUE_STR
        formula_s2_3 = MathTex(formula_s2_3_str, font_size=36, color=MY_BLACK, tex_template=color_support_template)
        formula_s2_3.move_to(formula_s2_1).align_to(formula_s2_1, LEFT)
        left_group = VGroup(text_title, formula_s2_1, formula_s2_2)
        self.add_fixed_in_frame_mobjects(left_group)
        formula_s2_2.set_opacity(0)
        # highlight_rect created later

        # --- Right 3D Visualization ---
        axes = ThreeDAxes(
            x_range=[0, 8, 2], y_range=[0, 6, 2], z_range=[0, 3, 1],
            x_length=7, y_length=5, z_length=3,
            axis_config={"color": MY_DARK_GRAY, "include_tip": False, "stroke_width": 2, "include_numbers": True, "decimal_number_config": {"num_decimal_places": 0}},
            x_axis_config={"color": MY_RED}, y_axis_config={"color": MY_GREEN}, z_axis_config={"color": MY_BLUE},
        )
        axes.move_to([right_zone_x, 0, 0])
        labels = axes.get_axis_labels(
            x_label=Tex("7", color=MY_RED), y_label=Tex("5", color=MY_GREEN), z_label=Tex("2", color=MY_BLUE)
        )

        # *** FIX: Add axes and labels to the scene explicitly first ***
        self.add(axes, labels)
        # Make them initially invisible if FadeIn animation is desired
        axes.set_opacity(0)
        labels.set_opacity(0)

        # Cube properties
        cube_size = 0.5
        gap = 0.0
        base_layer = VGroup()
        x_offset = - (7 - 1) * (cube_size + gap) / 2
        y_offset = - (5 - 1) * (cube_size + gap) / 2
        z_offset = cube_size / 2
        for i in range(7):
            for j in range(5):
                cube = Cube(side_length=cube_size, fill_opacity=0.8, stroke_width=0.5, stroke_color=MY_DARK_GRAY)
                x_pos = i * (cube_size + gap) + x_offset
                y_pos = j * (cube_size + gap) + y_offset
                z_pos = z_offset
                cube.move_to(axes.get_origin() + RIGHT * x_pos + UP * y_pos + OUT * (z_pos - cube_size/2))
                cube.set_fill(MY_ORANGE)
                base_layer.add(cube)
        top_layer = base_layer.copy()
        top_layer.shift(OUT * (cube_size + gap))
        top_layer.set_fill(MY_BLUE)
        # cubes_group = VGroup(base_layer, top_layer) # Group for potential later use

        # --- Animations ---
        voice_text_02 = "现在来看第一种计算方式，我们先计算 7 乘以 5。在右边的三维空间里，我们构建一个 7 行 5 列的底层，由 35 个小方块组成，代表 7 乘以 5 等于 35。接着，我们将这个底层向上堆叠一层，代表乘以 2。这样，我们就得到了一个 7 乘 5 乘 2 的长方体，总共有 35 乘以 2，等于 70 个小方块。"
        with custom_voiceover_tts(voice_text_02) as tracker:
            audio_duration = tracker.duration if tracker.audio_path else 0
            if tracker.audio_path and audio_duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else: print("Warning: Scene 2 TTS failed or has zero duration.")

            subtitle_voice = Text(voice_text_02, font_size=32, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5)
            self.add_fixed_in_frame_mobjects(subtitle_voice)

            anim_intro_duration = 1.5
            anim_base_duration = 2.0
            anim_stack_duration = 1.5
            fade_out_duration = 1.0

            target_highlight = VGroup(formula_s2_1.get_part_by_tex("7"), formula_s2_1.get_part_by_tex("5"), formula_s2_1.get_part_by_tex(r"\times")[0])
            highlight_rect = SurroundingRectangle(target_highlight, buff=0.05, color=MY_YELLOW_HIGHLIGHT, fill_color=MY_YELLOW_HIGHLIGHT, fill_opacity=0.3, stroke_width=0)
            self.add_fixed_in_frame_mobjects(highlight_rect)
            highlight_rect.set_opacity(0)

            # *** FIX: Animate FadeIn for already added axes/labels ***
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    FadeIn(axes), # FadeIn the axes
                    FadeIn(labels), # FadeIn the labels
                    FadeIn(text_title),
                    Write(formula_s2_1),
                    FadeIn(highlight_rect),
                    lag_ratio=0.0
                ),
                run_time=anim_intro_duration
            )

            self.play(
                AnimationGroup(
                    Create(base_layer, lag_ratio=0.01),
                    FadeIn(formula_s2_2, shift=DOWN*0.2),
                    lag_ratio=0.1
                ),
                run_time=anim_base_duration
            )

            self.move_camera(phi=65 * DEGREES, theta=-55 * DEGREES, distance=initial_distance * 1.1, run_time=anim_stack_duration)
            self.play(
                AnimationGroup(
                    TransformFromCopy(base_layer, top_layer),
                    ReplacementTransform(VGroup(formula_s2_1, highlight_rect), formula_s2_3),
                    FadeOut(formula_s2_2),
                    lag_ratio=0.1
                ),
                run_time=anim_stack_duration
            )

            total_anim_time = anim_intro_duration + anim_base_duration + anim_stack_duration
            if audio_duration > 0:
                remaining_time = audio_duration - total_anim_time - fade_out_duration
                if remaining_time > 0: self.wait(remaining_time)
            else: self.wait(1.5)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)

        self.wait(1)
        CombinedScene.final_cubes_s2 = VGroup(base_layer, top_layer)
        CombinedScene.final_axes_s2 = axes
        CombinedScene.final_labels_s2 = labels

    def play_scene_03(self):
        """Scene 3: 7 x (5x2) Visualization"""
        scene_num = self.get_scene_number("03")
        bg = self.create_gradient_background(MY_LIGHT_GRAY, MY_WHITE)

        initial_phi = 75 * DEGREES
        initial_theta = 15 * DEGREES
        initial_distance = 15
        self.set_camera_orientation(phi=initial_phi, theta=initial_theta, distance=initial_distance)

        left_zone_x = -config.frame_width / 4
        right_zone_x = config.frame_width / 4

        # --- Left Text & Formulas (Fixed in Frame) ---
        text_title_s3 = Text("计算方式二：先算 5 × 2", font_size=30, color=MY_BLACK)
        text_title_s3.move_to([left_zone_x, 3, 0]).align_to([-config.frame_width/2 + 1, 0, 0], LEFT)
        formula_s3_1_str = r"{\color[HTML]{%s} 7} \times ({\color[HTML]{%s} 5} \times {\color[HTML]{%s} 2})" % (MY_RED_STR, MY_GREEN_STR, MY_BLUE_STR)
        formula_s3_1 = MathTex(formula_s3_1_str, font_size=36, color=MY_DARK_BLUE, tex_template=color_support_template)
        formula_s3_1.next_to(text_title_s3, DOWN, buff=0.5, aligned_edge=LEFT)
        formula_s3_2_str = r"{\color[HTML]{%s} 5} \times {\color[HTML]{%s} 2} = 10" % (MY_GREEN_STR, MY_BLUE_STR)
        formula_s3_2 = MathTex(formula_s3_2_str, font_size=36, color=MY_BLACK, tex_template=color_support_template)
        formula_s3_2.next_to(formula_s3_1, DOWN, buff=0.5, aligned_edge=LEFT)
        formula_s3_3_str = r"= {\color[HTML]{%s} 7} \times 10 = 70" % MY_RED_STR
        formula_s3_3 = MathTex(formula_s3_3_str, font_size=36, color=MY_BLACK, tex_template=color_support_template)
        formula_s3_3.move_to(formula_s3_1).align_to(formula_s3_1, LEFT)
        left_group_s3 = VGroup(text_title_s3, formula_s3_1, formula_s3_2)
        self.add_fixed_in_frame_mobjects(left_group_s3)
        formula_s3_2.set_opacity(0)
        # highlight_rect_s3 created later

        # --- Right 3D Visualization ---
        axes_s3 = ThreeDAxes(
            x_range=[0, 8, 2], y_range=[0, 6, 2], z_range=[0, 3, 1],
            x_length=7, y_length=5, z_length=3,
            axis_config={"color": MY_DARK_GRAY, "include_tip": False, "stroke_width": 2, "include_numbers": True, "decimal_number_config": {"num_decimal_places": 0}},
            x_axis_config={"color": MY_RED}, y_axis_config={"color": MY_GREEN}, z_axis_config={"color": MY_BLUE},
        )
        axes_s3.move_to([right_zone_x, 0, 0])
        labels_s3 = axes_s3.get_axis_labels(
            x_label=Tex("7", color=MY_RED), y_label=Tex("5", color=MY_GREEN), z_label=Tex("2", color=MY_BLUE)
        )

        # *** FIX: Add axes and labels to the scene explicitly first ***
        self.add(axes_s3, labels_s3)
        axes_s3.set_opacity(0)
        labels_s3.set_opacity(0)


        cube_size = 0.5
        gap = 0.0
        slice_layer = VGroup()
        x_offset_s3 = - (7 - 1) * (cube_size + gap) / 2
        y_offset_s3 = - (5 - 1) * (cube_size + gap) / 2
        z_offset_s3 = - (2 - 1) * (cube_size + gap) / 2
        first_slice_x = x_offset_s3 + cube_size / 2
        for j in range(5):
            for k in range(2):
                cube = Cube(side_length=cube_size, fill_opacity=0.8, stroke_width=0.5, stroke_color=MY_DARK_GRAY)
                x_pos = first_slice_x
                y_pos = j * (cube_size + gap) + y_offset_s3 + cube_size / 2
                z_pos = k * (cube_size + gap) + z_offset_s3 + cube_size / 2
                cube.move_to(axes_s3.get_origin() + RIGHT * x_pos + UP * y_pos + OUT * z_pos)
                cube.set_fill(MY_CYAN)
                slice_layer.add(cube)

        full_block = VGroup()
        all_slices = []
        for i in range(7):
            new_slice = slice_layer.copy()
            x_shift = i * (cube_size + gap)
            actual_shift = RIGHT * x_shift
            new_slice.shift(actual_shift)
            new_slice.set_fill(MY_GRAY_CUBE)
            full_block.add(new_slice)
            all_slices.append(new_slice)

        # --- Animations ---
        voice_text_03 = "接下来，我们换一种方式，先计算括号里的 5 乘以 2。我们在 YZ 平面上构建一个 5 行 2 列的切片，由 10 个小方块组成，代表 5 乘以 2 等于 10。然后，我们将这个切片沿着 X 轴方向扩展 7 次，代表乘以 7。最终，我们同样得到了一个 7 乘 5 乘 2 的长方体，总共有 7 乘以 10，等于 70 个小方块。请注意，这个长方体和上一种方法得到的是完全一样的！"
        with custom_voiceover_tts(voice_text_03) as tracker:
            audio_duration = tracker.duration if tracker.audio_path else 0
            if tracker.audio_path and audio_duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else: print("Warning: Scene 3 TTS failed or has zero duration.")

            subtitle_voice = Text(voice_text_03, font_size=32, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.5)
            self.add_fixed_in_frame_mobjects(subtitle_voice)

            anim_intro_duration = 1.5
            anim_slice_duration = 1.5
            anim_extend_duration = 2.0
            fade_out_duration = 1.0

            target_highlight_s3 = VGroup(formula_s3_1.get_part_by_tex("5"), formula_s3_1.get_part_by_tex("2"), formula_s3_1.get_part_by_tex(r"\times")[1])
            highlight_rect_s3 = SurroundingRectangle(target_highlight_s3, buff=0.05, color=MY_YELLOW_HIGHLIGHT, fill_color=MY_YELLOW_HIGHLIGHT, fill_opacity=0.3, stroke_width=0)
            self.add_fixed_in_frame_mobjects(highlight_rect_s3)
            highlight_rect_s3.set_opacity(0)

            # *** FIX: Animate FadeIn for already added axes/labels ***
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    FadeIn(axes_s3), # FadeIn the axes
                    FadeIn(labels_s3), # FadeIn the labels
                    FadeIn(text_title_s3),
                    Write(formula_s3_1),
                    FadeIn(highlight_rect_s3),
                    lag_ratio=0.0
                ),
                run_time=anim_intro_duration
            )

            self.play(
                AnimationGroup(
                    Create(slice_layer, lag_ratio=0.05),
                    FadeIn(formula_s3_2, shift=DOWN*0.2),
                    lag_ratio=0.1
                ),
                run_time=anim_slice_duration
            )

            final_phi = 65 * DEGREES
            final_theta = -55 * DEGREES
            final_distance = initial_distance * 1.1
            self.move_camera(phi=final_phi, theta=final_theta, distance=final_distance, run_time=anim_extend_duration)
            self.play(
                AnimationGroup(
                    LaggedStart(*[TransformFromCopy(slice_layer if i==0 else all_slices[i-1], s) for i, s in enumerate(all_slices)], lag_ratio=0.1),
                    ReplacementTransform(VGroup(formula_s3_1, highlight_rect_s3), formula_s3_3),
                    FadeOut(formula_s3_2),
                    FadeOut(slice_layer, run_time=0.1),
                    lag_ratio=0.1
                ),
                run_time=anim_extend_duration
            )

            total_anim_time = anim_intro_duration + anim_slice_duration + anim_extend_duration
            if audio_duration > 0:
                remaining_time = audio_duration - total_anim_time - fade_out_duration
                if remaining_time > 0: self.wait(remaining_time)
            else: self.wait(1.5)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)

        self.wait(1)
        CombinedScene.final_cubes_s3 = full_block
        CombinedScene.final_axes_s3 = axes_s3
        CombinedScene.final_labels_s3 = labels_s3

    def play_scene_04(self):
        """Scene 4: Comparison and Conclusion"""
        scene_num = self.get_scene_number("04")
        # Use a plain background fixed in frame
        bg = Rectangle(width=config.frame_width*2, height=config.frame_height*2, fill_color=MY_LIGHT_BLUE_BG, fill_opacity=1, stroke_width=0).set_z_index(-10)
        self.add_fixed_in_frame_mobjects(bg)

        # Camera: Stable view, matching the end view of Scene 2 & 3
        final_phi = 65 * DEGREES
        final_theta = -55 * DEGREES
        final_distance = 15 * 1.1 # Match end distance
        self.set_camera_orientation(phi=final_phi, theta=final_theta, distance=final_distance)

        # --- Center: Final Cube ---
        # Use the cube from scene 3 (or scene 2, they should be identical)
        # Ensure it's colored gray
        if CombinedScene.final_cubes_s3:
             # Need to ensure the object exists before copying
            final_cube_display = CombinedScene.final_cubes_s3.copy()
        elif CombinedScene.final_cubes_s2:
            final_cube_display = CombinedScene.final_cubes_s2.copy()
        else:
            # Fallback: create a dummy cube if previous scenes failed
            print("Warning: Could not retrieve final cubes from previous scenes.")
            final_cube_display = Cube() # Placeholder

        final_cube_display.set_fill(MY_GRAY_CUBE, opacity=0.8)
        final_cube_display.move_to(ORIGIN) # Center it in 3D space

        # --- Left Formula (Fixed) ---
        formula_left_str1 = r"({\color[HTML]{%s} 7} \times {\color[HTML]{%s} 5}) \times {\color[HTML]{%s} 2}" % (MY_RED_STR, MY_GREEN_STR, MY_BLUE_STR)
        formula_left_str2 = r"= 35 \times {\color[HTML]{%s} 2} = 70" % MY_BLUE_STR
        formula_left1 = MathTex(formula_left_str1, font_size=36, color=MY_BLACK, tex_template=color_support_template)
        formula_left2 = MathTex(formula_left_str2, font_size=36, color=MY_BLACK, tex_template=color_support_template)
        formula_left_group = VGroup(formula_left1, formula_left2).arrange(DOWN, aligned_edge=LEFT)
        # Position fixed relative to the frame
        formula_left_group.to_corner(LEFT + UP, buff=1.5)

        # --- Right Formula (Fixed) ---
        formula_right_str1 = r"{\color[HTML]{%s} 7} \times ({\color[HTML]{%s} 5} \times {\color[HTML]{%s} 2})" % (MY_RED_STR, MY_GREEN_STR, MY_BLUE_STR)
        formula_right_str2 = r"= {\color[HTML]{%s} 7} \times 10 = 70" % MY_RED_STR
        formula_right1 = MathTex(formula_right_str1, font_size=36, color=MY_BLACK, tex_template=color_support_template)
        formula_right2 = MathTex(formula_right_str2, font_size=36, color=MY_BLACK, tex_template=color_support_template)
        formula_right_group = VGroup(formula_right1, formula_right2).arrange(DOWN, aligned_edge=LEFT)
        # Position fixed relative to the frame
        formula_right_group.to_corner(RIGHT + UP, buff=1.5)

        # --- Arrows (Fixed) ---
        # Arrows need to connect fixed formulas to the 3D cube's projected position
        # Draw arrows from formula groups towards the center (ORIGIN in fixed frame)
        arrow_left = Arrow(formula_left_group.get_right(), ORIGIN + LEFT*2, buff=0.2, color=MY_DARK_GRAY)
        arrow_right = Arrow(formula_right_group.get_left(), ORIGIN + RIGHT*2, buff=0.2, color=MY_DARK_GRAY)

        # --- Core Equality (Fixed) ---
        core_eq_str = r"({\color[HTML]{%s} 7} \times {\color[HTML]{%s} 5}) \times {\color[HTML]{%s} 2} = {\color[HTML]{%s} 7} \times ({\color[HTML]{%s} 5} \times {\color[HTML]{%s} 2})" % (
            MY_RED_STR, MY_GREEN_STR, MY_BLUE_STR, MY_RED_STR, MY_GREEN_STR, MY_BLUE_STR
        )
        core_equality = MathTex(core_eq_str, font_size=42, color=MY_DARK_BLUE, tex_template=color_support_template)
        # Position below the cube's projected area
        core_equality.move_to(DOWN * 1.5)

        # --- Conclusion Text (Fixed) ---
        conclusion_text = Text(
            "两种不同的计算顺序，得到了完全相同的几何体和结果 (70)。\n这直观地证明了乘法结合律。",
            font_size=32, color=MY_BLACK, line_spacing=0.8, should_center=True
        )
        conclusion_text.to_edge(DOWN, buff=0.8)

        # Add elements
        self.add(final_cube_display) # The 3D cube itself is not fixed
        fixed_elements = VGroup(formula_left_group, formula_right_group, arrow_left, arrow_right, core_equality, conclusion_text)
        self.add_fixed_in_frame_mobjects(fixed_elements)
        # Hide elements initially
        fixed_elements.set_opacity(0)


        # --- Animations ---
        voice_text_04 = "最后我们来对比一下。左边是先算 7 乘 5，右边是先算 5 乘 2。虽然计算过程不同，但我们最终都得到了中间这个完全相同的、由 70 个小方块组成的灰色长方体。这表明，(7 乘以 5) 再乘以 2，等于 7 乘以 (5 乘以 2)。两种不同的计算顺序，得到了完全相同的几何体和结果 70。这直观地证明了乘法结合律。"
        with custom_voiceover_tts(voice_text_04) as tracker:
            audio_duration = tracker.duration if tracker.audio_path else 0
            if tracker.audio_path and audio_duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else: print("Warning: Scene 4 TTS failed or has zero duration.")

            subtitle_voice = Text(voice_text_04, font_size=32, color=MY_BLACK, width=config.frame_width - 2, should_center=True)
            # Position subtitle above conclusion text
            subtitle_voice.next_to(conclusion_text, UP, buff=0.3)
            self.add_fixed_in_frame_mobjects(subtitle_voice)
            subtitle_voice.set_opacity(0) # Hide initially

            # Timings
            anim_cube_fadein = 1.5
            anim_rotate_start_delay = 0.5
            anim_rotate_duration = 8.0 # Slow rotation duration (used for wait calculation)
            anim_formulas_duration = 1.5
            anim_arrows_duration = 1.0
            anim_core_eq_duration = 1.0
            anim_conclusion_duration = 1.5
            fade_out_duration = 1.0

            # Fade in cube and subtitle
            self.play(
                FadeIn(final_cube_display),
                FadeIn(subtitle_voice, run_time=0.5), # Show subtitle early
                run_time=anim_cube_fadein
            )

            # Add rotation updater after a delay
            self.wait(anim_rotate_start_delay)
            # Define rotation speed (radians per second)
            rotation_speed = 0.2 # Radians per second
            final_cube_display.add_updater(lambda m, dt: m.rotate(rotation_speed * dt, axis=UP))

            # Show formulas, arrows, core equality, conclusion
            self.play(FadeIn(formula_left_group, shift=RIGHT*0.5), FadeIn(formula_right_group, shift=LEFT*0.5), run_time=anim_formulas_duration)
            self.play(Create(arrow_left), Create(arrow_right), run_time=anim_arrows_duration)
            self.play(Write(core_equality), run_time=anim_core_eq_duration) # Use Write for MathTex
            # Highlight equals sign
            self.play(Indicate(core_equality.get_part_by_tex("="), scale_factor=1.5, color=MY_RED))
            self.play(FadeIn(conclusion_text, shift=UP*0.3), run_time=anim_conclusion_duration)

            # Calculate wait time based on audio, considering rotation is ongoing
            # Time spent on main animations (excluding rotation start delay)
            main_anim_time = anim_cube_fadein + anim_formulas_duration + anim_arrows_duration + anim_core_eq_duration + 0.5 + anim_conclusion_duration # Added 0.5 for Indicate
            if audio_duration > 0:
                remaining_time = audio_duration - main_anim_time - fade_out_duration
                if remaining_time > 0:
                    self.wait(remaining_time)
            else:
                # Wait for a reasonable time if no audio
                self.wait(max(0, anim_rotate_duration - main_anim_time)) # Wait roughly for rotation duration

            # Stop rotation before fading out
            # Check if updater exists before clearing
            if final_cube_display.get_updaters():
                 final_cube_display.clear_updaters()

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)

        self.wait(2) # Hold final screen


# --- Main execution block ---
if __name__ == "__main__":
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 30
    config.output_file = "CombinedScene"
    config.disable_caching = True
    # Use placeholder for output path - IMPORTANT: Use raw string or double backslashes if needed on Windows
    config.media_dir = r"12" # Java will replace this placeholder

    scene = CombinedScene()
    scene.render()
    print(f"Scene rendering finished. Output in: {config.media_dir}")