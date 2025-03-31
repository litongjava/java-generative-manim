# -*- coding: utf-8 -*-
import os
import numpy as np
from manim import *

# 自定义颜色 (根据需求添加)
# MY_LIGHT_GRAY = "#D1D5DB" # Manim 的 LIGHT_GRAY 已经足够好用
MY_BEIGE = "#F5F5DC" # 米色
MY_WHITE = "#FFFFFF" # 白色
MY_BLACK = "#000000" # 黑色

# --- Main Scene Class ---
class CombinedScene(MovingCameraScene):
    """
    Manim 动画场景，用于展示重庆交通大学两个专业的关键信息速览。
    包含多个场景，展示不同信息点，并有背景切换和动画效果。
    """
    def construct(self):
        """
        构建整个动画序列，按顺序播放各个场景。
        """
        # 场景〇：开场标题
        self.play_scene_00()
        self.clear_and_reset()

        # 场景一：港口航道与海岸工程 - 关键年份
        self.play_scene_01()
        self.clear_and_reset()

        # 场景二：港口航道与海岸工程 - 学分要求
        self.play_scene_02()
        self.clear_and_reset()

        # 场景三：港口航道与海岸工程 - 专业核心课程
        self.play_scene_03()
        self.clear_and_reset()

        # 场景四：港口航道与海岸工程 - 特定课程信息
        self.play_scene_04()
        self.clear_and_reset()

        # 场景五：水利水电工程 - 关键年份与荣誉
        self.play_scene_05()
        self.clear_and_reset()

        # 场景六：水利水电工程 - 学分构成
        self.play_scene_06()
        self.clear_and_reset()

        # 场景七：水利水电工程 - 专业核心课程
        self.play_scene_07()
        self.clear_and_reset()

        # 场景八：自主发展计划 - 美育
        self.play_scene_08()
        self.clear_and_reset()

        # 场景九：结束画面
        self.play_scene_09()
        # 结束时不需要 clear_and_reset，让最后一幕停留

    def clear_and_reset(self):
        """
        清除当前场景所有对象并重置相机。
        在场景切换时调用，确保内容不残留，坐标系一致。
        """
        # 获取当前场景中所有非 None 的 Mobject
        valid_mobjects = [m for m in self.mobjects if m is not None]
        # 清除所有对象的更新器，防止残留的 updater 导致错误
        for mob in valid_mobjects:
            mob.clear_updaters()
        # 将所有有效对象放入一个 Group 中以便一次性 FadeOut
        all_mobjects_group = Group(*valid_mobjects)
        if all_mobjects_group: # 只有在场景中有对象时才执行 FadeOut
            self.play(FadeOut(all_mobjects_group, shift=DOWN * 0.5), run_time=0.5)
        # Manim 的 self.clear() 会移除场景中的所有 Mobject
        self.clear()
        # 重置相机位置到原点 (0, 0, 0)
        self.camera.frame.move_to(ORIGIN)
        # 重置相机框架的宽度和高度为配置中的默认值
        # 使用 config 而不是 self.camera 获取全局配置的宽高，确保一致性
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        # 短暂等待，让场景切换更平滑
        self.wait(0.1)

    def get_scene_number(self, number_str):
        """
        创建并定位场景编号文本。
        Args:
            number_str (str): 要显示的场景编号字符串，例如 "01"。
        Returns:
            Text: 配置好位置和样式的场景编号 Mobject。
        """
        scene_num = Text(number_str, font_size=24, color=MY_WHITE)
        # 定位到右上角，并设置一定的边距
        scene_num.to_corner(UR, buff=0.5)
        # 设置 Z 轴索引，确保编号在最顶层，不被其他元素遮挡
        scene_num.set_z_index(10)
        return scene_num

    def create_background(self, color=BLACK, opacity=1.0, gradient_colors=None, gradient_direction=DR):
        """
        创建覆盖全屏的背景矩形。
        Args:
            color: 背景颜色 (如果不是渐变)。
            opacity: 背景不透明度。
            gradient_colors: 渐变颜色列表 (例如 [BLUE_D, TEAL_E])。
            gradient_direction: 渐变方向 (例如 DR)。
        Returns:
            Rectangle: 配置好的背景 Mobject。
        """
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0, # 无边框
            fill_opacity=opacity
        )
        if gradient_colors:
            bg.set_fill(color=gradient_colors, opacity=opacity)
            # 注意：Manim CE v0.19.0 中 Rectangle 的渐变是通过 fill_color 参数直接传递列表实现的
            # 如果需要更复杂的渐变控制，可能需要查阅最新文档或使用 Shader
            # 简单线性渐变可以直接用颜色列表
            bg.set_style(fill_color=gradient_colors)
            # Manim似乎没有直接的gradient_direction参数给Rectangle, 渐变方向可能需要更复杂设置或默认为从上到下
            # 模拟从左上到右下，可能需要手动创建顶点颜色或使用着色器
            # 暂时使用默认渐变方向或纯色
            # 更新：Manim v0.18+ 可以直接在 fill_color 传列表实现渐变，但方向控制可能有限
            # 为了确保效果，这里使用一个近似的实现方式，或者直接用纯色/简单渐变
            # 修正：直接将列表传给 fill_color 即可，方向可能需要调整或接受默认
            bg.fill_color = gradient_colors # 尝试直接赋值
        else:
            bg.set_fill(color=color, opacity=opacity)

        bg.set_z_index(-10) # 置于最底层
        return bg

    # --- Scene 00: Opening Title ---
    def play_scene_00(self):
        """场景〇：开场标题"""
        # 背景：蓝绿色渐变 (左上到右下)
        # 注意：Manim CE v0.19 对 Rectangle 渐变方向支持可能有限，这里尝试用列表
        bg0 = self.create_background(gradient_colors=[BLUE_D, TEAL_E])
        # 如果渐变方向不符合预期，可以考虑用纯色或查找更新的渐变方法
        self.add(bg0)

        # 主标题
        title = Text("重庆交通大学 专业信息速览", font_size=60, color=MY_WHITE)
        title.move_to(UP * 1.5) # 屏幕中心偏上

        # 副标题
        subtitle = Text("港口航道与海岸工程 & 水利水电工程", font_size=40, color=LIGHT_GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 动画
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle, shift=DOWN * 0.5), run_time=1.5)
        self.wait(1)

    # --- Scene 01: Port & Channel - Key Years ---
    def play_scene_01(self):
        """场景一：港口航道与海岸工程 - 关键年份"""
        # 背景：浅灰色
        bg1 = self.create_background(color=GRAY_B)
        self.add(bg1)

        # 场景编号
        scene_num_01 = self.get_scene_number("01")
        self.add(scene_num_01)

        # 顶部标题
        title = Text("港口航道与海岸工程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)
        self.play(Write(title), run_time=1.5)

        # 左侧内容
        year_left = Text("2009年", font_size=36, color=GOLD_E, weight=BOLD)
        event_left = Text("评为国家级特色专业", font_size=32, color=MY_WHITE)
        group_left = VGroup(year_left, event_left).arrange(DOWN, buff=0.3, aligned_edge=LEFT) # 左对齐
        group_left.next_to(title, DOWN, buff=1.0).to_edge(LEFT, buff=2.0)

        # 右侧内容
        year_right = Text("2017年", font_size=36, color=GOLD_E, weight=BOLD)
        # 使用 width 实现长文本自动换行
        event_right = Text("通过全国工程教育专业认证复评", font_size=32, color=MY_WHITE, width=config.frame_width / 3 - 1) # 减1确保在边界内
        group_right = VGroup(year_right, event_right).arrange(DOWN, buff=0.3, aligned_edge=LEFT) # 左对齐
        group_right.next_to(title, DOWN, buff=1.0).to_edge(RIGHT, buff=2.0)

        # 动画
        self.play(FadeIn(group_left, shift=LEFT * 2), run_time=1)
        self.wait(0.5) # 稍作停顿
        self.play(FadeIn(group_right, shift=RIGHT * 2), run_time=1)
        self.wait(1)

    # --- Scene 02: Port & Channel - Credit Requirement ---
    def play_scene_02(self):
        """场景二：港口航道与海岸工程 - 学分要求"""
        # 背景：保持浅灰色
        bg2 = self.create_background(color=GRAY_B)
        self.add(bg2)

        # 场景编号
        scene_num_02 = self.get_scene_number("02")
        self.add(scene_num_02)

        # 问题文本
        question = Text("最低毕业学分要求？", font_size=48, color=BLUE_C)
        question.move_to(UP * 0.5)

        # 答案文本
        answer = Text("180 学分", font_size=72, color=MY_WHITE, weight=BOLD) # 加粗突出
        answer.next_to(question, DOWN, buff=0.8)

        # 动画
        # 注意：Text 是非矢量对象，不能用 Write。改用 FadeIn。
        self.play(FadeIn(question), run_time=1)
        self.play(GrowFromCenter(answer), run_time=1)
        self.wait(1)

    # --- Scene 03: Port & Channel - Core Courses ---
    def play_scene_03(self):
        """场景三：港口航道与海岸工程 - 专业核心课程"""
        # 背景：保持浅灰色
        bg3 = self.create_background(color=GRAY_B)
        self.add(bg3)

        # 场景编号
        scene_num_03 = self.get_scene_number("03")
        self.add(scene_num_03)

        # 标题
        title = Text("专业核心课程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)
        # 注意：Text 是非矢量对象，不能用 Write。改用 FadeIn。
        self.play(FadeIn(title), run_time=1)

        # 核心课程列表
        courses = [
            "渠化工程",
            "港口规划与布置",
            "航道整治",
            "工程项目管理",
            "港口与海岸水工建筑物"
        ]
        # 使用 VGroup 和 FadeIn 实现逐项显示
        course_mobjects = VGroup(*[Text(course, font_size=36, color=MY_WHITE) for course in courses])
        # arrange 默认垂直居中对齐，若需左对齐用 aligned_edge=LEFT
        course_mobjects.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        course_mobjects.next_to(title, DOWN, buff=0.8)
        # 将列表整体移到屏幕中心偏左的位置
        course_mobjects.move_to(ORIGIN + LEFT * 3)

        # 动画：逐项 FadeIn
        # 使用 AnimationGroup 并设置 lag_ratio 实现逐项延迟出现
        animations = [FadeIn(item, shift=UP*0.2) for item in course_mobjects]
        self.play(AnimationGroup(*animations, lag_ratio=0.5), run_time=3) # 总时长3秒，lag_ratio控制间隔
        self.wait(1)

    # --- Scene 04: Port & Channel - Specific Course Info ---
    def play_scene_04(self):
        """场景四：港口航道与海岸工程 - 特定课程信息"""
        # 背景：保持浅灰色
        bg4 = self.create_background(color=GRAY_B)
        self.add(bg4)

        # 场景编号
        scene_num_04 = self.get_scene_number("04")
        self.add(scene_num_04)

        # 上半部分信息
        course_name1 = Text("水工钢筋混凝土结构综合实践", font_size=36, color=MY_WHITE)
        course_term1 = Text("第 5 学期 开设", font_size=36, color=GOLD_E, weight=BOLD) # 突出显示
        group_top = VGroup(course_name1, course_term1).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        group_top.move_to(UP * 1.5 + LEFT * 2) # 移到左上方

        # 下半部分信息
        course_name2 = Text("数学建模课程代码", font_size=36, color=MY_WHITE)
        course_code2 = Text("19210919", font_size=48, color=GOLD_E, weight=BOLD) # 字号稍大，突出
        group_bottom = VGroup(course_name2, course_code2).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        group_bottom.move_to(DOWN * 1.5 + LEFT * 2) # 移到左下方

        # 动画
        self.play(FadeIn(group_top), run_time=1)
        self.wait(0.5)
        self.play(FadeIn(group_bottom), run_time=1)
        self.wait(1)

    # --- Scene 05: Hydraulic Engineering - Key Year & Honors ---
    def play_scene_05(self):
        """场景五：水利水电工程 - 关键年份与荣誉"""
        # 背景：浅蓝色 (替代水波纹)
        bg5 = self.create_background(color=BLUE_A) # 使用浅蓝色
        self.add(bg5)

        # 场景编号
        scene_num_05 = self.get_scene_number("05")
        self.add(scene_num_05)

        # 顶部标题
        title = Text("水利水电工程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)
        # 注意：Text 是非矢量对象，不能用 Write。改用 FadeIn。
        self.play(FadeIn(title), run_time=1.5)

        # 年份标识
        year = Text("2013年", font_size=40, color=GOLD_E, weight=BOLD)
        year.next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(year), run_time=0.5)

        # 荣誉列表
        honors = [
            "入选教育部‘卓越工程师教育培养计划’试点专业",
            "入选重庆市‘三特行动计划’首批特色专业建设点"
        ]
        # 使用 width 和 should_center 实现长文本自动换行和居中
        honor_mobjects = VGroup(*[Text(h, font_size=32, color=MY_WHITE, width=config.frame_width * 0.7, should_center=True) for h in honors])
        honor_mobjects.arrange(DOWN, buff=0.4)
        honor_mobjects.next_to(year, DOWN, buff=0.8)

        # 动画：逐条 FadeIn 上移
        animations = [FadeIn(item, shift=UP * 0.2) for item in honor_mobjects]
        self.play(AnimationGroup(*animations, lag_ratio=0.7), run_time=len(honors)*1.0) # 每条1秒
        self.wait(1)

    # --- Scene 06: Hydraulic Engineering - Credit Composition ---
    def play_scene_06(self):
        """场景六：水利水电工程 - 学分构成"""
        # 背景：保持浅蓝色
        bg6 = self.create_background(color=BLUE_A)
        self.add(bg6)

        # 场景编号
        scene_num_06 = self.get_scene_number("06")
        self.add(scene_num_06)

        # 专业标题（保持显示，不加动画）
        title = Text("水利水电工程", font_size=48, color=MY_WHITE)
        title.to_edge(UP, buff=1.0)
        self.add(title) # 直接添加，不播放动画

        # 总学分信息
        total_credit_label = Text("总学分", font_size=40, color=MY_WHITE)
        total_credit_value = Text("166 + 10 学分", font_size=60, color=GOLD_E, weight=BOLD) # 突出
        group_total_credit = VGroup(total_credit_label, total_credit_value).arrange(DOWN, buff=0.3)
        group_total_credit.move_to(UP * 0.5)

        # 毕业设计学分信息
        thesis_credit_label = Text("毕业设计", font_size=40, color=MY_WHITE)
        thesis_credit_value = Text("12 学分", font_size=60, color=GOLD_E, weight=BOLD) # 字号相近，加粗
        group_thesis_credit = VGroup(thesis_credit_label, thesis_credit_value).arrange(DOWN, buff=0.3)
        group_thesis_credit.next_to(group_total_credit, DOWN, buff=1.0)

        # 动画
        # GrowFromCenter 适用于 VMobject，Text 是非矢量对象，改用 FadeIn 或 ScaleInPlace
        self.play(FadeIn(group_total_credit, scale=0.5), run_time=1) # 使用 FadeIn 并稍微缩放
        self.wait(0.5)
        self.play(FadeIn(group_thesis_credit, scale=0.5), run_time=1)
        self.wait(1)

    # --- Scene 07: Hydraulic Engineering - Core Courses ---
    def play_scene_07(self):
        """场景七：水利水电工程 - 专业核心课程"""
        # 背景：保持浅蓝色
        bg7 = self.create_background(color=BLUE_A)
        self.add(bg7)

        # 场景编号
        scene_num_07 = self.get_scene_number("07")
        self.add(scene_num_07)

        # 专业标题（保持显示）
        title_major = Text("水利水电工程", font_size=48, color=MY_WHITE)
        title_major.to_edge(UP, buff=1.0)
        self.add(title_major) # 直接添加

        # 课程标题
        title_courses = Text("专业核心课程", font_size=48, color=MY_WHITE)
        title_courses.next_to(title_major, DOWN, buff=0.8) # 放在专业标题下方
        # 注意：Text 是非矢量对象，不能用 Write。改用 FadeIn。
        self.play(FadeIn(title_courses), run_time=1)

        # 核心课程列表
        courses = [
            "工程水文与水资源综合利用",
            "水工建筑物",
            "水电站",
            "水利工程施工与管理"
        ]
        # 使用 width 和 should_center 实现长文本自动换行和居中
        course_mobjects = VGroup(*[Text(course, font_size=36, color=MY_WHITE, width=config.frame_width*0.8, should_center=True) for course in courses])
        course_mobjects.arrange(DOWN, buff=0.4)
        course_mobjects.next_to(title_courses, DOWN, buff=0.8)

        # 动画：逐项 FadeIn
        animations = [FadeIn(item, shift=UP*0.2) for item in course_mobjects]
        self.play(AnimationGroup(*animations, lag_ratio=0.5), run_time=3)
        self.wait(1)

    # --- Scene 08: Self-Development Plan - Aesthetics ---
    def play_scene_08(self):
        """场景八：自主发展计划 - 美育"""
        # 背景：米色
        bg8 = self.create_background(color=MY_BEIGE) # 使用米色
        self.add(bg8)

        # 场景编号 (白色在米色上可能不清晰，改为黑色)
        scene_num_08 = self.get_scene_number("08").set_color(MY_BLACK)
        self.add(scene_num_08)

        # 标题 (使用黑色字体以确保对比度)
        title = Text("自主发展计划（第二课堂）", font_size=48, color=MY_BLACK)
        title.to_edge(UP, buff=1.5)
        # 注意：Text 是非矢量对象，不能用 Write。改用 FadeIn。
        self.play(FadeIn(title), run_time=1.5)

        # 内容 (使用黑色和蓝色字体)
        label = Text("美育", font_size=40, color=BLUE_C) # 蓝色标签
        practice = Text("美育实践", font_size=40, color=MY_BLACK, weight=BOLD) # 黑色加粗实践内容
        group_content = VGroup(label, practice).arrange(DOWN, buff=0.4)
        group_content.next_to(title, DOWN, buff=1.0)

        # 动画
        self.play(FadeIn(group_content), run_time=1)
        # 提示：如果需要添加图标，可以使用 SVGMobject 或 ImageMobject 并用 FadeIn 动画
        # 例如: icon = SVGMobject("path/to/icon.svg").scale(0.5).next_to(group_content, RIGHT)
        # self.play(FadeIn(icon))
        self.wait(1)

    # --- Scene 09: Ending Screen ---
    def play_scene_09(self):
        """场景九：结束画面"""
        # 背景：恢复蓝绿色渐变
        bg9 = self.create_background(gradient_colors=[BLUE_D, TEAL_E])
        self.add(bg9)

        # 场景编号 (可选，如果需要显示)
        scene_num_09 = self.get_scene_number("09")
        self.add(scene_num_09)

        # 结束语
        ending_text = Text("专业信息速览完毕 🎉", font_size=48, color=MY_WHITE) # 加个表情
        ending_text.move_to(ORIGIN)

        # 提示信息
        more_info_text = Text("更多详细信息请查询官方网站", font_size=28, color=LIGHT_GRAY)
        more_info_text.next_to(ending_text, DOWN, buff=0.8)

        # 动画
        self.play(FadeIn(ending_text), run_time=1.5)
        self.play(FadeIn(more_info_text), run_time=1)

        # 相机轻微缩小，营造结束感
        self.play(self.camera.frame.animate.scale(1.1), run_time=1.5)
        self.wait(2) # 停留2秒

        # 最终淡出整个场景
        # 获取当前所有对象进行淡出
        all_final_mobjects = Group(*self.mobjects)
        if all_final_mobjects:
            self.play(FadeOut(all_final_mobjects), run_time=1)
        self.wait(0.5) # 结束前的短暂等待


# --- Main execution block ---
if __name__ == "__main__":
    # 基本配置
    config.pixel_height = 1080  # 设置分辨率高
    config.pixel_width = 1920  # 设置分辨率宽
    config.frame_rate = 30  # 设置帧率
    config.output_file = "CombinedScene"  # 指定输出文件名
    config.disable_caching = True # 禁用缓存，确保每次都重新生成

    # 临时设置输出目录,必须使用#(output_video)
    # 注意：'#(output_video)' 是一个占位符，需要被外部程序替换为实际路径
    # 如果直接运行此脚本，需要手动修改为有效目录，例如 "./media_output"
    config.media_dir = "./#(output_video)"

    # 检查输出目录是否存在，如果不存在则创建
    output_dir = config.media_dir
    if output_dir == "./#(output_video)":
        print("警告：输出目录未被替换，将尝试在当前目录下创建 './output_video' 文件夹。")
        output_dir = "./output_video"
        config.media_dir = output_dir # 更新配置中的路径

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"输出目录 '{output_dir}' 已创建。")
        except OSError as e:
            print(f"错误：无法创建输出目录 '{output_dir}': {e}")
            # 可以选择退出或使用默认的 media 目录
            # config.media_dir = "./media" # 回退到默认

    # 实例化并渲染场景
    scene = CombinedScene()
    try:
        scene.render()
        print(f"场景渲染完成。视频文件位于: {os.path.join(config.media_dir, 'videos', str(config.pixel_width), str(config.frame_rate), config.output_file + '.mp4')}")
    except Exception as e:
        print(f"渲染过程中发生错误: {e}")
