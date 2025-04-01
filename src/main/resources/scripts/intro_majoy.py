# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
from manim.utils.color.SVGNAMES import BROWN
from moviepy import AudioFileClip # Correct import for AudioFileClip
import hashlib
from manim.utils.color import color_gradient # Import for gradient

# --- 自定义颜色 ---
MY_DARK_BLUE = "#1E3A8A"
MY_LIGHT_GRAY = "#F3F4F6"
MY_MEDIUM_GRAY = "#D1D5DB"
MY_GOLD = "#F59E0B" # GOLD_E
MY_ORANGE = "#F97316"
MY_RED = "#DC2626"
MY_WHITE = "#FFFFFF"
MY_BLACK = "#000000"
MY_BLUE_D = BLUE_D # "#2C71B0"
MY_TEAL_E = TEAL_E # "#43C4B2"
MY_GRAY_B = GRAY_B # "#BDBDBD"
MY_BLUE_C = BLUE_C # "#5C9DCE"
MY_BLUE_A = BLUE_A # "#8CD1F5"
MY_BEIGE = "#F5F5DC" # 米色

# --- TTS 配置 ---
CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


class CustomVoiceoverTracker:
    """辅助类，用于跟踪 TTS 音频路径和时长。"""
    def __init__(self, audio_path, duration):
        self.audio_path = audio_path
        self.duration = duration


def get_cache_filename(text):
    """根据文本内容生成缓存文件名。"""
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}.mp3")


@contextmanager
def custom_voiceover_tts(text, token="123456", base_url="https://uni-ai.fly.dev/api/manim/tts"):
    """
    上下文管理器，用于生成或获取缓存的 TTS 音频。

    Args:
        text (str): 需要转换为语音的文本。
        token (str): API 访问令牌。
        base_url (str): TTS 服务的基础 URL。

    Yields:
        CustomVoiceoverTracker: 包含音频路径和时长的对象。

    Raises:
        Exception: 如果 TTS API 请求失败。
    """
    cache_file = get_cache_filename(text)

    if os.path.exists(cache_file):
        audio_file = cache_file
        # print(f"Using cached TTS for: {text[:30]}...")
    else:
        # print(f"Generating TTS for: {text[:30]}...")
        input_text = requests.utils.quote(text)
        url = f"{base_url}?token={token}&input={input_text}"

        try:
            response = requests.get(url, stream=True, timeout=60) # 添加超时
            response.raise_for_status() # 检查 HTTP 错误状态码

            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            audio_file = cache_file
        except requests.exceptions.RequestException as e:
            raise Exception(f"TTS API request failed: {e}")
        except Exception as e:
            raise Exception(f"An error occurred during TTS generation: {e}")


    try:
        clip = AudioFileClip(audio_file)
        duration = clip.duration
        clip.close()
    except Exception as e:
        # 如果音频文件损坏或无法读取，尝试删除缓存并重新生成
        print(f"Error reading audio file {audio_file}: {e}. Attempting to regenerate.")
        if os.path.exists(cache_file):
            os.remove(cache_file)
        # 重新调用自身以尝试重新生成
        with custom_voiceover_tts(text, token, base_url) as tracker:
            yield tracker
        return # 确保在递归调用后退出

    tracker = CustomVoiceoverTracker(audio_file, duration)
    try:
        yield tracker
    finally:
        # 可以选择在这里清理缓存文件，但通常保留缓存以提高效率
        pass


# --- 主场景类 ---
class CombinedScene(MovingCameraScene):
    """
    整合所有场景的 Manim 动画，展示重庆交通大学专业信息速览。
    """
    def construct(self):
        """构建整个动画序列。"""
        # 确保中文字体可用，推荐使用 Noto Sans CJK SC 或系统支持的其他中文字体
        try:
            # 尝试设置默认字体，如果字体不存在会报错
            Text.set_default(font="Noto Sans CJK SC")
            print("Default font set to 'Noto Sans CJK SC'.")
        except Exception:
            print("警告：未找到 'Noto Sans CJK SC' 字体，将使用 Manim 默认字体。中文可能无法正确显示。")
            print("请安装 'Noto Sans CJK SC' 字体或修改代码中的字体名称。")
            # 如果需要，可以设置一个备用字体
            # Text.set_default(font="Microsoft YaHei") # 例如

        # 依次播放所有场景
        self.play_scene_00()
        self.clear_and_reset()
        self.play_scene_01()
        self.clear_and_reset()
        self.play_scene_02()
        self.clear_and_reset()
        self.play_scene_03() # 使用修改后的版本
        self.clear_and_reset()
        self.play_scene_04()
        self.clear_and_reset()
        self.play_scene_05()
        self.clear_and_reset()
        self.play_scene_06()
        self.clear_and_reset()
        self.play_scene_07() # 使用修改后的版本
        self.clear_and_reset()
        self.play_scene_08()
        self.clear_and_reset()
        self.play_scene_09()
        self.clear_and_reset() # 确保最后也清理

    def get_scene_number(self, number_str, color=MY_WHITE):
        """创建并定位场景编号。"""
        scene_num = Text(number_str, font_size=24, color=color)
        scene_num.to_corner(UR, buff=0.5)
        scene_num.set_z_index(10) # 确保在顶层
        return scene_num

    def clear_and_reset(self):
        """清除当前场景所有对象并重置相机。"""
        # 清除所有对象，包括更新器
        mobjects_to_remove = [m for m in self.mobjects if m is not None]
        for mob in mobjects_to_remove:
            mob.clear_updaters() # 清除可能存在的更新器
        if mobjects_to_remove:
            # 使用 Group 而不是 VGroup，因为 self.mobjects 可能包含非 VMobject
            self.play(FadeOut(Group(*mobjects_to_remove)), run_time=0.5)
        self.clear() # 确保 Manim 内部列表也清空
        # 重置相机位置和缩放
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        # self.wait(0.1) # 短暂等待确保清理完成，通常不需要

    def create_gradient_background(self, color1, color2):
        """创建从左上到右下的渐变背景。"""
        # 注意：Manim CE v0.19.0 的 Rectangle 不直接支持对角线渐变
        # 这里创建一个近似的垂直渐变作为替代
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_opacity=1.0
        )
        # 使用 color_gradient 创建垂直渐变
        gradient = color_gradient((color1, color2), int(bg.height * 2)) # 使用两倍高度使渐变更平缓
        # 应用渐变，这里仍然是垂直的
        bg.set_fill(color=gradient, opacity=1.0)
        # 如果需要精确的对角线渐变，需要使用 shader 或更复杂的技巧
        bg.set_z_index(-10) # 置于底层
        return bg


    def create_solid_background(self, color):
        """创建纯色背景。"""
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=color,
            fill_opacity=1.0,
            stroke_width=0
        )
        bg.set_z_index(-10) # 置于底层
        return bg

    def create_subtitle_voice(self, text, color=MY_WHITE):
        """创建屏幕底部用于同步语音的字幕。"""
        subtitle = Text(
            text,
            font_size=28,
            color=color,
            width=config.frame_width - 2, # 限制宽度以自动换行
            should_center=True, # 换行后居中
        )
        subtitle.to_edge(DOWN, buff=0.5)
        return subtitle

    # --- 场景 00: 开场标题 ---
    def play_scene_00(self):
        """播放开场标题场景。"""
        # 背景
        bg0 = self.create_gradient_background(MY_BLUE_D, MY_TEAL_E)
        self.add(bg0)

        # 内容
        title = Text("重庆交通大学 专业信息速览", font_size=60, color=MY_WHITE)
        title.move_to(UP * 1.5)
        subtitle = Text("港口航道与海岸工程 & 水利水电工程", font_size=40, color=MY_LIGHT_GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 旁白与动画
        voice_text_scene_00 = "大家好！欢迎收看重庆交通大学专业信息速览。本期我们将快速了解港口航道与海岸工程以及水利水电工程这两个专业的关键信息。"
        with custom_voiceover_tts(voice_text_scene_00) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0) # 立即播放声音

            subtitle_voice = self.create_subtitle_voice(voice_text_scene_00)

            # 同步开始：声音、底部字幕、主标题动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5), # 字幕快速淡入
                    Write(title, run_time=2.0),          # 主标题书写
                    lag_ratio=0.0 # 确保同时开始
                ),
                run_time=2.0 # 动画总时长由最长的 Write 决定
            )
            # 副标题动画
            self.play(FadeIn(subtitle, shift=DOWN * 0.5, run_time=1.5))

            # 计算剩余等待时间以匹配音频
            elapsed_time = 2.0 + 1.5 # 已播放动画时长
            fade_out_duration = 1.0 # 字幕淡出时长
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)

            # 淡出底部字幕
            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1) # 场景结束停留

    # --- 场景 01: 港航 - 关键年份 ---
    def play_scene_01(self):
        """播放港航专业关键年份场景。"""
        # 背景
        bg1 = self.create_solid_background(MY_GRAY_B)
        # 场景编号
        scene_num_01 = self.get_scene_number("01")

        # 内容
        title = Text("港口航道与海岸工程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)

        year_2009 = Text("2009年", font_size=36, color=MY_GOLD, weight=BOLD)
        event_2009 = Text("评为国家级特色专业", font_size=32, color=MY_WHITE)
        group_2009 = VGroup(year_2009, event_2009).arrange(DOWN, buff=0.3)

        year_2017 = Text("2017年", font_size=36, color=MY_GOLD, weight=BOLD)
        event_2017 = Text("通过全国工程教育专业认证复评", font_size=32, color=MY_WHITE)
        group_2017 = VGroup(year_2017, event_2017).arrange(DOWN, buff=0.3)

        # 使用 arrange 水平排列，并自动垂直居中
        content_group = VGroup(group_2009, group_2017).arrange(RIGHT, buff=2.0)
        content_group.next_to(title, DOWN, buff=1.0)

        # 旁白与动画
        voice_text_scene_01 = "首先来看港口航道与海岸工程专业。该专业在2009年被评为国家级特色专业，并在2017年通过了全国工程教育专业认证复评。"
        with custom_voiceover_tts(voice_text_scene_01) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = self.create_subtitle_voice(voice_text_scene_01)

            # 过渡：淡入新背景、场景编号、底部字幕和标题
            self.play(
                AnimationGroup(
                    FadeIn(bg1),
                    FadeIn(scene_num_01),
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5),
                    lag_ratio=0.0 # 同步开始
                ),
                run_time=1.5 # 由 Write 决定
            )

            # 主要内容动画
            self.play(FadeIn(group_2009, shift=LEFT * 2, run_time=1.0))
            self.wait(0.5) # 稍作停顿
            self.play(FadeIn(group_2017, shift=RIGHT * 2, run_time=1.0))

            # 计算剩余等待时间
            elapsed_time = 1.5 + 1.0 + 0.5 + 1.0 # 标题 + 左侧 + 停顿 + 右侧
            fade_out_duration = 1.0
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1)

    # --- 场景 02: 港航 - 学分要求 ---
    def play_scene_02(self):
        """播放港航专业学分要求场景。"""
        # 背景 (保持)
        bg2 = self.create_solid_background(MY_GRAY_B)
        self.add(bg2)
        # 场景编号
        scene_num_02 = self.get_scene_number("02")
        self.add(scene_num_02)

        # 内容
        question = Text("最低毕业学分要求？", font_size=48, color=MY_BLUE_C)
        question.move_to(UP * 0.5)
        answer = Text("180 学分", font_size=72, color=MY_WHITE)
        answer.next_to(question, DOWN, buff=0.8)

        # 旁白与动画
        voice_text_scene_02 = "该专业的最低毕业学分要求是多少呢？答案是 180 学分。"
        with custom_voiceover_tts(voice_text_scene_02) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = self.create_subtitle_voice(voice_text_scene_02)

            # 动画
            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(question, run_time=1.0),
                    lag_ratio=0.0
                ),
                run_time=1.0
            )
            self.play(GrowFromCenter(answer, run_time=1.0))

            # 计算剩余等待时间
            elapsed_time = 1.0 + 1.0
            fade_out_duration = 1.0
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1)

    # --- 场景 03: 港航 - 专业核心课程 (修改版) ---
    def play_scene_03(self):
        """播放港航专业核心课程场景 (使用手动列表)。"""
        # 背景 (保持)
        bg3 = self.create_solid_background(MY_GRAY_B)
        self.add(bg3)
        # 场景编号
        scene_num_03 = self.get_scene_number("03")
        self.add(scene_num_03)

        # 内容
        title = Text("专业核心课程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)

        # --- 手动创建列表 ---
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
        # 定位列表 (与之前 BulletedList 的定位逻辑保持一致)
        course_list_group.next_to(title, DOWN, buff=0.8).align_to(LEFT)
        # 微调水平位置，使其大致居中但靠左
        course_list_group.shift(LEFT * (config.frame_width/4 - course_list_group.get_width()/2))


        # --- 旁白与动画 ---
        voice_text_scene_03 = "专业核心课程包括：渠化工程、港口规划与布置、航道整治、工程项目管理，以及港口与海岸水工建筑物等。"
        with custom_voiceover_tts(voice_text_scene_03) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = self.create_subtitle_voice(voice_text_scene_03)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.0),
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # 列表项逐项 FadeIn (现在操作 VGroup 的子项)
            animations = []
            total_list_anim_time = 3.0 # 列表动画总时长
            num_items = len(course_list_group) # 使用 VGroup 的长度
            lag_ratio_val = 0.5
            # 确保 run_time_per_item 大于 0
            denominator = (1 + (num_items - 1) * lag_ratio_val)
            run_time_per_item = total_list_anim_time / denominator if denominator > 0 else total_list_anim_time

            for item_line in course_list_group: # 遍历 VGroup 中的每一行 (也是 VGroup)
                 animations.append(FadeIn(item_line, shift=UP*0.2, run_time=run_time_per_item))

            # 使用 AnimationGroup 并设置 lag_ratio
            if animations: # 确保列表不为空
                self.play(AnimationGroup(*animations, lag_ratio=lag_ratio_val), run_time=total_list_anim_time)

            # 计算剩余等待时间
            elapsed_time = 1.0 + total_list_anim_time
            fade_out_duration = 1.0
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1)


    # --- 场景 04: 港航 - 特定课程信息 ---
    def play_scene_04(self):
        """播放港航专业特定课程信息场景。"""
        # 背景 (保持)
        bg4 = self.create_solid_background(MY_GRAY_B)
        self.add(bg4)
        # 场景编号
        scene_num_04 = self.get_scene_number("04")
        self.add(scene_num_04)

        # 内容
        course1_name = Text("水工钢筋混凝土结构综合实践", font_size=36, color=MY_WHITE)
        course1_term = Text("第 5 学期 开设", font_size=36, color=MY_GOLD)
        group1 = VGroup(course1_name, course1_term).arrange(DOWN, buff=0.3).move_to(UP * 1.5)

        course2_name = Text("数学建模课程代码", font_size=36, color=MY_WHITE)
        course2_code = Text("19210919", font_size=48, color=MY_GOLD) # 课程代码字号稍大
        group2 = VGroup(course2_name, course2_code).arrange(DOWN, buff=0.3).move_to(DOWN * 1.5)

        # 旁白与动画
        voice_text_scene_04 = "来看两个具体的课程信息：水工钢筋混凝土结构综合实践在第 5 学期开设。数学建模课程的代码是 19210919。"
        with custom_voiceover_tts(voice_text_scene_04) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = self.create_subtitle_voice(voice_text_scene_04)

            self.play(FadeIn(subtitle_voice, run_time=0.5)) # 字幕先出现

            # 动画内容
            self.play(FadeIn(group1, run_time=1.0))
            self.wait(0.5) # 停顿
            self.play(FadeIn(group2, run_time=1.0))

            # 计算剩余等待时间
            elapsed_time = 0.5 + 1.0 + 0.5 + 1.0 # 字幕 + group1 + 停顿 + group2
            fade_out_duration = 1.0
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1)

    # --- 场景 05: 水利水电 - 关键年份与荣誉 ---
    def play_scene_05(self):
        """播放水利水电专业关键年份与荣誉场景。"""
        # 背景 (切换)
        bg5 = self.create_solid_background(MY_BLUE_A) # 使用浅蓝色
        # 场景编号
        scene_num_05 = self.get_scene_number("05")

        # 内容
        title = Text("水利水电工程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)

        year = Text("2013年", font_size=40, color=MY_GOLD, weight=BOLD)
        year.next_to(title, DOWN, buff=0.8)

        honor1 = Text("入选教育部‘卓越工程师教育培养计划’试点专业", font_size=32, color=MY_WHITE, width=config.frame_width - 4) # 限制宽度防止超屏
        honor2 = Text("入选重庆市‘三特行动计划’首批特色专业建设点", font_size=32, color=MY_WHITE, width=config.frame_width - 4)
        # 垂直排列，左对齐
        honors_group = VGroup(honor1, honor2).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        honors_group.next_to(year, DOWN, buff=0.8)
        # 确保荣誉列表在屏幕内
        if honors_group.get_left()[0] < -config.frame_width / 2 + 1:
             honors_group.shift(RIGHT * (-config.frame_width / 2 + 1 - honors_group.get_left()[0]))


        # 旁白与动画
        voice_text_scene_05 = "接下来是水利水电工程专业。在2013年，该专业入选了教育部的‘卓越工程师教育培养计划’试点专业，并同时入选重庆市‘三特行动计划’首批特色专业建设点。"
        with custom_voiceover_tts(voice_text_scene_05) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = self.create_subtitle_voice(voice_text_scene_05)

            # 过渡：淡入新背景、场景编号、底部字幕和标题
            self.play(
                AnimationGroup(
                    FadeIn(bg5),
                    FadeIn(scene_num_05),
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5),
                    lag_ratio=0.0
                ),
                run_time=1.5
            )

            # 主要内容动画
            self.play(FadeIn(year, run_time=0.5))
            # 荣誉逐条出现
            self.play(FadeIn(honor1, shift=UP * 0.2, run_time=1.0))
            self.play(FadeIn(honor2, shift=UP * 0.2, run_time=1.0))

            # 计算剩余等待时间
            elapsed_time = 1.5 + 0.5 + 1.0 + 1.0 # 标题 + 年份 + honor1 + honor2
            fade_out_duration = 1.0
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1)

    # --- 场景 06: 水利水电 - 学分构成 ---
    def play_scene_06(self):
        """播放水利水电专业学分构成场景。"""
        # 背景 (保持)
        bg6 = self.create_solid_background(MY_BLUE_A)
        self.add(bg6)
        # 场景编号
        scene_num_06 = self.get_scene_number("06")
        self.add(scene_num_06)

        # 专业标题 (保持) - 需要重新添加，因为 clear_and_reset 会清除
        title = Text("水利水电工程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)
        self.add(title) # 直接添加，不加动画

        # 内容
        total_credit_label = Text("总学分", font_size=36, color=MY_WHITE)
        total_credit_value = Text("166 + 10 学分", font_size=60, color=MY_GOLD) # 突出数值
        group_total = VGroup(total_credit_label, total_credit_value).arrange(DOWN, buff=0.3).move_to(UP * 0.5)

        grad_credit_label = Text("毕业设计", font_size=36, color=MY_WHITE)
        grad_credit_value = Text("12 学分", font_size=60, color=MY_GOLD) # 保持字号一致
        group_grad = VGroup(grad_credit_label, grad_credit_value).arrange(DOWN, buff=0.3).next_to(group_total, DOWN, buff=1.0)

        # 旁白与动画
        voice_text_scene_06 = "水利水电工程专业的总学分是 166 加 10 学分。其中，毕业设计占 12 学分。"
        with custom_voiceover_tts(voice_text_scene_06) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = self.create_subtitle_voice(voice_text_scene_06)

            self.play(FadeIn(subtitle_voice, run_time=0.5)) # 字幕先出现

            # 内容动画
            self.play(GrowFromCenter(group_total, run_time=1.0))
            self.wait(0.5) # 停顿
            self.play(FadeIn(group_grad, run_time=1.0))

            # 计算剩余等待时间
            elapsed_time = 0.5 + 1.0 + 0.5 + 1.0 # 字幕 + total + 停顿 + grad
            fade_out_duration = 1.0
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1)

    # --- 场景 07: 水利水电 - 专业核心课程 (修改版) ---
    def play_scene_07(self):
        """播放水利水电专业核心课程场景 (使用手动列表)。"""
        # 背景 (保持)
        bg7 = self.create_solid_background(MY_BLUE_A)
        self.add(bg7)
        # 场景编号
        scene_num_07 = self.get_scene_number("07")
        self.add(scene_num_07)

        # 内容
        title = Text("专业核心课程", font_size=48, color=MY_WHITE)
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
        bullet_color = MY_WHITE
        text_color = MY_WHITE
        line_buff = 0.4 # 行间距
        bullet_text_buff = 0.2 # 项目符号和文本间距

        for item_text in course_items_text:
            bullet = Text("• ", font_size=item_font_size, color=bullet_color)
            # 使用 width 自动换行长文本
            text = Text(item_text, font_size=item_font_size, color=text_color, width=config.frame_width - 4)
            line = VGroup(bullet, text).arrange(RIGHT, buff=bullet_text_buff, aligned_edge=UP) # 符号与文本顶部对齐
            course_list_group.add(line)

        course_list_group.arrange(DOWN, buff=line_buff, aligned_edge=LEFT)
        course_list_group.next_to(title, DOWN, buff=0.8).align_to(LEFT)
        # 微调水平位置
        course_list_group.shift(LEFT * (config.frame_width/4 - course_list_group.get_width()/2))


        # --- 旁白与动画 ---
        voice_text_scene_07 = "水利水电工程的核心课程包括：工程水文与水资源综合利用、水工建筑物、水电站，以及水利工程施工与管理。"
        with custom_voiceover_tts(voice_text_scene_07) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)
            subtitle_voice = self.create_subtitle_voice(voice_text_scene_07)

            self.play(
                AnimationGroup(
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.0),
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # 列表项逐项 FadeIn
            animations = []
            total_list_anim_time = 3.0
            num_items = len(course_list_group)
            lag_ratio_val = 0.5
            denominator = (1 + (num_items - 1) * lag_ratio_val)
            run_time_per_item = total_list_anim_time / denominator if denominator > 0 else total_list_anim_time

            for item_line in course_list_group:
                 animations.append(FadeIn(item_line, shift=UP*0.2, run_time=run_time_per_item))

            if animations:
                self.play(AnimationGroup(*animations, lag_ratio=lag_ratio_val), run_time=total_list_anim_time)

            # 计算剩余等待时间
            elapsed_time = 1.0 + total_list_anim_time
            fade_out_duration = 1.0
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)
            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1)


    # --- 场景 08: 自主发展计划 - 美育 ---
    def play_scene_08(self):
        """播放自主发展计划美育场景。"""
        # 背景 (切换)
        bg8 = self.create_solid_background(MY_BEIGE) # 米色
        # 场景编号 (使用黑色以适应背景)
        scene_num_08 = self.get_scene_number("08", color=MY_BLACK)

        # 内容 (使用黑色字体)
        title = Text("自主发展计划（第二课堂）", font_size=48, color=MY_BLACK)
        title.to_edge(UP, buff=1.5)

        label = Text("美育", font_size=40, color=MY_BLUE_C) # 标签用蓝色
        practice = Text("美育实践", font_size=40, color=MY_BLACK, weight=BOLD)
        content_group = VGroup(label, practice).arrange(DOWN, buff=0.4)
        content_group.next_to(title, DOWN, buff=1.0)

        # 可选图标 (简单画笔形状 - 使用 SVG 或 Manim 内置形状)
        try:
            # 尝试加载 SVG 图标 (需要提供 SVG 文件路径)
            # icon = SVGMobject("path/to/paintbrush.svg").scale(0.5).set_color(MY_ORANGE)
            # 如果没有 SVG，用 Manim 形状模拟
            # 创建一个简单的画笔形状 (矩形+三角形)
            handle = Rectangle(height=0.8, width=0.2, fill_color=BROWN, fill_opacity=1, stroke_width=0)
            bristles = Triangle(fill_color=MY_ORANGE, fill_opacity=1, stroke_width=0).scale(0.2).next_to(handle, DOWN, buff=0)
            icon = VGroup(handle, bristles).scale(0.8) # 调整整体大小
        except Exception as e:
            print(f"创建画笔图标时出错: {e}. 使用圆形替代。")
            icon = Circle(radius=0.3, color=MY_ORANGE, fill_opacity=0.8)

        icon.next_to(content_group, RIGHT, buff=0.5)


        # 旁白与动画
        voice_text_scene_08 = "在自主发展计划，也就是第二课堂中，美育部分要求完成美育实践。"
        with custom_voiceover_tts(voice_text_scene_08) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            # 字幕也用黑色
            subtitle_voice = self.create_subtitle_voice(voice_text_scene_08, color=MY_BLACK)

            # 过渡
            self.play(
                AnimationGroup(
                    FadeIn(bg8),
                    FadeIn(scene_num_08),
                    FadeIn(subtitle_voice, run_time=0.5),
                    Write(title, run_time=1.5),
                    lag_ratio=0.0
                ),
                run_time=1.5
            )

            # 主要内容动画 (内容和图标同时出现)
            self.play(
                AnimationGroup(
                    FadeIn(content_group, run_time=1.0),
                    FadeIn(icon, run_time=1.0),
                    lag_ratio=0.0
                ),
                run_time=1.0
            )

            # 计算剩余等待时间
            elapsed_time = 1.5 + 1.0 # 标题 + 内容/图标
            fade_out_duration = 1.0
            remaining_time = tracker.duration - elapsed_time - fade_out_duration
            if remaining_time > 0:
                self.wait(remaining_time)

            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)
        self.wait(1)

    # --- 场景 09: 结束画面 ---
    def play_scene_09(self):
        """播放结束画面场景。"""
        # 背景 (恢复渐变)
        bg9 = self.create_gradient_background(MY_BLUE_D, MY_TEAL_E)
        # 场景编号 (可选，这里不显示以保持简洁)
        # scene_num_09 = self.get_scene_number("09")

        # 内容
        end_text = Text("专业信息速览完毕", font_size=54, color=MY_WHITE)
        end_text.move_to(ORIGIN)
        more_info = Text("更多详细信息请查询官方网站", font_size=28, color=MY_LIGHT_GRAY)
        more_info.next_to(end_text, DOWN, buff=0.8)

        # 旁白与动画
        voice_text_scene_09 = "本次重庆交通大学专业信息速览到此结束。感谢您的观看！如果需要了解更详细的信息，请查询学校官方网站。"
        with custom_voiceover_tts(voice_text_scene_09) as tracker:
            self.add_sound(tracker.audio_path, time_offset=0)

            subtitle_voice = self.create_subtitle_voice(voice_text_scene_09)

            # 过渡 (淡入背景和字幕)
            self.play(
                AnimationGroup(
                    FadeIn(bg9),
                    # FadeIn(scene_num_09), # 如果需要显示编号
                    FadeIn(subtitle_voice, run_time=0.5),
                    lag_ratio=0.0
                ),
                run_time=0.5
            )

            # 主要内容动画
            self.play(FadeIn(end_text, run_time=1.5))
            self.play(FadeIn(more_info, run_time=1.0))

            # 计算动画和等待时间
            text_anim_time = 1.5 + 1.0
            fade_out_duration = 1.0
            # 相机缩放时间 = 总时长 - 字幕淡入 - 文字动画 - 字幕淡出
            # 确保相机缩放时间非负
            scale_anim_time = max(0, tracker.duration - 0.5 - text_anim_time - fade_out_duration)

            if scale_anim_time > 0.1: # 只有在有足够时间时才缩放
                 self.play(self.camera.frame.animate.scale(1.1), run_time=scale_anim_time)
            else:
                 # 如果时间太短，就不缩放，直接等待
                 wait_time = max(0, tracker.duration - 0.5 - text_anim_time - fade_out_duration)
                 if wait_time > 0:
                     self.wait(wait_time)


            # 淡出底部字幕
            self.play(FadeOut(subtitle_voice), run_time=fade_out_duration)

        # 结束停留
        self.wait(2)
        # clear_and_reset 会处理最后的淡出

# --- Main execution block ---
if __name__ == "__main__":
    # 基本配置
    config.pixel_height = 1080  # 设置分辨率高
    config.pixel_width = 1920  # 设置分辨率宽
    config.frame_rate = 30  # 设置帧率
    config.output_file = "CombinedScene"  # 指定输出文件名
    config.disable_caching = True # 禁用缓存，确保每次都重新生成

    # 临时设置输出目录,必须使用#(output_video)
    config.media_dir = "intro_majoy"

    # 实例化并渲染场景
    scene = CombinedScene()
    try:
        scene.render()
        print(f"Scene rendering finished. Output file: {config.output_file}.mp4 in {config.media_dir}")
    except Exception as e:
        print(f"An error occurred during rendering: {e}")