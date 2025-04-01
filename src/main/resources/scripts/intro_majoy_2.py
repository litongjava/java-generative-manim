# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
from moviepy import AudioFileClip # Correct import for AudioFileClip
import hashlib
import manimpango # <--- 添加导入

# --- 自定义颜色 ---
MY_DARK_BLUE = "#1E3A8A"  # 深蓝色
MY_LIGHT_GRAY = "#F3F4F6"  # 浅灰色
MY_MEDIUM_GRAY = "#D1D5DB"  # 中灰色
MY_GRAY_B = "#374151" # 深灰蓝，用于背景
MY_GOLD = "#F59E0B"  # 金色
MY_ORANGE = "#F97316"  # 橙色
MY_RED = "#DC2626"  # 红色
MY_WHITE = "#FFFFFF"  # 白色
MY_BLACK = "#000000"  # 黑色
MY_BLUE_D = "#2563EB" # 较深蓝
MY_TEAL_E = "#14B8A6" # 蓝绿
MY_BLUE_C = "#60A5FA" # 浅蓝
MY_BLUE_A = "#BFDBFE" # 更浅蓝，用于水利背景
MY_BEIGE = "#F5F5DC" # 米色

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
        pass # Keep cache

# --- 统一字体设置 ---
# 确保系统已安装 "Noto Sans CJK SC" 字体，或替换为其他可用中文字体
DEFAULT_FONT = "Noto Sans CJK SC"
# 使用 manimpango 检查字体是否存在
available_fonts = manimpango.list_fonts()
if DEFAULT_FONT not in available_fonts:
    print(f"警告: 字体 '{DEFAULT_FONT}' 未找到，将尝试使用备用字体。")
    # 查找一个备用中文字体，如果找不到则设为 None
    fallback_fonts = ["PingFang SC", "Microsoft YaHei", "SimHei", "Arial Unicode MS"] # 常见备选
    found_fallback = False
    for font in fallback_fonts:
        if font in available_fonts:
            DEFAULT_FONT = font
            print(f"已切换到备用字体: '{DEFAULT_FONT}'")
            found_fallback = True
            break
    if not found_fallback:
        print(f"警告: 未找到指定的 '{DEFAULT_FONT}' 或任何备用中文字体。将使用 Manim 默认字体，中文可能无法正确显示。")
        DEFAULT_FONT = None # Fallback to Manim's default if no common CJK font found
else:
    print(f"字体 '{DEFAULT_FONT}' 已找到。")


# -----------------------------
# CombinedScene：整合所有场景
# -----------------------------
class CombinedScene(MovingCameraScene):
    """
    重庆交通大学专业信息速览动画。
    """
    def setup(self):
        MovingCameraScene.setup(self)
        # 设置默认字体
        if DEFAULT_FONT:
            Text.set_default(font=DEFAULT_FONT)
            # MathTex 依赖 LaTeX，通常不需要设置 Pango 字体
            # MathTex.set_default(font=DEFAULT_FONT)
        else:
             # 如果没有找到合适的字体，这里不再重复打印警告，因为前面已经打印过了
             pass

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
        # Final wait before ending
        self.wait(2)

    def get_scene_number(self, number_str):
        """创建并定位场景编号"""
        scene_num = Text(number_str, font_size=24, color=MY_WHITE)
        scene_num.to_corner(UR, buff=0.5)
        scene_num.set_z_index(10) # 确保在顶层
        return scene_num

    def clear_and_reset(self):
        """清除当前场景所有对象并重置相机"""
        valid_mobjects = [m for m in self.mobjects if m is not None]
        for mob in valid_mobjects:
            mob.clear_updaters()
        all_mobjects_group = Group(*valid_mobjects)
        if all_mobjects_group:
            self.play(FadeOut(all_mobjects_group, shift=DOWN * 0.5), run_time=0.5)
        self.clear()
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        self.wait(0.1)

    def create_background(self, color=MY_BLACK, gradient_colors=None, gradient_direction=None):
        """创建覆盖全屏的背景"""
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_opacity=1.0
        )
        if gradient_colors:
            # Manim CE v0.19.0 使用 fill_color 接受列表表示渐变
            bg.set_fill(color=gradient_colors, opacity=1.0)
            if gradient_direction is not None:
                 # 使用 set_sheen_direction 设置渐变方向
                 bg.set_sheen_direction(gradient_direction)
            else:
                 # 默认为从左到右 (RIGHT)
                 bg.set_sheen_direction(RIGHT)
        else:
            bg.set_fill(color=color, opacity=1.0)

        bg.set_z_index(-10) # 置于最底层
        return bg

    def play_scene_00(self):
        """场景〇：开场标题"""
        # 背景
        bg0 = self.create_background(gradient_colors=[MY_BLUE_D, MY_TEAL_E], gradient_direction=DR) # 左上到右下渐变
        self.add(bg0)

        # 内容
        title = Text("重庆交通大学 专业信息速览", font_size=60, color=MY_WHITE)
        title.move_to(UP * 0.5)
        subtitle = Text("港口航道与海岸工程 & 水利水电工程", font_size=40, color=MY_LIGHT_GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 旁白与动画同步
        voice_text = "大家好！欢迎观看重庆交通大学专业信息速览。本期我们将聚焦港口航道与海岸工程以及水利水电工程这两个特色专业。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、主标题动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=2.0), # Write 对 Text 也可以用
                    lag_ratio=0.0
                ),
                run_time=2.0 # 动画总时长与主标题Write一致
            )

            # 主标题完成后，副标题滑入
            self.play(FadeIn(subtitle, shift=DOWN * 0.5), run_time=1.5)

            # 计算剩余等待时间
            elapsed_time = 2.0 + 1.5 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1) # 场景结束前稍作停留

    def play_scene_01(self):
        """场景一：港口航道与海岸工程 - 关键年份"""
        # 背景
        bg1 = self.create_background(color=MY_GRAY_B)
        self.add(bg1)
        scene_num = self.get_scene_number("01")
        self.add(scene_num)

        # 标题
        title = Text("港口航道与海岸工程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)

        # 左侧内容
        year_left = Text("2009年", font_size=36, color=MY_GOLD, weight=BOLD)
        event_left = Text("评为国家级特色专业", font_size=32, color=MY_WHITE)
        group_left = VGroup(year_left, event_left).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        group_left.next_to(title, DOWN, buff=1.0).shift(LEFT * 3.5)

        # 右侧内容
        year_right = Text("2017年", font_size=36, color=MY_GOLD, weight=BOLD)
        event_right = Text("通过全国工程教育专业认证复评", font_size=32, color=MY_WHITE)
        group_right = VGroup(year_right, event_right).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        group_right.next_to(title, DOWN, buff=1.0).shift(RIGHT * 3.5)

        # 旁白与动画同步
        voice_text = "首先来看港口航道与海岸工程。2009年，该专业被评为国家级特色专业。到了2017年，它顺利通过了全国工程教育专业认证的复评。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、标题动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5), # Write 对 Text 也可以用
                    lag_ratio=0.0
                ),
                run_time=1.5
            )

            # 左右内容滑入
            self.play(
                FadeIn(group_left, shift=LEFT * 2),
                run_time=1.0
            )
            self.wait(0.5) # 稍作停顿
            self.play(
                FadeIn(group_right, shift=RIGHT * 2),
                run_time=1.0
            )

            # 计算剩余等待时间
            elapsed_time = 1.5 + 1.0 + 0.5 + 1.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_02(self):
        """场景二：港口航道与海岸工程 - 学分要求"""
        # 背景 (保持)
        bg2 = self.create_background(color=MY_GRAY_B)
        self.add(bg2)
        scene_num = self.get_scene_number("02")
        self.add(scene_num)

        # 内容
        question = Text("最低毕业学分要求？", font_size=48, color=MY_BLUE_C)
        question.move_to(UP * 0.5)
        answer = Text("180 学分", font_size=72, color=MY_WHITE, weight=BOLD)
        answer.next_to(question, DOWN, buff=0.8)

        # 旁白与动画同步
        voice_text = "那么，港口航道与海岸工程专业的最低毕业学分要求是多少呢？答案是 180 学分。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、问题动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(question, run_time=1.0), # Write 对 Text 也可以用
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # 答案出现
            self.play(GrowFromCenter(answer), run_time=1.0)

            # 计算剩余等待时间
            elapsed_time = 1.0 + 1.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_03(self):
        """场景三：港口航道与海岸工程 - 专业核心课程"""
        # 背景 (保持)
        bg3 = self.create_background(color=MY_GRAY_B)
        self.add(bg3)
        scene_num = self.get_scene_number("03")
        self.add(scene_num)

        # 标题
        title = Text("专业核心课程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)

        # --- 手动创建列表 (替代 BulletedList) ---
        course_items_text = [
            "渠化工程",
            "港口规划与布置",
            "航道整治",
            "工程项目管理",
            "港口与海岸水工建筑物",
        ]
        course_list_group = VGroup()
        item_font_size = 36
        bullet_color = MY_WHITE
        text_color = MY_WHITE
        line_buff = 0.4 # 行间距
        bullet_text_buff = 0.2 # 项目符号和文本间距

        for item_text in course_items_text:
            # 创建项目符号 (使用 Text) 和文本
            bullet = Text("• ", font_size=item_font_size, color=bullet_color)
            text = Text(item_text, font_size=item_font_size, color=text_color)
            # 将符号和文本水平排列
            line = VGroup(bullet, text).arrange(RIGHT, buff=bullet_text_buff)
            course_list_group.add(line)

        # 垂直排列所有行，左对齐
        course_list_group.arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
        # 定位列表
        course_list_group.next_to(title, DOWN, buff=0.8).align_to(title, LEFT).shift(LEFT*0.5) # 稍微左移以居中感

        # 旁白与动画同步
        voice_text = "该专业的核心课程包括：渠化工程、港口规划与布置、航道整治、工程项目管理，以及港口与海岸水工建筑物。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、标题动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.0), # Write 对 Text 也可以用
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # 逐项显示列表 (使用 FadeIn)
            self.play(
                AnimationGroup(
                    *[FadeIn(item, shift=UP*0.2) for item in course_list_group],
                    lag_ratio=0.5 # 各项之间延迟
                ),
                run_time=3.0 # 总动画时间
            )

            # 计算剩余等待时间
            elapsed_time = 1.0 + 3.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_04(self):
        """场景四：港口航道与海岸工程 - 特定课程信息"""
        # 背景 (保持)
        bg4 = self.create_background(color=MY_GRAY_B)
        self.add(bg4)
        scene_num = self.get_scene_number("04")
        self.add(scene_num)

        # 上半部分
        course_name1 = Text("水工钢筋混凝土结构综合实践", font_size=36, color=MY_WHITE)
        course_term1 = Text("第 5 学期 开设", font_size=36, color=MY_GOLD, weight=BOLD)
        group_top = VGroup(course_name1, course_term1).arrange(DOWN, buff=0.3)
        group_top.move_to(UP * 1.5)

        # 下半部分
        course_name2 = Text("数学建模课程代码", font_size=36, color=MY_WHITE)
        course_code2 = Text("19210919", font_size=48, color=MY_GOLD, weight=BOLD)
        group_bottom = VGroup(course_name2, course_code2).arrange(DOWN, buff=0.3)
        group_bottom.move_to(DOWN * 1.5)

        # 旁白与动画同步
        voice_text = "具体来看，水工钢筋混凝土结构综合实践这门课在第 5 学期开设。而数学建模课程的代码是 19210919。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、上半部分动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    FadeIn(group_top, shift=UP*0.3),
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # 下半部分出现
            self.play(FadeIn(group_bottom, shift=UP*0.3), run_time=1.0)

            # 计算剩余等待时间
            elapsed_time = 1.0 + 1.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_05(self):
        """场景五：水利水电工程 - 关键年份与荣誉"""
        # 背景 (浅蓝色，模拟水)
        bg5 = self.create_background(color=MY_BLUE_A)
        self.add(bg5)
        scene_num = self.get_scene_number("05")
        self.add(scene_num)

        # 标题
        title = Text("水利水电工程", font_size=48, color=MY_DARK_BLUE) # 深色字配浅背景
        title.to_edge(UP, buff=1.0)

        # 年份
        year = Text("2013年", font_size=40, color=MY_GOLD, weight=BOLD)
        year.next_to(title, DOWN, buff=0.8)

        # 荣誉列表
        honor1 = Text("入选教育部‘卓越工程师教育培养计划’试点专业", font_size=32, color=MY_DARK_BLUE)
        honor2 = Text("入选重庆市‘三特行动计划’首批特色专业建设点", font_size=32, color=MY_DARK_BLUE)
        honors_group = VGroup(honor1, honor2).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        honors_group.next_to(year, DOWN, buff=0.8).align_to(year, LEFT).shift(LEFT*2) # 左对齐并调整位置

        # 旁白与动画同步
        voice_text = "接下来是水利水电工程专业。2013年是重要的一年，该专业不仅入选了教育部的‘卓越工程师教育培养计划’试点专业，还成为了重庆市‘三特行动计划’的首批特色专业建设点。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_DARK_BLUE, # 深色字配浅背景
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、标题动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5), # Write 对 Text 也可以用
                    lag_ratio=0.0
                ),
                run_time=1.5
            )

            # 年份出现
            self.play(FadeIn(year), run_time=0.5)

            # 荣誉逐条出现
            self.play(FadeIn(honor1, shift=UP * 0.2), run_time=1.0)
            self.play(FadeIn(honor2, shift=UP * 0.2), run_time=1.0)

            # 计算剩余等待时间
            elapsed_time = 1.5 + 0.5 + 1.0 + 1.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_06(self):
        """场景六：水利水电工程 - 学分构成"""
        # 背景 (保持)
        bg6 = self.create_background(color=MY_BLUE_A)
        self.add(bg6)
        scene_num = self.get_scene_number("06")
        self.add(scene_num)

        # 总学分
        label_total = Text("总学分", font_size=40, color=MY_DARK_BLUE)
        value_total = Text("166 + 10 学分", font_size=60, color=MY_GOLD, weight=BOLD)
        group_total = VGroup(label_total, value_total).arrange(DOWN, buff=0.3)
        group_total.move_to(UP * 1.0)

        # 毕业设计学分
        label_design = Text("毕业设计", font_size=40, color=MY_DARK_BLUE)
        value_design = Text("12 学分", font_size=60, color=MY_GOLD, weight=BOLD)
        group_design = VGroup(label_design, value_design).arrange(DOWN, buff=0.3)
        group_design.next_to(group_total, DOWN, buff=1.0)

        # 旁白与动画同步
        voice_text = "水利水电工程的总学分要求是 166 加 10 学分。其中，毕业设计占 12 学分。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_DARK_BLUE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、总学分动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    GrowFromCenter(group_total), # 或 FadeIn(group_total)
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # 毕业设计学分出现
            self.play(FadeIn(group_design), run_time=1.0)

            # 计算剩余等待时间
            elapsed_time = 1.0 + 1.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_07(self):
        """场景七：水利水电工程 - 专业核心课程"""
        # 背景 (保持)
        bg7 = self.create_background(color=MY_BLUE_A)
        self.add(bg7)
        scene_num = self.get_scene_number("07")
        self.add(scene_num)

        # 标题
        title = Text("专业核心课程", font_size=48, color=MY_DARK_BLUE)
        title.to_edge(UP, buff=1.0)

        # --- 手动创建列表 ---
        course_items_text = [
            "工程水文与水资源综合利用",
            "水工建筑物",
            "水电站",
            "水利工程施工与管理",
        ]
        course_list_group = VGroup()
        item_font_size = 36
        bullet_color = MY_DARK_BLUE
        text_color = MY_DARK_BLUE
        line_buff = 0.4 # 行间距
        bullet_text_buff = 0.2 # 项目符号和文本间距

        for item_text in course_items_text:
            bullet = Text("• ", font_size=item_font_size, color=bullet_color)
            text = Text(item_text, font_size=item_font_size, color=text_color)
            line = VGroup(bullet, text).arrange(RIGHT, buff=bullet_text_buff)
            course_list_group.add(line)

        course_list_group.arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
        course_list_group.next_to(title, DOWN, buff=0.8).align_to(title, LEFT).shift(LEFT*0.5)

        # 旁白与动画同步
        voice_text = "水利水电工程的核心课程主要有：工程水文与水资源综合利用、水工建筑物、水电站，以及水利工程施工与管理。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_DARK_BLUE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、标题动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.0), # Write 对 Text 也可以用
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # 逐项显示列表
            self.play(
                AnimationGroup(
                    *[FadeIn(item, shift=UP*0.2) for item in course_list_group],
                    lag_ratio=0.5
                ),
                run_time=3.0
            )

            # 计算剩余等待时间
            elapsed_time = 1.0 + 3.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_08(self):
        """场景八：自主发展计划 - 美育"""
        # 背景 (米色)
        bg8 = self.create_background(color=MY_BEIGE)
        self.add(bg8)
        scene_num = self.get_scene_number("08")
        self.add(scene_num)

        # 标题
        title = Text("自主发展计划（第二课堂）", font_size=48, color=MY_DARK_BLUE)
        title.to_edge(UP, buff=1.5)

        # 内容
        label = Text("美育", font_size=40, color=MY_BLUE_C)
        practice = Text("美育实践", font_size=40, color=MY_DARK_BLUE, weight=BOLD)
        content_group = VGroup(label, practice).arrange(RIGHT, buff=0.5)
        content_group.next_to(title, DOWN, buff=1.0)

        # 旁白与动画同步
        voice_text = "在自主发展计划，也就是第二课堂中，美育实践是其中的重要组成部分。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_DARK_BLUE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、标题动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5), # Write 对 Text 也可以用
                    lag_ratio=0.0
                ),
                run_time=1.5
            )

            # 内容出现
            self.play(
                FadeIn(content_group, shift=UP*0.2),
                run_time=1.0
            )

            # 计算剩余等待时间
            elapsed_time = 1.5 + 1.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    def play_scene_09(self):
        """场景九：结束画面"""
        # 背景 (恢复开场渐变)
        bg9 = self.create_background(gradient_colors=[MY_BLUE_D, MY_TEAL_E], gradient_direction=DR)
        self.add(bg9)
        scene_num = self.get_scene_number("09")
        self.add(scene_num)

        # 内容
        end_text = Text("专业信息速览完毕", font_size=54, color=MY_WHITE)
        end_text.move_to(ORIGIN + UP * 0.5)
        more_info = Text("更多详细信息请查询官方网站", font_size=30, color=MY_LIGHT_GRAY)
        more_info.next_to(end_text, DOWN, buff=0.8)

        # 旁白与动画同步
        voice_text = "重庆交通大学港口航道与海岸工程及水利水电工程的专业信息速览到此结束。感谢您的观看！如果想了解更多详细信息，请查询学校官方网站。"
        with custom_voiceover_tts(voice_text) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = Text(
                voice_text, font_size=28, color=MY_WHITE,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # 同步开始：声音、字幕、结束语动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    FadeIn(end_text, scale=0.8), # 从小到大淡入
                    lag_ratio=0.0
                ),
                run_time=1.5
            )

            # 提示信息出现
            self.play(FadeIn(more_info), run_time=1.0)

            # 可选：相机轻微缩小
            self.play(self.camera.frame.animate.scale(1.1), run_time=1.0)

            # 计算剩余等待时间
            elapsed_time = 1.5 + 1.0 + 1.0 # 已播放动画时间
            remaining_time = tracker.duration - elapsed_time - 1.0 # 减去字幕淡出时间
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出字幕
            self.play(FadeOut(subtitle_voice), run_time=1.0)

        # 结束前画面停留
        self.wait(2)
        # 最后的淡出由 clear_and_reset 处理，或者可以在 construct 最后加一个全局淡出

# --- Main execution block ---
if __name__ == "__main__":
    # 基本配置
    config.pixel_height = 1080  # 设置分辨率高
    config.pixel_width = 1920  # 设置分辨率宽
    config.frame_rate = 30  # 设置帧率
    config.output_file = "CombinedScene"  # 指定输出文件名
    config.disable_caching = True # 禁用缓存

    # 临时设置输出目录,必须使用#(output_video)
    config.media_dir = "intro_majoy2"

    # 字体检查已在类定义之前完成

    scene = CombinedScene()
    scene.render()
    print(f"Scene rendering finished. Output video: {config.output_file}.mp4 in {config.media_dir}")