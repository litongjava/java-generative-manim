# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
from moviepy import AudioFileClip # Correct import for AudioFileClip
import hashlib
import manimpango # For font checking

# --- 自定义颜色 ---
MY_DARK_BLUE = "#000033"  # 深蓝 (场景0, 4 背景)
MY_LIGHT_BLUE = "#6495ED" # 浅蓝 (场景0, 4 背景)
MY_VERY_LIGHT_BLUE = "#E0F2F7" # 极浅蓝 (场景3 背景)
MY_LIGHT_GRAY = "#EEEEEE"  # 浅灰色 (场景1, 2 背景)
MY_DARK_GRAY = "#333333"   # 深灰色 (文本)
MY_WHITE = "#FFFFFF"      # 白色 (标题, 文本)
MY_YELLOW = "#FFFFE0"     # 淡黄色 (副标题, 总结)
MY_BLUE = "#007BFF"       # 蓝色 (图形线条)
MY_LIGHT_BLUE_FILL = "#ADD8E6" # 浅蓝填充 (图形面积)
MY_RED = "#FF0000"         # 红色 (设计过程线)
MY_ORANGE = "#FFA500"      # 橙色 (备选设计过程线颜色)
MY_BLACK = "#000000"       # 黑色 (文本)

# --- TTS 配置 ---
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
    audio_file = None
    duration = 0

    try:
        if os.path.exists(cache_file):
            audio_file = cache_file
        else:
            input_text = requests.utils.quote(text)
            url = f"{base_url}?token={token}&input={input_text}"

            response = requests.get(url, stream=True)
            if response.status_code != 200:
                print(f"警告: TTS 接口错误: {response.status_code} - {response.text}")
                # 提供一个虚拟的 tracker，避免程序崩溃
                tracker = CustomVoiceoverTracker(None, 0)
                yield tracker
                return # 提前退出 context manager

            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            audio_file = cache_file

        # 确保文件写入完成且非空
        if audio_file and os.path.getsize(audio_file) > 0:
             # 使用 try-except 块处理可能的 MoviePy 错误
            try:
                # 使用 with 语句确保 AudioFileClip 正确关闭
                with AudioFileClip(audio_file) as clip:
                    duration = clip.duration
            except Exception as e:
                 print(f"警告: 无法读取音频文件 '{audio_file}' 获取时长: {e}")
                 duration = 5 # 假设一个默认时长，让动画继续
        else:
            print(f"警告: TTS 未能生成有效的音频文件 '{cache_file}'")
            duration = 5 # 假设一个默认时长

        tracker = CustomVoiceoverTracker(audio_file, duration)
        yield tracker

    except requests.exceptions.RequestException as e:
        print(f"警告: TTS 请求失败: {e}")
        tracker = CustomVoiceoverTracker(None, 0) # 提供虚拟 tracker
        yield tracker
    except Exception as e:
        print(f"警告: 处理 TTS 时发生未知错误: {e}")
        tracker = CustomVoiceoverTracker(None, 0) # 提供虚拟 tracker
        yield tracker
    finally:
        # 通常不在此处清理缓存，以便重用
        pass


# --- 字体检查 ---
DEFAULT_FONT = "Noto Sans CJK SC" # 优先使用 Noto Sans CJK SC
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

# -----------------------------
# CombinedScene：整合所有场景
# -----------------------------
class CombinedScene(MovingCameraScene):
    """
    整合所有场景的 Manim 动画，讲解设计洪水推求方法。
    """
    def setup(self):
        MovingCameraScene.setup(self)
        if final_font:
            # 只为 Text 设置默认字体
            Text.set_default(font=final_font)
            print(f"已将默认字体设置为: {final_font}")
        else:
            print("警告: 未能设置有效的中文字体，将使用 Manim 默认字体。")
        # 初始化场景时间跟踪器
        self.scene_time_tracker = ValueTracker(0)


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
        # 最后场景结束后不需要 clear_and_reset

    def get_scene_number(self, number_str):
        """创建并定位场景编号"""
        scene_num = Text(number_str, font_size=24, color=MY_WHITE)
        scene_num.to_corner(UR, buff=0.5)
        scene_num.set_z_index(10) # 确保在顶层
        return scene_num

    def clear_and_reset(self):
        """清除当前场景所有对象并重置相机"""
        # 停止所有更新器
        for mob in self.mobjects:
            if mob is not None:
                mob.clear_updaters()

        # 创建包含所有有效对象的组
        valid_mobjects = [m for m in self.mobjects if m is not None]
        if valid_mobjects:
            all_mobjects_group = Group(*valid_mobjects)
            # 使用 try-except 避免在空场景中调用 play 出错
            try:
                self.play(FadeOut(all_mobjects_group, shift=DOWN * 0.5), run_time=0.5)
            except Exception:
                 # 如果场景已空，FadeOut 会失败，忽略即可
                 pass


        self.clear() # 清除 Manim 内部列表
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        # 重置场景时间跟踪器
        self.scene_time_tracker.set_value(0)
        self.wait(0.1) # 短暂等待确保清除完成

    def create_gradient_background(self, color1, color2, direction=DOWN):
        """创建渐变背景矩形"""
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=[color1, color2], # 传递颜色列表以创建渐变
            fill_opacity=1.0
        )
        # Manim CE v0.19.0 默认垂直渐变 (DOWN)
        # 如果需要其他方向，需要更复杂的方法，这里假设 DOWN 即可
        bg.set_z_index(-10)
        return bg

    # ==========================================================================
    # 场景 0: 开场与标题
    # ==========================================================================
    def play_scene_00(self):
        self.scene_time_tracker.set_value(0)

        # 背景
        bg0 = self.create_gradient_background(MY_DARK_BLUE, MY_LIGHT_BLUE, DOWN)
        self.add(bg0)

        # 场景编号
        scene_num_00 = self.get_scene_number("00")
        self.add(scene_num_00)

        # 标题
        title = Text("设计洪水推求方法", font_size=60, color=MY_WHITE)
        title.move_to(UP * 1.5)
        subtitle = Text("典型过程线选择与计算步骤", font_size=40, color=MY_YELLOW)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 旁白与动画同步
        voice_text_scene_00 = "大家好！本次视频将为您详解设计洪水的推求方法，重点介绍典型洪水过程线的选择条件以及详细的计算步骤。让我们开始吧！🌊"

        with custom_voiceover_tts(voice_text_scene_00) as tracker:
            if tracker.audio_path:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("警告 [场景00]: 未能加载音频，动画将按预设时间进行。")

            subtitle_voice = Text(
                voice_text_scene_00, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            # 确保字幕背景不透明以提高可读性
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_BLACK, fill_color=MY_BLACK,
                fill_opacity=0.6, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)


            # 动画组：同时进行
            anim_duration_part1 = 1.5
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_group, run_time=0.5),
                    FadeIn(title, shift=UP * 0.2, run_time=anim_duration_part1),
                    lag_ratio=0.0
                ),
                run_time=anim_duration_part1
            )

            anim_duration_part2 = 2.5
            # 使用 FadeIn 替代 Write，更安全
            self.play(FadeIn(subtitle, shift=UP*0.2, run_time=anim_duration_part2))

            # 等待音频播放完毕
            elapsed_time = anim_duration_part1 + anim_duration_part2
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_group), run_time=1.0)

        self.wait(1) # 场景结束停留

    # ==========================================================================
    # 场景 1: 典型洪水过程线的条件
    # ==========================================================================
    def play_scene_01(self):
        self.scene_time_tracker.set_value(0)

        # 背景
        bg1 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_LIGHT_GRAY, fill_opacity=1.0, stroke_width=0)
        bg1.set_z_index(-10)
        self.add(bg1)

        # 场景编号
        scene_num_01 = self.get_scene_number("01")
        scene_num_01.set_color(MY_BLACK) # 在浅色背景上用黑色
        self.add(scene_num_01)

        # 问题文本
        question = Text("1. 由流量资料推求设计洪水选择的典型洪水过程线应具备什么条件？🤔",
                        font_size=36, color=MY_DARK_GRAY)
        question.to_edge(UP, buff=1.0).align_to(LEFT, LEFT).shift(RIGHT*1.0)

        # 答案区域标题
        answer_title = Text("答案要点：", font_size=32, color=MY_BLACK, weight=BOLD)
        answer_title.next_to(question, DOWN, buff=0.8).align_to(question, LEFT)

        # --- 创建答案要点 ---
        points_group = VGroup()
        point_texts = ["峰高量大", "具有代表性", "峰形集中", "洪峰偏后"]
        point_anims = []
        point_elements = [] # 存储每个要点的 VGroup (Text + Graph)

        # 要点1: 峰高量大
        text1 = Text(point_texts[0], font_size=28, color=MY_DARK_GRAY)
        axes1 = Axes(
            x_range=[0, 5, 1], y_range=[0, 7, 1],
            x_length=2.5, y_length=1.8,
            axis_config={"include_numbers": False, "include_tip": False, "color": MY_DARK_GRAY},
            tips=False
        )
        curve1_func = lambda t: 6 * np.exp(-(t - 2.5)**2 / 0.8) # 高峰，面积大
        curve1 = axes1.plot(curve1_func, color=MY_BLUE, stroke_width=3)
        area1 = axes1.get_area(curve1, x_range=(0.5, 4.5), color=[MY_LIGHT_BLUE_FILL, MY_BLUE], opacity=0.5)
        labels1 = axes1.get_axis_labels(x_label=MathTex("T", font_size=20), y_label=MathTex("Q", font_size=20))
        graph1_group = VGroup(axes1, curve1, area1, labels1)
        point1 = VGroup(text1, graph1_group).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        point_elements.append(point1)
        # 动画：文本淡入，图形创建，峰顶指示，面积闪烁
        peak_dot1 = Dot(axes1.input_to_graph_point(2.5, curve1), color=YELLOW) # Pass curve1
        anim1 = AnimationGroup(
            FadeIn(text1),
            Create(axes1), Create(curve1), FadeIn(labels1),
            FadeIn(area1, scale=0.5),
            AnimationGroup(Indicate(peak_dot1, scale_factor=1.5), FadeIn(peak_dot1), lag_ratio=0.5),
            lag_ratio=0.3
        )
        point_anims.append(anim1)

        # 要点2: 代表性
        text2 = Text(point_texts[1], font_size=28, color=MY_DARK_GRAY)
        axes2 = Axes(x_range=[0, 5, 1], y_range=[0, 7, 1], x_length=2.5, y_length=1.8, axis_config={"include_numbers": False, "include_tip": False, "color": MY_DARK_GRAY}, tips=False)
        hist_curves = VGroup()
        for i in range(3):
            func = lambda t: (4 + np.random.uniform(-1, 1)) * np.exp(-(t - (2.5 + np.random.uniform(-0.5, 0.5)))**2 / (1 + np.random.uniform(-0.2, 0.2)))
            hist_curves.add(axes2.plot(func, color=GRAY, stroke_width=1.5))
        typical_curve_func = lambda t: 4.5 * np.exp(-(t - 2.5)**2 / 1.0)
        typical_curve = axes2.plot(typical_curve_func, color=MY_BLUE, stroke_width=3)
        labels2 = axes2.get_axis_labels(x_label=MathTex("T", font_size=20), y_label=MathTex("Q", font_size=20))
        graph2_group = VGroup(axes2, hist_curves, labels2) # Initially show history
        point2 = VGroup(text2, graph2_group).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        point_elements.append(point2)
        # 动画：文本淡入，历史曲线创建，然后替换为典型曲线
        anim2 = AnimationGroup(
            FadeIn(text2),
            Create(axes2), Create(hist_curves), FadeIn(labels2),
            ReplacementTransform(hist_curves, typical_curve),
            lag_ratio=0.3
        )
        point_anims.append(anim2)


        # 要点3: 峰形集中
        text3 = Text(point_texts[2], font_size=28, color=MY_DARK_GRAY)
        axes3 = Axes(x_range=[0, 5, 1], y_range=[0, 7, 1], x_length=2.5, y_length=1.8, axis_config={"include_numbers": False, "include_tip": False, "color": MY_DARK_GRAY}, tips=False)
        curve_sharp_func = lambda t: 6 * np.exp(-(t - 2.5)**2 / 0.4) # 尖峰
        curve_flat_func = lambda t: 3.5 * np.exp(-(t - 2.5)**2 / 1.5) # 平缓峰
        curve_sharp = axes3.plot(curve_sharp_func, color=MY_BLUE, stroke_width=3)
        curve_flat = axes3.plot(curve_flat_func, color=GRAY, stroke_width=2)
        labels3 = axes3.get_axis_labels(x_label=MathTex("T", font_size=20), y_label=MathTex("Q", font_size=20))
        # 指示箭头
        arrow_start = axes3.c2p(1.8, curve_sharp_func(1.8) + 0.5)
        arrow_end = axes3.c2p(2.3, curve_sharp_func(2.3))
        indicator_arrow = Arrow(start=arrow_start, end=arrow_end, color=MY_RED, stroke_width=4, max_tip_length_to_length_ratio=0.15, buff=0.1)
        graph3_group = VGroup(axes3, curve_flat, curve_sharp, labels3)
        point3 = VGroup(text3, graph3_group).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        point_elements.append(point3)
        # 动画：文本淡入，创建图形，指示箭头
        anim3 = AnimationGroup(
            FadeIn(text3),
            Create(axes3), Create(curve_flat), Create(curve_sharp), FadeIn(labels3),
            Create(indicator_arrow),
            lag_ratio=0.3
        )
        point_anims.append(anim3)

        # 要点4: 洪峰偏后
        text4 = Text(point_texts[3], font_size=28, color=MY_DARK_GRAY)
        axes4 = Axes(x_range=[0, 6, 1], y_range=[0, 7, 1], x_length=2.5, y_length=1.8, axis_config={"include_numbers": False, "include_tip": False, "color": MY_DARK_GRAY}, tips=False)
        peak_time = 4.0 # 峰值时间偏后 (中点是 3.0)
        curve4_func = lambda t: 5.5 * np.exp(-(t - peak_time)**2 / 0.9)
        curve4 = axes4.plot(curve4_func, color=MY_BLUE, stroke_width=3)
        labels4 = axes4.get_axis_labels(x_label=MathTex("T", font_size=20), y_label=MathTex("Q", font_size=20))
        # 中心线和指示箭头
        mid_point_x = axes4.x_range[0] + (axes4.x_range[1] - axes4.x_range[0]) / 2
        center_line = DashedLine(axes4.c2p(mid_point_x, 0), axes4.c2p(mid_point_x, 6), color=GRAY, stroke_width=2)
        peak_point_coord = axes4.input_to_graph_point(peak_time, curve4) # Pass curve4
        peak_arrow_start_point = axes4.c2p(mid_point_x + 0.2, 3) # 从中心线右侧一点开始
        peak_arrow = Arrow(start=peak_arrow_start_point, end=peak_point_coord + UP*0.1, color=MY_RED, stroke_width=4, max_tip_length_to_length_ratio=0.15, buff=0.1)
        graph4_group = VGroup(axes4, curve4, labels4, center_line)
        point4 = VGroup(text4, graph4_group).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        point_elements.append(point4)
        # 动画：文本淡入，创建图形，创建箭头 (使用 Create 替代 GrowArrow)
        anim4 = AnimationGroup(
            FadeIn(text4),
            Create(axes4), Create(curve4), FadeIn(labels4), Create(center_line),
            Create(peak_arrow), # 使用 Create 替代 GrowArrow
            lag_ratio=0.3
        )
        point_anims.append(anim4)

        # 排列所有要点
        points_group.add(*point_elements)
        points_group.arrange(RIGHT, buff=1.0)
        points_group.next_to(answer_title, DOWN, buff=0.5).align_to(answer_title, LEFT).shift(RIGHT*0.5) # 整体居中一些

        # --- 旁白与动画 ---
        voice_text_scene_01 = "那么，选择典型洪水过程线需要满足哪些条件呢？主要有四点：一、峰高量大，代表洪水强度和总体积都比较显著；二、具有代表性，能反映流域洪水的一般特性；三、峰形集中，洪水涨落迅速；四、洪峰偏后，峰顶出现在洪水过程的后半段。🧐"

        with custom_voiceover_tts(voice_text_scene_01) as tracker:
            if tracker.audio_path:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("警告 [场景01]: 未能加载音频，动画将按预设时间进行。")

            subtitle_voice = Text(
                voice_text_scene_01, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_BLACK, fill_color=MY_BLACK,
                fill_opacity=0.6, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)

            # 动画序列
            self.play(FadeIn(subtitle_group, run_time=0.5)) # 字幕先出现
            self.play(FadeIn(question), run_time=2.0) # 使用 FadeIn
            self.play(self.camera.frame.animate.shift(DOWN * 1.0).set_run_time(0.5)) # 稍微下移看答案
            self.play(FadeIn(answer_title), run_time=1.0)

            # 逐个展示要点，并配合相机移动和缩放
            total_anim_time = 0
            focus_scale = 1.1
            original_center = self.camera.frame.get_center()
            original_width = self.camera.frame.width

            for i, (anim, element) in enumerate(zip(point_anims, point_elements)):
                target_center = element.get_center()
                # 移动并放大聚焦
                self.play(
                    self.camera.frame.animate.set_width(original_width / focus_scale).move_to(target_center),
                    run_time=0.7
                )
                self.play(anim, run_time=2.5) # 播放当前要点的动画
                total_anim_time += (0.7 + 2.5 + 0.7) # 聚焦+动画+复原
                # 恢复视角
                self.play(
                    self.camera.frame.animate.set_width(original_width).move_to(original_center),
                    run_time=0.7
                )
                self.wait(0.3) # 每个要点间稍作停顿
                total_anim_time += 0.3

            # 等待音频结束
            # 计算已播放动画时间 (粗略估计)
            intro_time = 0.5 + 2.0 + 0.5 + 1.0 # 字幕+问题+移动+标题
            wait_time = max(0, tracker.duration - intro_time - total_anim_time - 1.0) # 减去字幕淡出时间
            if wait_time > 0:
                self.wait(wait_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_group), run_time=1.0)

        self.wait(1.5) # 场景结束停留

    # ==========================================================================
    # 场景 2: 设计洪水计算步骤 - 概述
    # ==========================================================================
    def play_scene_02(self):
        self.scene_time_tracker.set_value(0)

        # 背景
        bg2 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_LIGHT_GRAY, fill_opacity=1.0, stroke_width=0)
        bg2.set_z_index(-10)
        self.add(bg2)

        # 场景编号
        scene_num_02 = self.get_scene_number("02")
        scene_num_02.set_color(MY_BLACK)
        self.add(scene_num_02)

        # 问题文本
        question = Text("2. 试述由流量资料推求设计洪水计算步骤。📝",
                        font_size=36, color=MY_DARK_GRAY)
        question.to_edge(UP, buff=1.0).align_to(LEFT, LEFT).shift(RIGHT*1.0)

        # 步骤标题
        steps_title = Text("计算步骤要点：", font_size=32, color=MY_BLACK, weight=BOLD)
        steps_title.next_to(question, DOWN, buff=0.8).align_to(question, LEFT)

        # --- 手动创建步骤列表 ---
        steps_text = [
            "1. 按年最大值法选样",
            "2. 资料可靠性、一致性、代表性审查",
            "3. 特大洪水频率处理",
            "4. 峰、量频率计算",
            "5. 分析计算安全修正值",
            "6. 查算设计洪峰和设计洪量",
            "7. 频率计算成果合理性检验",
            "8. 选择典型洪水",
            "9. 同倍比或同频率缩放得出设计洪水过程线"
        ]
        steps_list_group = VGroup()
        item_font_size = 28
        bullet_color = MY_BLUE
        text_color = MY_DARK_GRAY
        line_buff = 0.35 # 行间距
        bullet_text_buff = 0.2 # 项目符号和文本间距

        for i, item_text in enumerate(steps_text):
            # 创建编号 (使用 Text) 和文本
            bullet = Text(f"{i+1}.", font_size=item_font_size, color=bullet_color, weight=BOLD)
            # 使用 width 控制长文本自动换行
            text = Text(item_text, font_size=item_font_size, color=text_color,
                        width=config.frame_width * 0.7) # 限制宽度防止超出屏幕
            # 将编号和文本水平排列
            line = VGroup(bullet, text).arrange(RIGHT, buff=bullet_text_buff, aligned_edge=UP) # 顶部对齐
            steps_list_group.add(line)

        # 垂直排列所有行，左对齐
        steps_list_group.arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
        # 定位列表
        steps_list_group.next_to(steps_title, DOWN, buff=0.5).align_to(steps_title, LEFT)

        # --- 旁白与动画 ---
        voice_text_scene_02 = "接下来，我们梳理一下由流量资料推求设计洪水的完整计算步骤。主要包括：一、按年最大值法选样；二、进行资料的三性审查；三、处理特大洪水频率；四、计算洪峰和洪量的频率；五、分析计算安全修正值；六、查算得到设计洪峰和洪量；七、对频率计算成果进行合理性检验；八、选择典型的洪水过程线；最后，九、通过同倍比或同频率缩放，得到最终的设计洪水过程线。🔢"

        with custom_voiceover_tts(voice_text_scene_02) as tracker:
            if tracker.audio_path:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("警告 [场景02]: 未能加载音频，动画将按预设时间进行。")

            subtitle_voice = Text(
                voice_text_scene_02, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_BLACK, fill_color=MY_BLACK,
                fill_opacity=0.6, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)

            # 动画序列
            self.play(FadeIn(subtitle_group, run_time=0.5))
            self.play(FadeIn(question), run_time=2.0) # 使用 FadeIn
            self.play(self.camera.frame.animate.shift(DOWN * 0.8).set_run_time(0.5)) # 下移看列表
            self.play(FadeIn(steps_title), run_time=1.0)

            # 逐条显示列表项
            anims_list = []
            # 估算每项动画时间，确保总时间大致匹配音频（留出前后时间）
            total_list_anim_time = max(5.0, tracker.duration - (0.5 + 2.0 + 0.5 + 1.0 + 1.0 + 2.0)) # 至少5秒，减去其他动画和等待时间
            item_anim_duration = total_list_anim_time / len(steps_list_group)
            lag_ratio_val = 0.8 # 控制列表项出现的间隔

            for item in steps_list_group:
                 # 高亮效果：短暂改变颜色再恢复
                highlight_anim = ApplyMethod(item.set_color, YELLOW_E, rate_func=there_and_back, run_time=item_anim_duration * 0.8)
                fadein_anim = FadeIn(item, shift=RIGHT*0.2, run_time=item_anim_duration * 0.6)
                anims_list.append(AnimationGroup(fadein_anim, highlight_anim, lag_ratio=0.1))


            # 使用 AnimationGroup 和 lag_ratio 播放动画组，使其逐个出现
            self.play(AnimationGroup(*anims_list, lag_ratio=lag_ratio_val), run_time=total_list_anim_time)

            # 等待音频结束
            intro_time = 0.5 + 2.0 + 0.5 + 1.0 # 字幕+问题+移动+标题
            wait_time = max(0, tracker.duration - intro_time - total_list_anim_time - 1.0) # 减去字幕淡出时间
            if wait_time > 0:
                self.wait(wait_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_group), run_time=1.0)

        self.wait(2) # 场景结束停留

    # ==========================================================================
    # 场景 3: 可视化步骤概要 - 频率计算与缩放
    # ==========================================================================
    def play_scene_03(self):
        self.scene_time_tracker.set_value(0)

        # 背景
        bg3 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_VERY_LIGHT_BLUE, fill_opacity=1.0, stroke_width=0)
        bg3.set_z_index(-10)
        self.add(bg3)

        # 场景编号
        scene_num_03 = self.get_scene_number("03")
        scene_num_03.set_color(MY_BLACK)
        self.add(scene_num_03)

        # --- 左右布局 ---
        left_group = VGroup()
        right_group = VGroup()

        # --- 左侧：频率计算 ---
        axes_freq = Axes(
            x_range=[0, 10, 2], y_range=[0, 5, 1], # 示例范围 Q vs P(%)
            x_length=5, y_length=4,
            axis_config={"include_numbers": True, "color": MY_DARK_GRAY},
            tips=False
        ).shift(LEFT * 3.5 + DOWN * 0.5)
        # 模拟 P-III 型曲线（简化）
        freq_curve_func = lambda q: 4.5 * np.exp(-0.8 * q) + 0.1 # 示意曲线 P(Q)
        freq_curve = axes_freq.plot(freq_curve_func, x_range=[0.1, 8], color=MY_BLUE, stroke_width=3)
        freq_labels = axes_freq.get_axis_labels(x_label=MathTex("Q (m^3/s)", font_size=24), y_label=MathTex("P (\\%)", font_size=24))

        # 标记设计频率点 (e.g., P=1%)
        design_P = 1.0
        # 反向查找对应的 Q (或直接设定一个 Q 值)
        design_Qp = 4.0 # 假设设计洪峰是 4
        # 找到曲线上 Q=design_Qp 的点
        design_point_coord = axes_freq.input_to_graph_point(design_Qp, freq_curve) # Pass freq_curve
        design_point_dot = Dot(design_point_coord, color=MY_RED, radius=0.1)

        # 引导线和标签
        # ******** 修正处 ********
        # Manually create dashed lines to the point
        x_coord, y_coord = axes_freq.point_to_coords(design_point_coord)
        point_on_x_axis = axes_freq.c2p(x_coord, 0)
        point_on_y_axis = axes_freq.c2p(0, y_coord)

        v_line = DashedLine(
            point_on_x_axis, design_point_coord,
            color=MY_RED, stroke_width=2,
            dash_length=0.1, dashed_ratio=0.6
        )
        h_line = DashedLine(
            point_on_y_axis, design_point_coord,
            color=MY_RED, stroke_width=2,
            dash_length=0.1, dashed_ratio=0.6
        )
        lines = VGroup(v_line, h_line) # Group the manually created dashed lines
        # ***********************

        label_Qp = MathTex("Q_p", font_size=32, color=MY_RED).next_to(point_on_x_axis, DOWN, buff=0.2)
        label_P = MathTex("P=1\\%", font_size=32, color=MY_RED).next_to(point_on_y_axis, LEFT, buff=0.2)


        # 文本标注
        text_freq = Text("步骤 4 & 6：频率计算确定设计值", font_size=28, color=MY_DARK_GRAY)
        text_freq.next_to(axes_freq, UP, buff=0.5).align_to(axes_freq, LEFT)

        left_group.add(axes_freq, freq_curve, freq_labels, design_point_dot, lines, label_Qp, label_P, text_freq)

        # --- 右侧：典型选择与缩放 ---
        axes_scale = Axes(
            x_range=[0, 8, 1], y_range=[0, 12, 2], # T vs Q
            x_length=5, y_length=4,
            axis_config={"include_numbers": True, "color": MY_DARK_GRAY},
            tips=False
        ).shift(RIGHT * 3.5 + DOWN * 0.5)
        scale_labels = axes_scale.get_axis_labels(x_label=MathTex("T (h)", font_size=24), y_label=MathTex("Q (m^3/s)", font_size=24))

        # 典型过程线 (未缩放)
        typical_func = lambda t: 8 * np.exp(-(t - 4)**2 / 2.0) # 假设峰值为 8
        typical_curve = axes_scale.plot(typical_func, color=MY_BLUE, stroke_width=3)
        typical_label = Text("典型过程线 (未缩放)", font_size=24, color=MY_BLUE)
        typical_label.next_to(typical_curve, UP, buff=0.1).shift(LEFT*0.5)

        # 设计洪峰线 (假设 Qp = 10)
        design_Qp_value = 10.0
        design_peak_line = DashedLine(
            axes_scale.c2p(0, design_Qp_value),
            axes_scale.c2p(8, design_Qp_value),
            color=MY_RED, stroke_width=2
        )
        label_Qp_line = MathTex(f"Q_p = {design_Qp_value:.0f}", font_size=28, color=MY_RED)
        label_Qp_line.next_to(design_peak_line, RIGHT, buff=0.2)

        # 文本标注
        text_scale = Text("步骤 8 & 9：选择典型并缩放至设计值", font_size=28, color=MY_DARK_GRAY)
        text_scale.next_to(axes_scale, UP, buff=0.5).align_to(axes_scale, LEFT)

        right_group.add(axes_scale, scale_labels, typical_curve, typical_label, design_peak_line, label_Qp_line, text_scale)

        # --- 旁白与动画 ---
        voice_text_scene_03 = "我们来可视化关键的两个环节。左侧是频率计算，通过频率曲线（如P-III型线）确定特定频率（如1%）对应的设计洪峰Qp和设计洪量W。右侧是选择典型洪水过程线，并根据计算出的设计洪峰Qp值，对其进行同倍比缩放，最终得到红色的设计洪水过程线。📈➡️📉"

        with custom_voiceover_tts(voice_text_scene_03) as tracker:
            if tracker.audio_path:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("警告 [场景03]: 未能加载音频，动画将按预设时间进行。")

            subtitle_voice = Text(
                voice_text_scene_03, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_BLACK, fill_color=MY_BLACK,
                fill_opacity=0.6, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)

            # 动画序列
            self.play(FadeIn(subtitle_group, run_time=0.5))

            # 显示左侧频率计算部分
            self.play(
                self.camera.frame.animate.move_to(left_group.get_center() + UP*0.5).set_width(left_group.width * 2.5),
                run_time=1.0
            )
            self.play(
                FadeIn(text_freq),
                Create(axes_freq), Create(freq_curve), FadeIn(freq_labels),
                run_time=2.0
            )
            self.play(
                FadeIn(design_point_dot, scale=0.5),
                Create(lines), # Create the VGroup of dashed lines
                Write(label_Qp), Write(label_P),
                run_time=2.5
            )
            self.wait(1.0) # 停留看左侧

            # 移动到右侧缩放部分
            self.play(
                self.camera.frame.animate.move_to(right_group.get_center() + UP*0.5).set_width(right_group.width * 2.5),
                run_time=1.5
            )
            self.play(
                FadeIn(text_scale),
                Create(axes_scale), FadeIn(scale_labels),
                Create(typical_curve), FadeIn(typical_label),
                Create(design_peak_line), Write(label_Qp_line),
                run_time=2.5
            )

            # 执行缩放动画
            original_peak_value = 8.0 # typical_func 的峰值
            scale_factor = design_Qp_value / original_peak_value
            # 创建缩放后的曲线对象
            scaled_curve_obj = axes_scale.plot(lambda t: typical_func(t) * scale_factor, color=MY_RED, stroke_width=3)
            scaled_label = Text("设计洪水过程线", font_size=24, color=MY_RED)
            scaled_label.move_to(typical_label).shift(UP*0.2) # 稍微上移避免重叠

            # 使用 Transform 进行平滑过渡
            self.play(
                Transform(typical_curve, scaled_curve_obj),
                Transform(typical_label, scaled_label),
                self.camera.frame.animate.scale(0.9).move_to(right_group.get_center() + UP*0.5), # 稍微拉远看清整体
                run_time=2.5
            )
            self.wait(1.0) # 停留看右侧结果

            # 恢复相机
            self.play(self.camera.frame.animate.move_to(ORIGIN).set_width(config.frame_width), run_time=1.0)

            # 等待音频结束
            intro_time = 0.5 # 字幕
            left_anim_time = 1.0 + 2.0 + 2.5 + 1.0 # 左侧动画
            transition_time = 1.5 # 移动到右侧
            right_anim_time = 2.5 + 2.5 + 1.0 # 右侧动画 + 缩放 + 停留
            outro_time = 1.0 # 恢复相机
            total_anim_time_est = intro_time + left_anim_time + transition_time + right_anim_time + outro_time

            wait_time = max(0, tracker.duration - total_anim_time_est - 1.0) # 减去字幕淡出时间
            if wait_time > 0:
                self.wait(wait_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_group), run_time=1.0)

        self.wait(1.5) # 场景结束停留

    # ==========================================================================
    # 场景 4: 总结与结束
    # ==========================================================================
    def play_scene_04(self):
        self.scene_time_tracker.set_value(0)

        # 背景
        bg4 = self.create_gradient_background(MY_DARK_BLUE, MY_LIGHT_BLUE, DOWN)
        self.add(bg4)

        # 场景编号
        scene_num_04 = self.get_scene_number("04")
        self.add(scene_num_04)

        # 总结标题
        summary_title = Text("总结回顾 📜", font_size=48, color=MY_WHITE)
        summary_title.to_edge(UP, buff=1.5)

        # 核心要点
        point1 = Text("典型洪水选择标准：峰高量大、代表性、峰形集中、洪峰偏后。",
                      font_size=32, color=MY_YELLOW, width=config.frame_width - 4, should_center=True) # 自动换行并居中
        point2 = Text("设计洪水计算流程：数据准备 → 频率分析 → 典型选择 → 过程线缩放。",
                      font_size=32, color=MY_YELLOW, width=config.frame_width - 4, should_center=True) # 自动换行并居中

        summary_points = VGroup(point1, point2).arrange(DOWN, buff=0.5) # 内部垂直排列
        summary_points.next_to(summary_title, DOWN, buff=1.0) # 定位

        # 结束语
        end_text = Text("感谢观看！ 🎉", font_size=36, color=MY_WHITE)
        end_text.to_edge(DOWN, buff=1.0)

        # --- 旁白与动画 ---
        voice_text_scene_04 = "最后，我们来总结一下。选择典型洪水过程线要关注峰高量大、代表性、峰形集中和洪峰偏后这四个关键条件。而设计洪水的计算则遵循数据准备、频率分析、典型选择和过程线缩放的基本流程。希望本次讲解对您有所帮助，感谢观看！"

        with custom_voiceover_tts(voice_text_scene_04) as tracker:
            if tracker.audio_path:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("警告 [场景04]: 未能加载音频，动画将按预设时间进行。")

            subtitle_voice = Text(
                voice_text_scene_04, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            subtitle_bg = SurroundingRectangle(
                subtitle_voice, buff=0.1, color=MY_BLACK, fill_color=MY_BLACK,
                fill_opacity=0.6, stroke_width=0
            )
            subtitle_group = VGroup(subtitle_bg, subtitle_voice).set_z_index(5)

            # 动画序列
            self.play(FadeIn(subtitle_group, run_time=0.5))
            self.play(FadeIn(summary_title, shift=DOWN*0.2), run_time=1.5)

            # 使用 FadeIn 替代 Write
            self.play(FadeIn(point1, shift=UP*0.1), run_time=2.5)
            self.play(FadeIn(point2, shift=UP*0.1), run_time=3.0)

            self.play(FadeIn(end_text, scale=0.8), run_time=1.5)

            # 等待音频结束
            intro_time = 0.5 # 字幕
            summary_anim_time = 1.5 + 2.5 + 3.0 + 1.5 # 标题+要点+结束语
            total_anim_time_est = intro_time + summary_anim_time

            wait_time = max(0, tracker.duration - total_anim_time_est - 1.0) # 减去字幕淡出时间
            if wait_time > 0:
                self.wait(wait_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_group), run_time=1.0)

        # 结束动画：所有元素淡出
        all_elements = VGroup(summary_title, summary_points, end_text, scene_num_04) # 不包括背景
        self.play(FadeOut(all_elements), run_time=2.0)
        self.wait(1)


# --- Main execution block ---
if __name__ == "__main__":
    # 基本配置
    config.pixel_height = 1080  # 设置分辨率高
    config.pixel_width = 1920  # 设置分辨率宽
    config.frame_rate = 30  # 设置帧率
    config.output_file = "CombinedScene"  # 指定输出文件名
    config.disable_caching = True # 禁用缓存

    # 临时设置输出目录,必须使用#(output_video)
    config.media_dir = "avoid_flood" # java程序会对#(output_video)进行替换
    scene = CombinedScene()
    scene.render()
    print(f"Scene rendering finished. Output file: {config.output_file}.mp4 in {config.media_dir}")