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
        # --- 场景二：切线概念与问题背景介绍 ---
        self.play_scene_02()
        self.clear_and_reset()
        # --- 场景三：切线求解步骤展示 ---
        self.play_scene_03()
        self.clear_and_reset()
        # --- 场景四：理论原理与数学公式解析 ---
        self.play_scene_04()
        self.clear_and_reset()
        # --- 场景五：总结与回顾 ---
        self.play_scene_05()
        self.clear_and_reset()  # 结束前也清理一次

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
        #self.wait(0.5)

    def star_updater(self, star, dt):
        """更新星星透明度，实现闪烁效果"""
        base_opacity = getattr(star, "base_opacity", 0.5)
        frequency = getattr(star, "frequency", 0.5)
        phase = getattr(star, "phase", 0)
        current_time = self.scene_time_tracker.get_value()
        opacity_variation = 0.4 * np.sin(2 * PI * frequency * current_time + phase)
        target_opacity = np.clip(base_opacity + opacity_variation, 0.1, 0.9)
        star.set_opacity(target_opacity)

    def play_voiceover(self, text, font_size=32, wait_time=0.5):
        with custom_voiceover_tts(text) as tracker:
            # 添加音频，确保旁白和动画同步播放
            self.add_sound(tracker.audio_path, time_offset=0)

            # 创建并定位字幕（屏幕底部）
            subtitle = Text(text, font_size=font_size, color=MY_WHITE)
            subtitle.to_edge(DOWN, buff=0.5)

            # 字幕简单淡入显示，保持整个音频时长，然后淡出
            self.play(FadeIn(subtitle), run_time=0.5)
            # 显示字幕的时间为音频时长减去淡入和淡出时间（若时长不足则直接等待）
            display_time = max(tracker.duration - 1.0, 0)
            self.wait(display_time)
            self.play(FadeOut(subtitle), run_time=0.5)
            self.wait(wait_time)

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

    # -----------------------------
    # 场景二：切线概念与问题背景介绍
    # -----------------------------
    # 场景二同步修改
    def play_scene_02(self):
        voice_text = "切线是曲线在某一点的瞬时方向。在函数 f(x)=x^2 中，切线反映了曲线在该点的斜率变化。"

        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=32, color=MY_BLACK,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    FadeIn(self.get_scene_number("02"), run_time=0.5),
                    lag_ratio=0.0
                ),
                run_time=0.5
            )

            animation_duration = 5
            total_used_time = 0.5 + animation_duration + 1

            # 开始场景动画
            self.original_scene_02_animation(animation_duration)

            remaining_time = tracker.duration - total_used_time
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=1)

    def original_scene_02_animation(self, run_time):
        bg2 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=MY_LIGHT_GRAY,
            fill_opacity=1.0,
            stroke_width=0
        )
        bg2.set_z_index(-10)
        self.add(bg2)

        text_left_part1 = Text("切线是曲线在某一点的瞬时方向 📏", font_size=28, color=MY_BLACK)
        text_left_part2 = Text("在函数", font_size=28, color=MY_BLACK)
        text_left_part3 = MathTex("f(x)=x^2", font_size=32, color=MY_DARK_BLUE)
        text_left_part4 = Text("中,", font_size=28, color=MY_BLACK)
        text_left_part5 = Text("切线反映了曲线在该点的斜率变化 📈", font_size=28, color=MY_BLACK)

        line1 = VGroup(text_left_part1).arrange(RIGHT, buff=0.1)
        line2 = VGroup(text_left_part2, text_left_part3, text_left_part4).arrange(RIGHT, buff=0.1)
        line3 = VGroup(text_left_part5).arrange(RIGHT, buff=0.1)
        text_left = VGroup(line1, line2, line3).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        text_left.to_edge(LEFT, buff=1)

        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
            x_length=6,
            y_length=5,
            axis_config={"color": MY_BLACK, "include_tip": True, "include_numbers": True, "stroke_width": 2},
            x_axis_config={"numbers_to_include": np.arange(-3, 4, 1)},
            y_axis_config={"numbers_to_include": np.arange(0, 10, 2)},
        )
        x_label = axes.get_x_axis_label("x", edge=RIGHT, direction=DOWN, buff=0.2)
        y_label = axes.get_y_axis_label("f(x)", edge=UP, direction=LEFT, buff=0.2)
        axes_labels = VGroup(x_label, y_label).set_color(MY_BLACK)

        parabola = axes.plot(lambda x: x ** 2, x_range=[-3, 3], color=MY_DARK_BLUE, stroke_width=3)
        parabola_label_obj = axes.get_graph_label(parabola, label="f(x)=x^2", x_val=-2, direction=UL, buff=0.3)
        parabola_label_obj.set_color(MY_DARK_BLUE)
        parabola_label_obj.set_font_size(24)

        a = 1
        tangent_point_coords = axes.c2p(a, a ** 2)
        tangent_point_dot = Dot(point=tangent_point_coords, color=MY_RED, radius=0.1)

        graph_group = VGroup(axes, axes_labels, parabola, parabola_label_obj, tangent_point_dot)
        graph_group.to_edge(RIGHT, buff=1)
        graph_group.move_to([graph_group.get_center()[0], text_left.get_center()[1], 0])

        self.play(
            AnimationGroup(
                FadeIn(text_left, shift=RIGHT * 0.2),
                Create(graph_group),
                lag_ratio=0.3
            ),
            run_time=run_time
        )

    # -----------------------------
    # 场景三：切线求解步骤展示
    # -----------------------------
    def play_scene_03(self):
        # 创建背景平面
        plane = NumberPlane(
            x_range=[-config.frame_width / 2, config.frame_width / 2, 1],
            y_range=[-config.frame_height / 2, config.frame_height / 2, 1],
            x_length=config.frame_width,
            y_length=config.frame_height,
            background_line_style={
                "stroke_color": MY_MEDIUM_GRAY,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            },
            x_axis_config={"stroke_width": 0},
            y_axis_config={"stroke_width": 0},
        )
        plane.set_z_index(-10)
        bg3 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=MY_LIGHT_GRAY,
            fill_opacity=1.0,
            stroke_width=0
        )
        bg3.set_z_index(-11)
        self.add(bg3, plane)

        # 添加场景编号
        scene_num_03 = self.get_scene_number("03")
        scene_num_03.set_color(MY_BLACK)
        scene_num_03.set_z_index(10)
        self.add(scene_num_03)

        # 显示步骤文本与数学表达式
        step1_text = Text("步骤1: 确定切点 P", font_size=28, color=MY_BLACK)
        step1_math = MathTex("(a, a^2)", font_size=32, color=MY_DARK_BLUE)
        step1 = VGroup(step1_text, step1_math).arrange(RIGHT, buff=0.2)

        step2_text = Text("步骤2: 求导数及切点斜率 k", font_size=28, color=MY_BLACK)
        step2_math = MathTex("f'(x)=2x \\implies k = f'(a)=2a", font_size=32, color=MY_DARK_BLUE)
        step2 = VGroup(step2_text, step2_math).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        step3_text = Text("步骤3: 使用点斜式写出方程", font_size=28, color=MY_BLACK)
        step3_math = MathTex("y - a^2 = 2a(x - a)", font_size=32, color=MY_DARK_BLUE)
        step3 = VGroup(step3_text, step3_math).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        step4_text = Text("步骤4: 整理得切线方程 ✨", font_size=28, color=MY_BLACK)
        step4_math = MathTex("y = 2a(x - a) + a^2", font_size=32, color=MY_DARK_BLUE)
        step4 = VGroup(step4_text, step4_math).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        steps = VGroup(step1, step2, step3, step4).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        steps.to_edge(LEFT, buff=1)

        # 绘制右侧图形：坐标轴、抛物线、切点与切线
        axes_right = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
            x_length=5,
            y_length=4,
            axis_config={"color": MY_BLACK, "include_tip": True, "stroke_width": 2},
            tips=False,
        )
        parabola_right = axes_right.plot(lambda x: x ** 2, x_range=[-3, 3], color=MY_DARK_BLUE, stroke_width=3)
        a_val = 1
        tangent_point_right_coords = axes_right.c2p(a_val, a_val ** 2)
        tangent_point_right_dot = Dot(point=tangent_point_right_coords, color=MY_RED, radius=0.08)
        tangent_line = axes_right.plot(lambda x: 2 * a_val * x - a_val ** 2, x_range=[-1, 3], color=MY_ORANGE,
                                       stroke_width=3)
        tangent_label_obj = MathTex("y = 2x - 1", font_size=24, color=MY_ORANGE)
        tangent_label_obj.next_to(tangent_line.get_end(), UR, buff=0.1)
        graph_group_right = VGroup(axes_right, parabola_right, tangent_point_right_dot, tangent_line, tangent_label_obj)
        graph_group_right.to_edge(RIGHT, buff=1)
        graph_group_right.move_to([graph_group_right.get_center()[0], steps.get_center()[1], 0])


        # 严格同步的旁白与字幕部分
        voice_text = (
            "第一步，确定切点 P，即 (a, a平方)；"
            "第二步，求导数 f的导数等于 2x，故切点处斜率为 2a；"
            "第三步，利用点斜式写出方程：y 减 a平方等于 2a乘以 x 减 a；"
            "第四步，整理得切线方程：y 等于 2a乘以 (x 减 a) 加 a平方。"
        )

        with custom_voiceover_tts(voice_text) as tracker:
            # 播放第一个动画
            self.play(FadeIn(step1[0]), Write(step1[1]), run_time=1)
            self.wait(0.5)

            # 立即启动音频播放
            self.add_sound(tracker.audio_path, time_offset=0)

            # 创建并定位底部字幕
            subtitle_voice = Text(
                voice_text,
                font_size=28,
                width=config.frame_width - 2,
                should_center=True,
            ).to_edge(DOWN, buff=0.5)

            # 同步启动字幕动画，确保字幕与其他动画同时开始
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    FadeIn(self.get_scene_number("03"), run_time=0.5),
                    lag_ratio=0.0
                ),
                run_time=0.5
            )
            # 播放剩余动画
            self.play(FadeIn(step2[0]), Write(step2[1]), run_time=1.5)
            self.wait(0.5)
            self.play(FadeIn(step3[0]), Write(step3[1]), run_time=1.5)
            self.wait(0.5)
            self.play(FadeIn(step4[0]), Write(step4[1]), run_time=1.5)
            self.wait(1)
            self.play(Create(axes_right), Create(parabola_right), run_time=1.5)
            self.play(Create(tangent_point_right_dot), Create(tangent_line), Write(tangent_label_obj), run_time=2)
            self.wait(2)

            # 根据音频时长计算剩余等待时间（预留0.5秒字幕淡入和1秒字幕淡出）
            remaining_time = tracker.duration - 0.5 - 1.0
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

    # -----------------------------
    # 场景四：理论原理与数学公式解析
    # -----------------------------
    def play_scene_04(self):
        bg4 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=[MY_LIGHT_GRAY, MY_MEDIUM_GRAY],
            fill_opacity=1.0,
        )
        bg4.set_fill(color=[MY_LIGHT_GRAY, MY_MEDIUM_GRAY], opacity=1.0)
        bg4.set_z_index(-10)
        self.add(bg4)
        scene_num_04 = self.get_scene_number("04")
        scene_num_04.set_color(MY_BLACK)
        scene_num_04.set_z_index(10)
        self.add(scene_num_04)
        derivative_title = Text("理论基础 1: 导数的定义", font_size=32, color=MY_BLACK)
        derivative_formula = MathTex(
            r"f'(x)=\lim_{h\to0}\frac{f(x+h)-f(x)}{h}", font_size=48, color=MY_DARK_BLUE
        )
        derivative_group = VGroup(derivative_title, derivative_formula).arrange(DOWN, buff=0.4)
        derivative_group.to_edge(UP, buff=1.5)
        lineslope_title = Text("理论基础 2: 点斜式直线方程", font_size=32, color=MY_BLACK)
        lineslope_formula = MathTex(r"y-y_1=m(x-x_1)", font_size=48, color=MY_DARK_BLUE)
        lineslope_group = VGroup(lineslope_title, lineslope_formula).arrange(DOWN, buff=0.4)
        lineslope_group.to_edge(DOWN, buff=1.5)
        arrow = Arrow(
            derivative_formula.get_bottom() + DOWN * 0.2,
            lineslope_formula.get_top() + UP * 0.2,
            buff=0.1,
            color=MY_ORANGE,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.15
        )
        self.play(FadeIn(derivative_title), Write(derivative_formula), run_time=2)
        self.wait(0.5)
        self.play(FadeIn(lineslope_title), Write(lineslope_formula), run_time=2)
        self.wait(0.5)
        self.play(Create(arrow), run_time=1.5)
        self.wait(0.5)
        try:
            f_prime_part = derivative_formula.get_part_by_tex("f'(x)")
            m_part = lineslope_formula.get_part_by_tex("m")
            self.play(
                Indicate(f_prime_part, color=MY_ORANGE, scale_factor=1.2),
                Indicate(m_part, color=MY_ORANGE, scale_factor=1.2),
                run_time=2
            )
        except Exception as e:
            print(f"Warning: {e}")
            self.play(
                Indicate(derivative_formula, color=MY_ORANGE, scale_factor=1.1),
                Indicate(lineslope_formula, color=MY_ORANGE, scale_factor=1.1),
                run_time=2
            )
        self.wait(2)
        # 添加旁白与字幕：理论原理解析
        voice_text = (
            "导数的定义为 f 的导数等于极限，当 h 趋近于零时，"
            "分子为 f(x+h) 减去 f(x)，除以 h；"
            "点斜式直线方程为 y 减 y1 等于 m 乘以 (x 减 x1)。"
        )
        self.play_voiceover(voice_text, font_size=28)

    # -----------------------------
    # 场景五：总结与回顾
    # -----------------------------
    def play_scene_05(self):
        bg5 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=[MY_DARK_BLUE, MY_BLACK],
            fill_opacity=1.0,
        )
        bg5.set_fill(color=[MY_DARK_BLUE, MY_BLACK], opacity=1.0)
        bg5.set_z_index(-10)
        self.add(bg5)
        scene_num_05 = self.get_scene_number("05")
        scene_num_05.set_color(MY_WHITE)
        scene_num_05.set_z_index(10)
        self.add(scene_num_05)
        summary_title = Text("总结 🏆", font_size=60, color=MY_GOLD)
        summary_title.to_edge(UP, buff=1.0)
        point_label = Text("切点 P: ", font_size=40, color=MY_WHITE)
        point_formula = MathTex("(a, a^2)", font_size=40, color=MY_WHITE)
        point_group = VGroup(point_label, point_formula).arrange(RIGHT, buff=0.2)
        derivative_label = Text("导数/斜率 k: ", font_size=40, color=MY_WHITE)
        derivative_formula = MathTex("f'(x)=2x \\implies k=2a", font_size=40, color=MY_WHITE)
        derivative_group = VGroup(derivative_label, derivative_formula).arrange(RIGHT, buff=0.2)
        tangent_eq_label = Text("切线方程: ", font_size=40, color=MY_WHITE)
        tangent_eq_formula = MathTex("y = 2a(x - a) + a^2", font_size=40, color=MY_WHITE)
        tangent_eq_group = VGroup(tangent_eq_label, tangent_eq_formula).arrange(RIGHT, buff=0.2)
        formulas = VGroup(point_group, derivative_group, tangent_eq_group).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        formulas.next_to(summary_title, DOWN, buff=0.8)
        question = Text(
            "你认为切线方程还能帮助我们解决哪些类型的问题？🤔💡",
            font_size=32,
            color=MY_LIGHT_GRAY,
            t2c={"切线方程": MY_ORANGE, "解决": MY_ORANGE}
        )
        question.to_edge(DOWN, buff=1.0)
        self.play(FadeIn(summary_title, scale=0.8), run_time=1.5)
        self.wait(0.5)
        self.play(FadeIn(point_group[0]), Write(point_group[1]), run_time=1.5)
        self.wait(0.3)
        self.play(FadeIn(derivative_group[0]), Write(derivative_group[1]), run_time=1.5)
        self.wait(0.3)
        self.play(FadeIn(tangent_eq_group[0]), Write(tangent_eq_group[1]), run_time=1.5)
        self.wait(1)
        self.play(FadeIn(question, shift=UP * 0.3), run_time=1.5)
        self.wait(1)
        summary_group = VGroup(summary_title, formulas)
        self.play(self.camera.frame.animate.scale(0.9).move_to(summary_group.get_center()), run_time=2)
        self.wait(3)
        # 添加旁白与字幕：总结回顾
        voice_text = (
            "总结一下，切点为 (a, a平方)，导数 f 的导数等于 2x，"
            "因此切点处斜率为 2a，切线方程为 y 等于 2a乘以 (x 减 a) 加 a平方。"
            "你认为切线方程还能帮助我们解决哪些问题？"
        )
        self.play_voiceover(voice_text, font_size=28)


# --- Main execution block ---
if __name__ == "__main__":
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 30
    config.output_file = "CombinedScene"
    config.media_dir = "05"
    config.disable_caching = True
    scene = CombinedScene()
    scene.render()
    print("Scene rendering finished.")
