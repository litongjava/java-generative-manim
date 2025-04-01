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
MY_DARK_BLUE = "#003366"
MY_LIGHT_BLUE = "#ADD8E6"
MY_WHITE = "#FFFFFF"
MY_BLACK = "#000000"
MY_LIGHT_GRAY = "#EEEEEE"
MY_RED = "#DC2626"
MY_BLUE = "#3B82F6"
MY_ORANGE = "#F97316"
MY_GREEN = "#10B981"
MY_PURPLE = "#8B5CF6"
MY_GOLD = "#F59E0B"
MY_DARK_BG = "#0A192F"

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
    audio_file = None # Initialize audio_file
    duration = 0 # Initialize duration

    try:
        if os.path.exists(cache_file):
            audio_file = cache_file
        else:
            input_text = requests.utils.quote(text)
            url = f"{base_url}?token={token}&input={input_text}"

            response = requests.get(url, stream=True)
            if response.status_code != 200:
                print(f"TTS API Error: {response.status_code} - {response.text}")
                with open(cache_file, "wb") as f: pass # Create empty file
                audio_file = cache_file
            else:
                with open(cache_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk: f.write(chunk)
                audio_file = cache_file

        if audio_file and os.path.getsize(audio_file) > 0:
            try:
                clip = AudioFileClip(audio_file)
                duration = clip.duration
                clip.close()
            except Exception as e:
                print(f"Error processing audio file {audio_file}: {e}")
                duration = 0
        else:
             print(f"Warning: TTS cache file {cache_file} is empty or invalid.")
             duration = 0
             if not audio_file:
                 if not os.path.exists(cache_file):
                      with open(cache_file, "wb") as f: pass
                 audio_file = cache_file

        tracker = CustomVoiceoverTracker(audio_file, duration)
        yield tracker
    finally:
        pass

# --- Font Check ---
DEFAULT_FONT = "Noto Sans CJK SC"
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

# --- Helper Function for Subscripts ---
def create_symbol_with_text_subscript(base_symbol_str, sub_text_str, base_style, sub_style, sub_scale=0.7, sub_buff=0.05):
    """Creates a VGroup with a base symbol (MathTex) and a text subscript (Text)."""
    base_symbol = MathTex(base_symbol_str, **base_style)
    subscript = Text(sub_text_str, **sub_style).scale(sub_scale)
    # Position subscript relative to the bottom-right of the base symbol
    subscript.next_to(base_symbol.get_corner(DR), DR, buff=sub_buff)
    # Adjust vertical alignment slightly if needed (Pango vs LaTeX baseline)
    subscript.shift(UP * subscript.get_height() * 0.1) # Small adjustment often helps
    return VGroup(base_symbol, subscript)

# --- Combined Scene ---
class CombinedScene(MovingCameraScene):
    def setup(self):
        MovingCameraScene.setup(self)
        if final_font:
            Text.set_default(font=final_font)
            print(f"Default font set to: {final_font}")
        else:
             print("Using Manim default font.")

    def construct(self):
        self.scene_time_tracker = ValueTracker(0)
        self.play_scene_01()
        self.clear_and_reset()
        self.play_scene_02()
        self.clear_and_reset()
        self.play_scene_03()
        self.clear_and_reset()
        self.play_scene_04()
        self.clear_and_reset()
        self.play_scene_05()
        self.clear_and_reset()
        self.wait(1)

    def get_scene_number(self, number_str):
        scene_num = Text(number_str, font_size=24, color=MY_BLACK)
        scene_num.to_corner(DR, buff=0.5)
        scene_num.set_z_index(10)
        return scene_num

    def clear_and_reset(self):
        for mob in self.mobjects:
            if mob is not None: mob.clear_updaters()
        valid_mobjects = [m for m in self.mobjects if m is not None]
        if valid_mobjects:
            self.play(FadeOut(Group(*valid_mobjects), shift=DOWN * 0.5), run_time=0.5)
        self.clear()
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        self.scene_time_tracker.set_value(0)
        self.wait(0.1)

    def create_gradient_background(self, color1, color2):
        bg = Rectangle(
            width=config.frame_width * 1.1, height=config.frame_height * 1.1,
            stroke_width=0, fill_color=[color1, color2], fill_opacity=1
        )
        bg.set_z_index(-10)
        return bg

    # ==========================================================================
    # Scene 1: Problem Introduction
    # ==========================================================================
    def play_scene_01(self):
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        bg1 = self.create_gradient_background(MY_LIGHT_BLUE, MY_WHITE)
        scene_num_01 = self.get_scene_number("01")
        self.add(bg1, scene_num_01)

        title = Text("斜坡上雪橇做功问题分析", font_size=48, color=MY_DARK_BLUE, weight=BOLD)
        title.to_edge(UP, buff=0.8)

        text_style = {"font_size": 28, "color": MY_BLACK}
        math_style = {"font_size": 32, "color": MY_DARK_BLUE}
        line_buff = 0.4

        line1 = Text("滑雪巡逻队用绳子以 恒速 将救援雪橇及受害者沿斜坡 下放。", **text_style)
        line1.next_to(title, DOWN, buff=0.5)

        params_group = VGroup(
            MathTex("m = 90.0\\ \\text{kg}", **math_style),
            MathTex("\\theta = 60.0^\\circ", **math_style),
            MathTex("d = 30.0\\ \\text{m}", **math_style),
            MathTex("\\mu = 0.100", **math_style),
        ).arrange(RIGHT, buff=0.8).next_to(line1, DOWN, buff=line_buff)

        line2 = Text("计算：", **text_style).next_to(params_group, DOWN, buff=line_buff*1.5)

        # --- CORRECTED CALCULATION ITEMS (with Text Subscripts) ---
        calc_items_data = [
            {"text": "(a) 摩擦力做的功: ", "base": "W", "sub": "摩擦"},
            {"text": "(b) 绳子对雪橇做的功: ", "base": "W", "sub": "绳子"},
            {"text": "(c) 重力做的功: ", "base": "W", "sub": "重力"},
            {"text": "(d) 总功: ", "base": "W", "sub": "总"},
        ]
        calc_items = VGroup()
        item_text_style = {"font_size": 30, "color": MY_BLACK}
        item_base_math_style = {"font_size": 30, "color": MY_BLACK} # Style for 'W'
        item_sub_text_style = {"font_size": 30, "color": MY_BLACK} # Style for subscript Text

        for item_data in calc_items_data:
            text_part = Text(item_data["text"], **item_text_style)
            # Create 'W' with subscript using helper function
            symbol_part = create_symbol_with_text_subscript(
                item_data["base"],
                item_data["sub"],
                item_base_math_style,
                item_sub_text_style
            )
            line_group = VGroup(text_part, symbol_part).arrange(RIGHT, buff=0.15, aligned_edge=DOWN) # Align baseline
            calc_items.add(line_group)

        calc_items.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        calc_items.next_to(line2, DOWN, buff=line_buff).align_to(line2, LEFT)
        # --- END CORRECTION ---

        problem_group = VGroup(title, line1, params_group, line2, calc_items)

        # --- Schematic Diagram (Code unchanged from previous version) ---
        slope_angle = 60 * DEGREES
        slope_length = 4
        base_length = slope_length * np.cos(slope_angle)
        height = slope_length * np.sin(slope_angle)
        p0 = [-base_length / 2, -height / 2, 0]
        p1 = [base_length / 2, -height / 2, 0]
        p2 = [-base_length / 2, height / 2, 0]
        slope_line = Line(p1, p2, color=MY_BLACK)
        base_line = Line(p0, p1, color=MY_BLACK)
        arc = Arc(radius=0.5, start_angle=base_line.get_angle(), angle=slope_line.get_angle() - base_line.get_angle(), arc_center=p1, color=MY_BLACK)
        theta_label = MathTex("\\theta=60^\\circ", font_size=24, color=MY_BLACK)
        arc_mid_point_local = arc.point_from_proportion(0.5) - arc.get_arc_center()
        theta_label.next_to(arc.get_arc_center() + arc_mid_point_local * 1.2, RIGHT, buff=0.1)
        sled_width = 0.6; sled_height = 0.3
        sled_center = slope_line.point_from_proportion(0.5)
        sled = Rectangle(width=sled_width, height=sled_height, color=MY_BLUE, fill_opacity=0.5)
        sled.move_to(sled_center).rotate(slope_line.get_angle())
        disp_arrow_start = slope_line.point_from_proportion(0.7)
        disp_arrow_end = slope_line.point_from_proportion(0.2)
        disp_arrow = Arrow(disp_arrow_start, disp_arrow_end, buff=0, color=MY_RED, stroke_width=4, max_tip_length_to_length_ratio=0.15)
        disp_label = MathTex("d = 30.0\\ \\text{m}", font_size=24, color=MY_RED)
        disp_label.next_to(disp_arrow.get_center(), DOWN, buff=0.1).rotate(slope_line.get_angle(), about_point=disp_label.get_center())
        diagram = VGroup(slope_line, base_line, arc, theta_label, sled, disp_arrow, disp_label)
        diagram.scale(0.8).move_to(RIGHT * 3.5 + DOWN * 1.0)
        # --- End Schematic Diagram ---


        # --- Voiceover and Animation (Code unchanged from previous version) ---
        voice_text_01 = "大家好！本视频将分析一个经典的物理问题：一个滑雪巡逻队用绳子以恒定速度，将一个总质量为90千克、包含受害者的救援雪橇，沿着倾角为60度的斜坡向下放30米。已知摩擦系数为0.1。我们将计算摩擦力、绳子拉力、重力所做的功以及总功。"
        with custom_voiceover_tts(voice_text_01) as tracker:
            if tracker.audio_path and tracker.duration > 0: self.add_sound(tracker.audio_path, time_offset=0)
            else: print("Warning: Audio file not available or invalid for Scene 1.")
            subtitle_voice = Text(voice_text_01, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)
            self.play(AnimationGroup(FadeIn(subtitle_voice, run_time=0.5), Write(title, run_time=2.0), lag_ratio=0.0), run_time=2.0)
            self.play(FadeIn(line1, shift=DOWN*0.2), run_time=1.0)
            self.play(LaggedStartMap(FadeIn, params_group, shift=DOWN*0.2, lag_ratio=0.3), run_time=1.5)
            self.play(FadeIn(line2, shift=DOWN*0.2), run_time=0.5)
            self.play(LaggedStartMap(FadeIn, calc_items, shift=DOWN*0.2, lag_ratio=0.2), run_time=2.0) # Animate corrected items
            self.play(Create(VGroup(slope_line, base_line)), run_time=1.0)
            self.play(Create(arc), Write(theta_label), run_time=0.8)
            self.play(Create(sled), run_time=0.8)
            self.play(Create(disp_arrow), Write(disp_label), run_time=1.0)
            content_group = VGroup(problem_group, diagram)
            self.play(self.camera.frame.animate.scale(1.1).move_to(content_group.get_center()), run_time=1.5)
            total_anim_time = 2.0 + 1.0 + 1.5 + 0.5 + 2.0 + 1.0 + 0.8 + 0.8 + 1.0 + 1.5
            subtitle_fadeout_time = 1.0
            if tracker.duration > 0:
                remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
                if remaining_wait > 0: self.wait(remaining_wait)
            else: self.wait(2.0)
            self.play(FadeOut(subtitle_voice), run_time=subtitle_fadeout_time)
        self.wait(1)

    # ==========================================================================
    # Scene 2: Force Analysis (Unchanged)
    # ==========================================================================
    def play_scene_02(self):
        # This scene does not contain mixed text/math issues, code remains the same
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        bg2 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_LIGHT_GRAY, fill_opacity=1, stroke_width=0)
        bg2.set_z_index(-10)
        scene_num_02 = self.get_scene_number("02")
        self.add(bg2, scene_num_02)
        title2 = Text("1. 受力分析与坐标系", font_size=36, color=MY_BLACK)
        title2.to_corner(UL, buff=0.5)
        slope_angle = 60 * DEGREES
        slope_visual_length = 6
        slope_line = Line(LEFT * slope_visual_length / 2, RIGHT * slope_visual_length / 2, color=MY_BLACK)
        slope_line.rotate(slope_angle, about_point=ORIGIN).shift(DOWN*0.5)
        sled_width = 1.0; sled_height = 0.5
        sled = Rectangle(width=sled_width, height=sled_height, color=MY_BLUE, fill_opacity=0.7, stroke_color=MY_BLACK)
        sled.move_to(slope_line.get_center()).rotate(slope_line.get_angle())
        sled_center = sled.get_center()
        diagram_group = VGroup(slope_line, sled).move_to(ORIGIN + RIGHT*1.0)
        axis_length = 2.0
        x_axis = Arrow(ORIGIN, RIGHT * axis_length, buff=0, color=MY_BLACK, stroke_width=3, max_tip_length_to_length_ratio=0.1)
        y_axis = Arrow(ORIGIN, UP * axis_length, buff=0, color=MY_BLACK, stroke_width=3, max_tip_length_to_length_ratio=0.1)
        x_label = MathTex("x", font_size=30, color=MY_BLACK).next_to(x_axis.get_end(), DR, buff=0.1)
        y_label = MathTex("y", font_size=30, color=MY_BLACK).next_to(y_axis.get_end(), UR, buff=0.1)
        coord_sys = VGroup(x_axis, y_axis, x_label, y_label).rotate(slope_angle, about_point=ORIGIN).move_to(sled_center)
        force_scale = 1.5
        arrow_config = {"buff": 0, "stroke_width": 5, "max_tip_length_to_length_ratio": 0.15}
        mg_vec = Arrow(sled_center, sled_center + DOWN * force_scale * 1.5, color=MY_RED, **arrow_config)
        mg_label = MathTex("m\\vec{g}", font_size=30, color=MY_RED).next_to(mg_vec.get_end(), DOWN, buff=0.1)
        N_vec_dir = rotate_vector(UP, slope_angle)
        N_mag_visual = force_scale * np.cos(slope_angle) * 1.5
        N_vec = Arrow(sled_center, sled_center + N_vec_dir * N_mag_visual, color=MY_BLUE, **arrow_config)
        N_label = MathTex("\\vec{N}", font_size=30, color=MY_BLUE).next_to(N_vec.get_end(), N_vec_dir, buff=0.1)
        f_vec_dir = rotate_vector(LEFT, slope_angle)
        f_mag_visual = force_scale * 0.3
        f_vec = Arrow(sled_center, sled_center + f_vec_dir * f_mag_visual, color=MY_ORANGE, **arrow_config)
        f_label = MathTex("\\vec{f}", font_size=30, color=MY_ORANGE).next_to(f_vec.get_end(), f_vec_dir, buff=0.1)
        T_vec_dir = f_vec_dir
        T_mag_visual = force_scale * 1.0
        T_start = sled.get_corner(UL) + f_vec_dir * 0.1
        T_vec = Arrow(T_start, T_start + T_vec_dir * T_mag_visual, color=MY_GREEN, **arrow_config)
        T_label = MathTex("\\vec{T}", font_size=30, color=MY_GREEN).next_to(T_vec.get_end(), T_vec_dir, buff=0.1)
        mg_end = mg_vec.get_end()
        mg_par_dir = rotate_vector(RIGHT, slope_angle)
        mg_par_mag = force_scale * 1.5 * np.sin(slope_angle)
        mg_par_end = sled_center + mg_par_dir * mg_par_mag
        mg_par_vec = Arrow(sled_center, mg_par_end, color=MY_PURPLE, **arrow_config, stroke_opacity=0.7)
        mg_par_label = MathTex("mg\\sin\\theta", font_size=28, color=MY_PURPLE).next_to(mg_par_vec.get_end(), mg_par_dir, buff=0.1)
        mg_perp_dir = rotate_vector(DOWN, slope_angle)
        mg_perp_mag = force_scale * 1.5 * np.cos(slope_angle)
        mg_perp_end = sled_center + mg_perp_dir * mg_perp_mag
        mg_perp_vec = Arrow(sled_center, mg_perp_end, color=MY_PURPLE, **arrow_config, stroke_opacity=0.7)
        mg_perp_label = MathTex("mg\\cos\\theta", font_size=28, color=MY_PURPLE).next_to(mg_perp_vec.get_end(), mg_perp_dir*1.2 + LEFT*0.1, buff=0.05)
        dashed_line1 = DashedLine(mg_end, mg_par_end, color=MY_PURPLE, stroke_opacity=0.7)
        dashed_line2 = DashedLine(mg_end, mg_perp_end, color=MY_PURPLE, stroke_opacity=0.7)
        forces = VGroup(mg_vec, mg_label, N_vec, N_label, f_vec, f_label, T_vec, T_label)
        decomp_group = VGroup(mg_par_vec, mg_par_label, mg_perp_vec, mg_perp_label, dashed_line1, dashed_line2)
        voice_text_02 = "首先，我们进行受力分析。选择沿斜面向下为x轴正方向，垂直斜面向上为y轴正方向。雪橇受到竖直向下的重力mg，垂直斜面向上的支持力N，沿斜面向上的摩擦力f（与运动方向相反），以及沿斜面向上的绳子拉力T。为了方便计算，我们将重力分解为沿斜面向下的分力mg sin theta 和垂直斜面向下的分力mg cos theta。"
        with custom_voiceover_tts(voice_text_02) as tracker:
            if tracker.audio_path and tracker.duration > 0: self.add_sound(tracker.audio_path, time_offset=0)
            else: print("Warning: Audio file not available or invalid for Scene 2.")
            subtitle_voice = Text(voice_text_02, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)
            self.play(AnimationGroup(FadeIn(subtitle_voice, run_time=0.5), FadeIn(title2, shift=DOWN*0.2), Create(diagram_group), lag_ratio=0.0), run_time=1.5)
            self.play(Create(coord_sys), run_time=1.5)
            self.play(Create(mg_vec), Write(mg_label), run_time=1.0)
            self.play(Create(N_vec), Write(N_label), run_time=1.0)
            self.play(Create(f_vec), Write(f_label), run_time=1.0)
            self.play(Create(T_vec), Write(T_label), run_time=1.0)
            self.play(FadeOut(mg_vec, mg_label, run_time=0.5), AnimationGroup(Create(mg_par_vec), Write(mg_par_label), Create(mg_perp_vec), Write(mg_perp_label), Create(dashed_line1), Create(dashed_line2), lag_ratio=0.1), run_time=2.5)
            total_anim_time = 1.5 + 1.5 + 1.0*4 + 2.5
            subtitle_fadeout_time = 1.0
            if tracker.duration > 0:
                remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
                if remaining_wait > 0: self.wait(remaining_wait)
            else: self.wait(2.0)
            self.play(FadeOut(subtitle_voice), run_time=subtitle_fadeout_time)
        self.wait(1)

    # ==========================================================================
    # Scene 3: Applying Laws (Unchanged)
    # ==========================================================================
    def play_scene_03(self):
        # This scene does not contain mixed text/math issues, code remains the same
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        bg3 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_LIGHT_GRAY, fill_opacity=1, stroke_width=0)
        bg3.set_z_index(-10)
        scene_num_03 = self.get_scene_number("03")
        self.add(bg3, scene_num_03)
        left_col_pos = LEFT * (config.frame_width / 4) + UP * 1.5
        right_col_pos = RIGHT * (config.frame_width / 4) + UP * 1.5
        title3_left = Text("2. 依据“恒速运动”计算力值", font_size=32, color=MY_BLACK)
        title3_left.move_to(left_col_pos + UP * 1.5)
        condition_text = Text("雪橇 恒速 下滑 ⇒ 加速度 a=0，\n沿斜面方向合力为零。", font_size=26, color=MY_BLACK, line_spacing=0.8)
        condition_text.next_to(title3_left, DOWN, buff=0.4).align_to(title3_left, LEFT)
        eq_x_sum = MathTex("\\sum F_x = mg\\sin\\theta - f - T = 0", font_size=30, color=MY_BLACK)
        eq_x_sum.next_to(condition_text, DOWN, buff=0.4).align_to(condition_text, LEFT)
        eq_T_deriv1 = MathTex("T = mg\\sin\\theta - f", font_size=30, color=MY_BLACK)
        eq_T_deriv1.next_to(eq_x_sum, DOWN, buff=0.4).align_to(eq_x_sum, LEFT)
        eq_f = MathTex("f = \\mu N", font_size=30, color=MY_BLACK)
        eq_f.next_to(eq_T_deriv1, DOWN, buff=0.4).align_to(eq_T_deriv1, LEFT)
        eq_y_sum = MathTex("\\sum F_y = N - mg\\cos\\theta = 0", font_size=30, color=MY_BLACK)
        eq_y_sum.next_to(eq_f, DOWN, buff=0.4).align_to(eq_f, LEFT)
        eq_N = MathTex("N = mg\\cos\\theta", font_size=30, color=MY_BLACK)
        eq_N.next_to(eq_y_sum, DOWN, buff=0.2).align_to(eq_y_sum, LEFT).shift(RIGHT*0.5)
        eq_f_sub = MathTex("f = \\mu (mg\\cos\\theta)", font_size=30, color=MY_BLACK)
        eq_f_sub.next_to(eq_N, DOWN, buff=0.4).align_to(eq_f, LEFT)
        eq_T_final = MathTex("T = mg\\sin\\theta - \\mu mg\\cos\\theta", font_size=30, color=MY_BLACK)
        eq_T_final2 = MathTex("T = mg(\\sin\\theta - \\mu\\cos\\theta)", font_size=30, color=MY_BLACK)
        eq_T_final.next_to(eq_f_sub, DOWN, buff=0.4).align_to(eq_T_deriv1, LEFT)
        eq_T_final2.next_to(eq_T_final, DOWN, buff=0.2).align_to(eq_T_final, LEFT)
        left_group = VGroup(title3_left, condition_text, eq_x_sum, eq_T_deriv1, eq_f, eq_y_sum, eq_N, eq_f_sub, eq_T_final, eq_T_final2)
        title3_right = Text("力的数值计算 (g=9.8 m/s²)", font_size=32, color=MY_BLACK)
        title3_right.move_to(right_col_pos + UP * 1.5)
        calc_N = MathTex("N = mg\\cos60^\\circ = (90.0)(9.8)(0.5) = 441.0\\ \\text{N}", font_size=28, color=MY_BLACK)
        calc_N.next_to(title3_right, DOWN, buff=0.4).align_to(title3_right, LEFT)
        calc_f = MathTex("f = \\mu N = (0.100)(441.0) = 44.1\\ \\text{N}", font_size=28, color=MY_BLACK)
        calc_f.next_to(calc_N, DOWN, buff=0.4).align_to(calc_N, LEFT)
        calc_mgsin_implied = MathTex("mg\\sin\\theta \\approx 762.9 \\text{ N}", font_size=28, color=MY_BLACK)
        calc_mgsin_implied.next_to(calc_f, DOWN, buff=0.4).align_to(calc_f, LEFT)
        calc_T = MathTex("T = mg\\sin\\theta - f \\approx 762.9 - 44.1 = 718.8\\ \\text{N}", font_size=28, color=MY_BLACK)
        calc_T.next_to(calc_mgsin_implied, DOWN, buff=0.4).align_to(calc_mgsin_implied, LEFT)
        right_group = VGroup(title3_right, calc_N, calc_f, calc_mgsin_implied, calc_T)
        voice_text_03 = "由于雪橇是恒速下滑，其加速度为零。根据牛顿第二定律，沿斜面方向的合力为零。也就是 mg sin theta 减去 f 再减去 T 等于 0。由此可得 T 等于 mg sin theta 减去 f。同时，摩擦力 f 等于摩擦系数 mu 乘以支持力 N。在垂直斜面方向，合力也为零，即 N 减去 mg cos theta 等于 0，所以 N 等于 mg cos theta。将这些代入，我们得到 T 的表达式。现在，代入数值：m=90kg, g=9.8m/s², theta=60度, mu=0.1。我们计算出支持力N约为441牛顿，摩擦力f约为44.1牛顿，绳子拉力T约为719牛顿。"
        with custom_voiceover_tts(voice_text_03) as tracker:
            if tracker.audio_path and tracker.duration > 0: self.add_sound(tracker.audio_path, time_offset=0)
            else: print("Warning: Audio file not available or invalid for Scene 3.")
            subtitle_voice = Text(voice_text_03, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)
            self.play(AnimationGroup(FadeIn(subtitle_voice, run_time=0.5), Write(title3_left), FadeIn(title3_right), lag_ratio=0.0), run_time=1.5)
            self.play(FadeIn(condition_text), run_time=1.5)
            self.play(Write(eq_x_sum), run_time=1.5)
            self.play(Write(eq_T_deriv1), run_time=1.0)
            self.play(Write(eq_f), run_time=1.0)
            self.play(Write(eq_y_sum), run_time=1.5)
            self.play(Write(eq_N), run_time=1.0)
            self.play(ReplacementTransform(eq_f.copy(), eq_f_sub), run_time=1.5)
            self.play(ReplacementTransform(eq_T_deriv1.copy(), eq_T_final), run_time=1.5)
            self.play(Write(eq_T_final2), run_time=1.0)
            calc_anims = []
            results_to_highlight = [calc_N, calc_f, calc_T]
            items_to_animate = [calc_N, calc_f, calc_mgsin_implied, calc_T]
            for i, item in enumerate(items_to_animate):
                 anim = FadeIn(item, shift=RIGHT*0.2)
                 calc_anims.append(anim)
                 if item in results_to_highlight and isinstance(item, VMobject):
                     target_for_rect = item
                     rect = SurroundingRectangle(target_for_rect, buff=0.05, color=MY_GOLD)
                     highlight_anim = Succession(Create(rect, run_time=0.4), FadeOut(rect, run_time=0.6))
                     calc_anims.append(highlight_anim)
            total_highlight_time = sum(1.0 for item in items_to_animate if item in results_to_highlight)
            total_fadein_time = len(items_to_animate) * 0.3
            right_col_run_time = max(2.0, total_highlight_time + total_fadein_time)
            self.play(LaggedStart(*calc_anims, lag_ratio=0.3), run_time=right_col_run_time)
            total_anim_time = 1.5 + 1.5 + 1.5 + 1.0 + 1.0 + 1.5 + 1.0 + 1.5 + 1.5 + 1.0 + right_col_run_time
            subtitle_fadeout_time = 1.0
            if tracker.duration > 0:
                remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
                if remaining_wait > 0: self.wait(remaining_wait)
            else: self.wait(2.0)
            self.play(FadeOut(subtitle_voice), run_time=subtitle_fadeout_time)
        self.wait(1)

    # ==========================================================================
    # Scene 4: Calculating Work Done
    # ==========================================================================
    def play_scene_04(self):
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        bg4 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_LIGHT_GRAY, fill_opacity=1, stroke_width=0)
        bg4.set_z_index(-10)
        scene_num_04 = self.get_scene_number("04")
        self.add(bg4, scene_num_04)

        title4 = Text("3. 计算各力所做的功", font_size=36, color=MY_BLACK)
        title4.to_edge(UP, buff=0.8)

        work_formula = MathTex("W = F d \\cos\\phi", font_size=32, color=MY_BLACK)
        work_desc = Text("其中 ϕ 是力 F 与位移 d 的夹角, d = 30.0 m (沿斜面向下)", font_size=24, color=MY_DARK_BLUE)
        work_formula_group = VGroup(work_formula, work_desc).arrange(DOWN, buff=0.2)
        work_formula_group.next_to(title4, DOWN, buff=0.5)

        calc_start_y = work_formula_group.get_bottom()[1] - 0.8
        calc_style = {"font_size": 28, "color": MY_BLACK}
        result_style_neg = {"font_size": 30, "color": MY_RED}
        result_style_pos = {"font_size": 30, "color": MY_GREEN}
        title_style = {"font_size": 30, "color": MY_BLACK, "weight": BOLD}
        base_math_style = {"font_size": calc_style["font_size"], "color": calc_style["color"]}
        sub_text_style = {"font_size": calc_style["font_size"], "color": calc_style["color"]}

        # (a) Friction Work
        title_a = Text("(a) 摩擦力做的功:", **title_style)
        title_a.move_to(LEFT * 5 + UP * (calc_start_y/1.5) ).align_to(title_a, LEFT)
        desc_a = Text("f = 44.1 N, d = 30.0 m, ϕ = 180°", **calc_style)
        desc_a.next_to(title_a, DOWN, buff=0.2, aligned_edge=LEFT)
        # Create W_friction using helper
        w_friction_sym = create_symbol_with_text_subscript("W", "摩擦", base_math_style, sub_text_style)
        calc_a_rhs = MathTex("= f d \\cos 180^\\circ = (44.1)(30.0)(-1)", **calc_style)
        calc_a = VGroup(w_friction_sym, calc_a_rhs).arrange(RIGHT, buff=0.15).next_to(desc_a, DOWN, buff=0.2, aligned_edge=LEFT)
        result_a = MathTex("= -1323\\ \\text{J} \\approx -1.32 \\times 10^3\\ \\text{J}", **result_style_neg)
        result_a.next_to(calc_a, DOWN, buff=0.2, aligned_edge=LEFT)
        group_a = VGroup(title_a, desc_a, calc_a, result_a)

        # (b) Rope Work
        title_b = Text("(b) 绳子拉力做的功:", **title_style)
        title_b.next_to(group_a, DOWN, buff=0.6, aligned_edge=LEFT)
        desc_b = Text("T = 718.8 N, d = 30.0 m, ϕ = 180°", **calc_style)
        desc_b.next_to(title_b, DOWN, buff=0.2, aligned_edge=LEFT)
        w_rope_sym = create_symbol_with_text_subscript("W", "绳子", base_math_style, sub_text_style)
        calc_b_rhs = MathTex("= T d \\cos 180^\\circ = (718.8)(30.0)(-1)", **calc_style)
        calc_b = VGroup(w_rope_sym, calc_b_rhs).arrange(RIGHT, buff=0.15).next_to(desc_b, DOWN, buff=0.2, aligned_edge=LEFT)
        result_b = MathTex("= -21564\\ \\text{J} \\approx -2.16 \\times 10^4\\ \\text{J}", **result_style_neg)
        result_b.next_to(calc_b, DOWN, buff=0.2, aligned_edge=LEFT)
        group_b = VGroup(title_b, desc_b, calc_b, result_b)

        # (c) Gravity Work
        title_c = Text("(c) 重力做的功:", **title_style)
        title_c.move_to(RIGHT * 1.5 + UP * (calc_start_y/1.5)).align_to(title_c, LEFT)
        desc_c = Text("力为 mgsinθ ≈ 762.9 N, d = 30.0 m, ϕ = 0°", **calc_style)
        desc_c.next_to(title_c, DOWN, buff=0.2, aligned_edge=LEFT)
        w_gravity_sym = create_symbol_with_text_subscript("W", "重力", base_math_style, sub_text_style)
        calc_c_rhs = MathTex("= (mg\\sin\\theta) d \\cos 0^\\circ = (762.9)(30.0)(1)", **calc_style)
        calc_c = VGroup(w_gravity_sym, calc_c_rhs).arrange(RIGHT, buff=0.15).next_to(desc_c, DOWN, buff=0.2, aligned_edge=LEFT)
        result_c = MathTex("= 22887\\ \\text{J} \\approx 2.29 \\times 10^4\\ \\text{J}", **result_style_pos)
        result_c.next_to(calc_c, DOWN, buff=0.2, aligned_edge=LEFT)
        group_c = VGroup(title_c, desc_c, calc_c, result_c)

        # --- Voiceover and Animation (Code unchanged) ---
        voice_text_04 = "接下来，我们计算各个力所做的功。功的计算公式为 W 等于 F 乘以 d 乘以 cos phi，其中 phi 是力 F 与位移 d 之间的夹角。位移 d 是沿斜面向下30米。(a) 摩擦力 f 方向沿斜面向上，与位移夹角为180度，所以摩擦力做负功，约为负1320焦耳。(b) 绳子拉力 T 方向沿斜面向上，与位移夹角也为180度，所以绳子拉力也做负功，约为负21600焦耳。(c) 重力做的功，可以看作是重力沿斜面的分力 mg sin theta 做的功。该分力方向沿斜面向下，与位移夹角为0度，所以重力做正功，约为22900焦耳。"
        with custom_voiceover_tts(voice_text_04) as tracker:
            if tracker.audio_path and tracker.duration > 0: self.add_sound(tracker.audio_path, time_offset=0)
            else: print("Warning: Audio file not available or invalid for Scene 4.")
            subtitle_voice = Text(voice_text_04, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)
            self.play(AnimationGroup(FadeIn(subtitle_voice, run_time=0.5), Write(title4), FadeIn(work_formula_group), lag_ratio=0.0), run_time=2.0)
            self.play(LaggedStartMap(FadeIn, group_a, shift=UP*0.2, lag_ratio=0.2), run_time=2.5)
            self.wait(0.5)
            self.play(LaggedStartMap(FadeIn, group_b, shift=UP*0.2, lag_ratio=0.2), run_time=2.5)
            self.wait(0.5)
            self.play(LaggedStartMap(FadeIn, group_c, shift=UP*0.2, lag_ratio=0.2), run_time=2.5)
            total_anim_time = 2.0 + 2.5 + 0.5 + 2.5 + 0.5 + 2.5
            subtitle_fadeout_time = 1.0
            if tracker.duration > 0:
                remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
                if remaining_wait > 0: self.wait(remaining_wait)
            else: self.wait(2.0)
            self.play(FadeOut(subtitle_voice), run_time=subtitle_fadeout_time)
        self.wait(1)

    # ==========================================================================
    # Scene 5: Total Work and Conclusion
    # ==========================================================================
    def play_scene_05(self):
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        bg5 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_DARK_BG, fill_opacity=1, stroke_width=0)
        bg5.set_z_index(-10)
        scene_num_05 = self.get_scene_number("05")
        scene_num_05.set_color(MY_WHITE)
        self.add(bg5, scene_num_05)

        text_color = MY_WHITE
        title_style = {"font_size": 34, "color": text_color, "weight": BOLD}
        subtitle_style = {"font_size": 28, "color": text_color}
        math_style = {"font_size": 30, "color": text_color}
        result_style = {"font_size": 32, "color": MY_GOLD}
        desc_style = {"font_size": 26, "color": text_color, "line_spacing": 0.8}
        base_math_style = {"font_size": math_style["font_size"], "color": math_style["color"]}
        sub_text_style = {"font_size": math_style["font_size"], "color": math_style["color"]}


        # --- (d) Total Work Calculation ---
        title_d = Text("(d) 总功计算", **title_style)
        title_d.to_edge(UP, buff=1.0).shift(LEFT*4)

        # Method 1: Summation
        method1_title = Text("方法一：直接求和", **subtitle_style)
        method1_title.next_to(title_d, DOWN, buff=0.4, aligned_edge=LEFT)
        # Create symbols using helper
        w_total_sym1 = create_symbol_with_text_subscript("W", "总", base_math_style, sub_text_style)
        w_grav_sym = create_symbol_with_text_subscript("W", "重力", base_math_style, sub_text_style)
        w_fric_sym = create_symbol_with_text_subscript("W", "摩擦", base_math_style, sub_text_style)
        w_rope_sym = create_symbol_with_text_subscript("W", "绳子", base_math_style, sub_text_style)
        eq_sum1_rhs = VGroup(w_grav_sym, MathTex("+", **math_style), w_fric_sym, MathTex("+", **math_style), w_rope_sym).arrange(RIGHT, buff=0.15)
        eq_sum1 = VGroup(w_total_sym1, MathTex("=", **math_style), eq_sum1_rhs).arrange(RIGHT, buff=0.15)
        eq_sum1.next_to(method1_title, DOWN, buff=0.3, aligned_edge=LEFT)

        w_total_sym2 = create_symbol_with_text_subscript("W", "总", base_math_style, sub_text_style)
        eq_sum2_rhs = MathTex("\\approx (22887) + (-1323) + (-21564)\\ \\text{J}", **math_style)
        eq_sum2 = VGroup(w_total_sym2, eq_sum2_rhs).arrange(RIGHT, buff=0.15)
        eq_sum2.next_to(eq_sum1, DOWN, buff=0.3, aligned_edge=LEFT)

        w_total_sym3 = create_symbol_with_text_subscript("W", "总", base_math_style, sub_text_style)
        result_sum_rhs = MathTex("= 0\\ \\text{J}", **result_style)
        result_sum = VGroup(w_total_sym3, result_sum_rhs).arrange(RIGHT, buff=0.15)
        result_sum.next_to(eq_sum2, DOWN, buff=0.3, aligned_edge=LEFT)
        group_d1 = VGroup(method1_title, eq_sum1, eq_sum2, result_sum)

        # Method 2: Work-Energy Theorem
        method2_title = Text("方法二：功能关系", **subtitle_style)
        method2_title.next_to(result_sum, DOWN, buff=0.6, aligned_edge=LEFT)
        desc2_line1 = Text("由于雪橇 恒速 运动，动能变化 ΔE<0xE2><0x82><0x96> = 0。", **desc_style)
        w_total_sym4 = create_symbol_with_text_subscript("W", "总", {"font_size": desc_style["font_size"]+2, "color": text_color}, {"font_size": desc_style["font_size"]+2, "color": text_color})
        desc2_line2 = VGroup(
             Text("根据动能定理 ", **desc_style),
             w_total_sym4, # Use the created symbol
             MathTex("= \\Delta E_k", font_size=desc_style["font_size"]+2, color=text_color),
             Text("，可知：", **desc_style)
        ).arrange(RIGHT, buff=0.1)
        desc2 = VGroup(desc2_line1, desc2_line2).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        desc2.next_to(method2_title, DOWN, buff=0.3, aligned_edge=LEFT)

        w_total_sym5 = create_symbol_with_text_subscript("W", "总", result_style, result_style)
        result_we_rhs = MathTex("= 0\\ \\text{J}", **result_style)
        result_we = VGroup(w_total_sym5, result_we_rhs).arrange(RIGHT, buff=0.15)
        result_we.next_to(desc2, DOWN, buff=0.3, aligned_edge=LEFT)
        group_d2 = VGroup(method2_title, desc2, result_we)

        group_d = VGroup(title_d, group_d1, group_d2).move_to(LEFT * 3)

        # --- Final Answer Summary ---
        final_title = Text("最终答案", font_size=36, color=MY_GOLD, weight=BOLD)
        final_title.to_edge(RIGHT, buff=2.0).align_to(title_d, UP)

        final_answers_data = [
            {"text": "(a) 摩擦力做的功: ", "base": "W", "sub": "摩擦", "result": "\\approx -1.32 \\times 10^3\\ \\text{J}"},
            {"text": "(b) 绳子做的功: ", "base": "W", "sub": "绳子", "result": "\\approx -2.16 \\times 10^4\\ \\text{J}"},
            {"text": "(c) 重力做的功: ", "base": "W", "sub": "重力", "result": "\\approx 2.29 \\times 10^4\\ \\text{J}"},
            {"text": "(d) 总功: ", "base": "W", "sub": "总", "result": "= 0\\ \\text{J}"},
        ]
        final_list_group = VGroup()
        item_font_size = 30
        line_buff = 0.4
        final_text_style = {"font_size": item_font_size, "color": text_color}
        final_base_math_style = {"font_size": item_font_size, "color": text_color}
        final_sub_text_style = {"font_size": item_font_size, "color": text_color}
        final_result_math_style = {"font_size": item_font_size, "color": text_color}

        for item_data in final_answers_data:
            text_part = Text(item_data["text"], **final_text_style)
            symbol_part = create_symbol_with_text_subscript(
                item_data["base"], item_data["sub"],
                final_base_math_style, final_sub_text_style
            )
            result_part = MathTex(item_data["result"], **final_result_math_style)
            line = VGroup(text_part, symbol_part, result_part).arrange(RIGHT, buff=0.15, aligned_edge=DOWN) # Align baseline
            final_list_group.add(line)

        final_list_group.arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
        final_list_group.next_to(final_title, DOWN, buff=0.5).align_to(final_title, LEFT)

        final_group = VGroup(final_title, final_list_group)

        # --- Voiceover and Animation (Code unchanged) ---
        voice_text_05 = "最后，我们计算总功。(d) 总功 W_total 是所有力做功的代数和。将重力、摩擦力、绳子拉力做的功相加，我们得到 W_total 约等于 22900 减 1320 减 21600，结果为 0 焦耳。这与动能定理一致：因为雪橇是恒速运动，动能变化为零，所以合外力做的总功也必须为零。总结一下最终答案：摩擦力做功约为负1.32乘以10的三次方焦耳，绳子做功约为负2.16乘以10的四次方焦耳，重力做功约为2.29乘以10的四次方焦耳，总功为零。"
        with custom_voiceover_tts(voice_text_05) as tracker:
            if tracker.audio_path and tracker.duration > 0: self.add_sound(tracker.audio_path, time_offset=0)
            else: print("Warning: Audio file not available or invalid for Scene 5.")
            subtitle_voice = Text(voice_text_05, font_size=28, color=MY_WHITE, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)
            self.play(AnimationGroup(FadeIn(subtitle_voice, run_time=0.5), FadeIn(title_d), lag_ratio=0.0), run_time=1.0)
            self.play(Write(method1_title), run_time=0.8)
            self.play(Write(eq_sum1), run_time=1.2)
            self.play(Write(eq_sum2), run_time=1.5)
            self.play(Write(result_sum), run_time=1.0)
            self.wait(0.5)
            self.play(Write(method2_title), run_time=0.8)
            self.play(FadeIn(desc2), run_time=1.5)
            self.play(Write(result_we), run_time=1.0)
            self.play(Write(final_title), run_time=1.0)
            self.play(LaggedStartMap(FadeIn, final_list_group, shift=RIGHT*0.1, lag_ratio=0.3), run_time=3.0)
            self.play(self.camera.frame.animate.scale(0.9).move_to(final_list_group.get_center() + UP*0.5), run_time=1.5)
            total_anim_time = 1.0 + 0.8 + 1.2 + 1.5 + 1.0 + 0.5 + 0.8 + 1.5 + 1.0 + 1.0 + 3.0 + 1.5
            subtitle_fadeout_time = 1.0
            if tracker.duration > 0:
                remaining_wait = tracker.duration - total_anim_time - subtitle_fadeout_time
                if remaining_wait > 0: self.wait(remaining_wait)
            else: self.wait(2.0)
            self.play(FadeOut(subtitle_voice), run_time=subtitle_fadeout_time)
        self.wait(2)


# --- Main execution block ---
if __name__ == "__main__":
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 30
    config.output_file = "CombinedScene"
    config.media_dir = "slide"
    config.disable_caching = True

    scene = CombinedScene()
    scene.render()
    print("Scene rendering finished.")
    output_path = os.path.join(config.media_dir, "videos", str(config.pixel_height) + "p" + str(config.frame_rate), f"{config.output_file}.mp4")
    alt_output_path = os.path.join(config.media_dir, f"{config.output_file}.mp4") # Manim CE 0.18+ might use this
    final_path = None
    if os.path.exists(output_path):
        final_path = output_path
    elif os.path.exists(alt_output_path):
         final_path = alt_output_path

    if final_path:
        print(f"Output video generated successfully at: {final_path}")
    else:
        print(f"Error: Output video not found at expected locations:")
        print(f" - {output_path}")
        print(f" - {alt_output_path}")
        print("Please check Manim logs for errors and the exact output location.")