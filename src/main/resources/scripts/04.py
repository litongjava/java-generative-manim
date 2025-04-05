# -*- coding: utf-8 -*-
import numpy as np
from manim import *

# 自定义颜色
MY_DARK_BLUE = "#1E3A8A"  # 深蓝色
MY_LIGHT_GRAY = "#F3F4F6"  # 浅灰色
MY_MEDIUM_GRAY = "#D1D5DB"  # 中灰色
MY_GOLD = "#F59E0B"  # 金色
MY_ORANGE = "#F97316"  # 橙色
MY_RED = "#DC2626"  # 红色
MY_WHITE = "#FFFFFF"  # 白色
MY_BLACK = "#000000"  # 黑色


class CombinedScene(MovingCameraScene):
    """
    合并所有场景的 Manim 动画。
    用于讲解如何求解函数 f(x) = x^2 的切线方程。
    """

    def construct(self):
        # 用于跟踪动画时间的变量
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
        # 使用 Group(*self.mobjects) 包含所有类型的对象
        # Filter out None values which might appear in self.mobjects
        valid_mobjects = [m for m in self.mobjects if m is not None]
        all_mobjects = Group(*valid_mobjects)

        # 停止所有 updater
        for mob in self.mobjects:
            if mob is not None:
                mob.clear_updaters()

        if all_mobjects:  # Only play FadeOut if there are objects
            self.play(FadeOut(all_mobjects, shift=DOWN * 0.5), run_time=0.5)

        self.clear()  # 清除 Manim 内部列表

        # 重置相机位置和缩放
        self.camera.frame.move_to(ORIGIN)
        # 使用 camera 的属性来设置宽高，确保一致性
        # Use config values as they are reliable frame dimensions
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 重置时间跟踪器 (如果需要每个场景独立计时)
        self.scene_time_tracker.set_value(0)
        # 短暂等待，确保过渡自然
        self.wait(0.5)

    def star_updater(self, star, dt):
        """更新星星透明度的函数，实现闪烁效果"""
        # 获取星星存储的基础透明度和闪烁频率/相位
        # 使用 getattr with default values
        base_opacity = getattr(star, "base_opacity", 0.5)  # 默认基础透明度
        frequency = getattr(star, "frequency", 0.5)  # 默认频率
        phase = getattr(star, "phase", 0)  # 默认相位

        # 使用 scene_time_tracker 的值
        current_time = self.scene_time_tracker.get_value()
        # 基于正弦波计算当前透明度
        opacity_variation = 0.4 * np.sin(2 * PI * frequency * current_time + phase)
        target_opacity = base_opacity + opacity_variation
        # 限制透明度在 [0.1, 0.9] 范围内，避免完全消失或完全不透明
        target_opacity = np.clip(target_opacity, 0.1, 0.9)
        # 使用 .set_opacity() 设置透明度
        star.set_opacity(target_opacity)

        # 注意：时间更新应该由 self.play 或 self.wait 驱动，而不是在 updater 内部递增

    def play_scene_01(self):
        """场景一：欢迎介绍与星空背景"""
        # 0. 重置时间跟踪器
        self.scene_time_tracker.set_value(0)

        # 1. 背景设计：深蓝色背景 + 闪烁星空
        bg1 = Rectangle(
            # 使用 config 的值来确保覆盖全屏
            width=config.frame_width,
            height=config.frame_height,
            fill_color=MY_DARK_BLUE,
            fill_opacity=1.0,  # Use float for opacity
            stroke_width=0
        )
        bg1.set_z_index(-10)  # 确保背景在最底层
        self.add(bg1)

        # 创建星星
        stars = VGroup()
        num_stars = 200
        for _ in range(num_stars):
            # 在摄像机框架内随机选择位置
            x_pos = np.random.uniform(-config.frame_width / 2, config.frame_width / 2)
            y_pos = np.random.uniform(-config.frame_height / 2, config.frame_height / 2)
            # 不要直接在 Dot 构造函数中设置 opacity
            star_dot = Dot(point=[x_pos, y_pos, 0], radius=0.02, color=MY_WHITE)

            # 存储基础透明度、频率和相位作为对象的属性
            base_op = np.random.uniform(0.3, 0.7)
            freq = np.random.uniform(0.3, 0.8)
            phase_val = np.random.uniform(0, 2 * PI)
            # 直接设置属性
            star_dot.base_opacity = base_op
            star_dot.frequency = freq
            star_dot.phase = phase_val

            # 初始设置透明度使用 .set_opacity()
            star_dot.set_opacity(base_op)
            stars.add(star_dot)

        # 添加星星闪烁的 updater
        # Pass the updater function directly to add_updater
        stars.add_updater(self.star_updater)
        self.add(stars)  # Add stars after setting up updater

        # 2. 场景编号
        scene_num_01 = self.get_scene_number("01")
        scene_num_01.set_z_index(10)  # 确保在顶层
        self.add(scene_num_01)

        # 3. 主要内容：标题和副标题
        title = Text("大家好，欢迎来到本期数学讲解视频 👋", font_size=48, color=MY_WHITE)
        title.shift(UP * 2.5)

        subtitle_part1 = Text("如何求解函数", font_size=36, color=MY_WHITE)
        subtitle_part2 = MathTex("f(x)=x^2", font_size=42, color=MY_ORANGE)  # LaTeX公式
        subtitle_part3 = Text("的切线方程 🤔", font_size=36, color=MY_WHITE)

        subtitle = VGroup(subtitle_part1, subtitle_part2, subtitle_part3).arrange(RIGHT, buff=0.2)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 4. 动画效果
        # Use FadeIn for Text objects
        self.play(FadeIn(title, shift=UP * 0.5), run_time=1.5)
        self.wait(0.5)
        # 分别对 Text 和 MathTex 应用动画
        self.play(
            FadeIn(subtitle_part1, shift=RIGHT * 0.2),
            Write(subtitle_part2),  # Write works for MathTex (VMobject)
            FadeIn(subtitle_part3, shift=LEFT * 0.2),
            run_time=2
        )
        self.wait(1)

        # 5. 相机轻微移动 (向外移动等效于缩小画面)
        # Scale the camera frame, 1.05 means zoom out slightly
        self.play(self.camera.frame.animate.scale(1.05), run_time=1.5)
        self.wait(1)

        # 驱动时间更新器，让星星闪烁
        # Animate the value tracker, which the updater uses
        self.play(self.scene_time_tracker.animate.set_value(5), run_time=5, rate_func=linear)
        self.wait(1)

    def play_scene_02(self):
        """场景二：切线概念与问题背景介绍"""
        # 1. 背景与布局
        bg2 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=MY_LIGHT_GRAY,
            fill_opacity=1.0,
            stroke_width=0
        )
        bg2.set_z_index(-10)
        self.add(bg2)

        # 2. 场景编号
        scene_num_02 = self.get_scene_number("02")
        scene_num_02.set_color(MY_BLACK)  # 浅色背景用黑色字
        scene_num_02.set_z_index(10)
        self.add(scene_num_02)

        # 3. 内容呈现
        # 左侧文字说明 (使用 VGroup for mixed Text/MathTex)
        text_left_part1 = Text("切线是曲线在某一点的瞬时方向 📏", font_size=28, color=MY_BLACK)
        text_left_part2 = Text("在函数", font_size=28, color=MY_BLACK)
        text_left_part3 = MathTex("f(x)=x^2", font_size=32, color=MY_DARK_BLUE)
        text_left_part4 = Text("中,", font_size=28, color=MY_BLACK)
        text_left_part5 = Text("切线反映了曲线在该点的斜率变化📈", font_size=28, color=MY_BLACK)

        # Arrange parts carefully
        line1 = VGroup(text_left_part1).arrange(RIGHT, buff=0.1)
        line2 = VGroup(text_left_part2, text_left_part3, text_left_part4).arrange(RIGHT, buff=0.1)
        line3 = VGroup(text_left_part5).arrange(RIGHT, buff=0.1)

        text_left = VGroup(line1, line2, line3).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        text_left.to_edge(LEFT, buff=1)

        # 右侧坐标系与函数图像
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
            x_length=6,
            y_length=5,
            # Use stroke_opacity for axes transparency if needed, not opacity in axis_config
            axis_config={"color": MY_BLACK, "include_tip": True, "include_numbers": True, "stroke_width": 2},
            x_axis_config={"numbers_to_include": np.arange(-3, 4, 1)},
            y_axis_config={"numbers_to_include": np.arange(0, 10, 2)},
        )
        # 添加坐标轴标签
        x_label = axes.get_x_axis_label("x", edge=RIGHT, direction=DOWN, buff=0.2)
        y_label = axes.get_y_axis_label("f(x)", edge=UP, direction=LEFT, buff=0.2)
        axes_labels = VGroup(x_label, y_label).set_color(MY_BLACK)

        # 绘制函数 f(x) = x^2
        parabola = axes.plot(lambda x: x ** 2, x_range=[-3, 3], color=MY_DARK_BLUE, stroke_width=3)
        # Use get_graph_label and then set font size
        parabola_label_obj = axes.get_graph_label(parabola, label="f(x)=x^2", x_val=-2, direction=UL, buff=0.3)
        parabola_label_obj.set_color(MY_DARK_BLUE)
        parabola_label_obj.set_font_size(24)  # Set font size after creation

        # 标记切点 (a, a^2)，取 a=1
        a = 1
        tangent_point_coords = axes.c2p(a, a ** 2)  # 坐标系到屏幕坐标
        # Don't set opacity in constructor
        tangent_point_dot = Dot(point=tangent_point_coords, color=MY_RED, radius=0.1)
        # Set initial opacity if needed (though default is 1.0)
        # tangent_point_dot.set_opacity(1.0)

        # 为点添加脉动效果的 updater
        # Use scene_time_tracker for animation timing
        tangent_point_dot.add_updater(
            lambda mob: mob.set(width=0.1 * (1 + 0.2 * np.sin(3 * self.scene_time_tracker.get_value())))
        )

        # 将右侧元素组合并定位
        graph_group = VGroup(axes, axes_labels, parabola, parabola_label_obj, tangent_point_dot)
        graph_group.to_edge(RIGHT, buff=1)

        # 垂直对齐：将图形组的中心 Y 坐标对齐到文本组的中心 Y 坐标
        graph_group.move_to([graph_group.get_center()[0], text_left.get_center()[1], 0])

        # 4. 动画效果
        # 渐显文字 (FadeIn for Text, Write for MathTex)
        self.play(FadeIn(text_left_part1), run_time=1)
        self.play(
            FadeIn(text_left_part2, shift=RIGHT * 0.1),
            Write(text_left_part3),
            FadeIn(text_left_part4, shift=LEFT * 0.1),
            run_time=1.5
        )
        self.play(FadeIn(text_left_part5), run_time=1)
        self.wait(0.5)

        # 创建坐标轴和图像
        self.play(Create(axes), Write(axes_labels), run_time=1.5)
        self.play(Create(parabola), Write(parabola_label_obj), run_time=1.5)
        self.wait(0.5)

        # 标记切点并开始脉动
        self.play(Create(tangent_point_dot), run_time=0.5)
        # 驱动时间更新器以显示脉动
        self.play(self.scene_time_tracker.animate.set_value(5), rate_func=linear, run_time=5)
        self.wait(1)

    def play_scene_03(self):
        """场景三：切线求解步骤展示"""
        # 1. 背景与布局
        # 使用 NumberPlane 创建带网格的背景，但隐藏中轴线并使网格线变淡
        plane = NumberPlane(
            x_range=[-config.frame_width / 2, config.frame_width / 2, 1],  # Use camera width for range
            y_range=[-config.frame_height / 2, config.frame_height / 2, 1],  # Use camera height for range
            x_length=config.frame_width,
            y_length=config.frame_height,
            background_line_style={
                "stroke_color": MY_MEDIUM_GRAY,
                "stroke_width": 1,
                "stroke_opacity": 0.3  # 使网格线隐约可见
            },
            # 隐藏中轴线 by setting stroke_width to 0
            x_axis_config={"stroke_width": 0},
            y_axis_config={"stroke_width": 0},
        )
        plane.set_z_index(-10)
        # 创建一个纯色背景层，防止网格直接在透明背景上
        bg3 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=MY_LIGHT_GRAY,  # 使用浅灰色背景
            fill_opacity=1.0,
            stroke_width=0
        )
        bg3.set_z_index(-11)  # 在网格后面
        self.add(bg3, plane)

        # 2. 场景编号
        scene_num_03 = self.get_scene_number("03")
        scene_num_03.set_color(MY_BLACK)
        scene_num_03.set_z_index(10)
        self.add(scene_num_03)

        # 3. 左侧推导步骤 (Using VGroup for mixed Text/MathTex)
        step1_text = Text("步骤1: 确定切点 P", font_size=28, color=MY_BLACK)
        step1_math = MathTex("(a, a^2)", font_size=32, color=MY_DARK_BLUE)
        step1 = VGroup(step1_text, step1_math).arrange(RIGHT, buff=0.2)

        step2_text = Text("步骤2: 求导数及切点斜率 k", font_size=28, color=MY_BLACK)
        step2_math = MathTex("f'(x)=2x \\implies k = f'(a)=2a", font_size=32, color=MY_DARK_BLUE)
        step2 = VGroup(step2_text, step2_math).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        step3_text = Text("步骤3: 使用点斜式写出方程", font_size=28, color=MY_BLACK)
        step3_math = MathTex("y - y_1 = k(x - x_1) \\implies y - a^2 = 2a(x - a)", font_size=32, color=MY_DARK_BLUE)
        step3 = VGroup(step3_text, step3_math).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        step4_text = Text("步骤4: 整理得切线方程 ✨", font_size=28, color=MY_BLACK)
        step4_math = MathTex("y = 2a(x - a) + a^2", font_size=32, color=MY_DARK_BLUE)
        step4 = VGroup(step4_text, step4_math).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

        # Use aligned_edge=LEFT for VGroup arrangement
        steps = VGroup(step1, step2, step3, step4).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        steps.to_edge(LEFT, buff=1)

        # 4. 右侧图形展示
        axes_right = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
            x_length=5,
            y_length=4,
            axis_config={"color": MY_BLACK, "include_tip": True, "stroke_width": 2},
            tips=False,  # 简化显示，不显示箭头尖端
        )
        parabola_right = axes_right.plot(lambda x: x ** 2, x_range=[-3, 3], color=MY_DARK_BLUE, stroke_width=3)

        # 切点 a=1
        a_val = 1
        tangent_point_right_coords = axes_right.c2p(a_val, a_val ** 2)
        tangent_point_right_dot = Dot(point=tangent_point_right_coords, color=MY_RED, radius=0.08)

        # 计算切线: y = 2a(x - a) + a^2 = 2(1)(x - 1) + 1^2 = 2x - 2 + 1 = 2x - 1
        # Use axes.plot for the tangent line
        tangent_line = axes_right.plot(lambda x: 2 * a_val * x - a_val ** 2, x_range=[-1, 3], color=MY_ORANGE,
                                       stroke_width=3)
        # Create label and position it
        tangent_label_obj = MathTex("y = 2x - 1", font_size=24, color=MY_ORANGE)
        tangent_label_obj.next_to(tangent_line.get_end(), UR, buff=0.1)

        # 组合右侧图形
        graph_group_right = VGroup(axes_right, parabola_right, tangent_point_right_dot, tangent_line, tangent_label_obj)
        graph_group_right.to_edge(RIGHT, buff=1)

        # 垂直对齐
        graph_group_right.move_to([graph_group_right.get_center()[0], steps.get_center()[1], 0])

        # 5. 动画效果
        # 逐步显示推导步骤 (FadeIn for Text, Write for MathTex)
        self.play(FadeIn(step1[0]), Write(step1[1]), run_time=1)
        self.wait(0.5)
        self.play(FadeIn(step2[0]), Write(step2[1]), run_time=1.5)
        self.wait(0.5)
        self.play(FadeIn(step3[0]), Write(step3[1]), run_time=1.5)
        self.wait(0.5)
        self.play(FadeIn(step4[0]), Write(step4[1]), run_time=1.5)
        self.wait(1)

        # 同时创建右侧图形
        self.play(
            Create(axes_right),
            Create(parabola_right),
            run_time=1.5
        )
        self.play(
            Create(tangent_point_right_dot),
            Create(tangent_line),
            Write(tangent_label_obj),
            run_time=2
        )
        self.wait(2)

    def play_scene_04(self):
        """场景四：理论原理与数学公式解析"""
        # 1. 背景设计：使用 Rectangle with gradient fill
        bg4 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            # Pass color list directly for gradient
            fill_color=[MY_LIGHT_GRAY, MY_MEDIUM_GRAY],
            fill_opacity=1.0,
            # Manim uses gradient_direction attribute
            # gradient_direction=UP, # Check Manim docs for exact syntax if needed
        )
        # Manim v0.19 might use set_fill with gradient kwarg
        bg4.set_fill(color=[MY_LIGHT_GRAY, MY_MEDIUM_GRAY], opacity=1.0)
        # Or potentially:
        # bg4.set_style(fill_color=[MY_LIGHT_GRAY, MY_MEDIUM_GRAY], fill_opacity=1.0)
        # Let's assume direct fill_color works or use set_fill
        bg4.set_z_index(-10)
        self.add(bg4)

        # 2. 场景编号
        scene_num_04 = self.get_scene_number("04")
        scene_num_04.set_color(MY_BLACK)
        scene_num_04.set_z_index(10)
        self.add(scene_num_04)

        # 3. 主要数学内容
        # 上半部分：导数定义
        derivative_title = Text("理论基础 1: 导数的定义", font_size=32, color=MY_BLACK)
        derivative_formula = MathTex(
            r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}",
            font_size=48, color=MY_DARK_BLUE
        )
        derivative_group = VGroup(derivative_title, derivative_formula).arrange(DOWN, buff=0.4)
        derivative_group.to_edge(UP, buff=1.5)

        # 下半部分：点斜式直线方程
        lineslope_title = Text("理论基础 2: 点斜式直线方程", font_size=32, color=MY_BLACK)
        lineslope_formula = MathTex(
            r"y - y_1 = m(x - x_1)",
            font_size=48, color=MY_DARK_BLUE
        )
        lineslope_group = VGroup(lineslope_title, lineslope_formula).arrange(DOWN, buff=0.4)
        lineslope_group.to_edge(DOWN, buff=1.5)

        # 连接箭头
        arrow = Arrow(
            derivative_formula.get_bottom() + DOWN * 0.2,
            lineslope_formula.get_top() + UP * 0.2,
            buff=0.1,
            color=MY_ORANGE,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.15  # Adjusted for better tip size
        )

        # 4. 动画与相机细节
        # 渐显公式 (FadeIn for Text, Write for MathTex)
        self.play(FadeIn(derivative_title), Write(derivative_formula), run_time=2)
        self.wait(0.5)
        self.play(FadeIn(lineslope_title), Write(lineslope_formula), run_time=2)
        self.wait(0.5)

        # 创建箭头连接 - Use Create instead of GrowArrow
        self.play(Create(arrow), run_time=1.5)
        self.wait(0.5)

        # 高亮重点部分 (例如导数 f'(x) 和斜率 m)
        # Use get_part_by_tex safely
        try:
            f_prime_part = derivative_formula.get_part_by_tex("f'(x)")
            m_part = lineslope_formula.get_part_by_tex("m")
            self.play(
                Indicate(f_prime_part, color=MY_ORANGE, scale_factor=1.2),
                Indicate(m_part, color=MY_ORANGE, scale_factor=1.2),
                run_time=2
            )
        except Exception as e:
            print(f"Warning: Could not find parts for indication: {e}")
            # Optionally play without indication or indicate the whole formula
            self.play(
                Indicate(derivative_formula, color=MY_ORANGE, scale_factor=1.1),
                Indicate(lineslope_formula, color=MY_ORANGE, scale_factor=1.1),
                run_time=2
            )

        self.wait(2)

    def play_scene_05(self):
        """场景五：总结与回顾"""
        # 1. 背景设计：深蓝到黑渐变背景
        bg5 = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=[MY_DARK_BLUE, MY_BLACK],  # 深蓝到黑的渐变
            fill_opacity=1.0,
            # gradient_direction=DOWN, # Check Manim docs for exact syntax
        )
        # Use set_fill for gradient
        bg5.set_fill(color=[MY_DARK_BLUE, MY_BLACK], opacity=1.0)
        bg5.set_z_index(-10)
        self.add(bg5)

        # 2. 场景编号
        scene_num_05 = self.get_scene_number("05")
        scene_num_05.set_color(MY_WHITE)  # 深色背景用白色字
        scene_num_05.set_z_index(10)
        self.add(scene_num_05)

        # 3. 回顾内容
        summary_title = Text("总结 🏆", font_size=60, color=MY_GOLD)
        summary_title.to_edge(UP, buff=1.0)

        # 核心公式 (Using MathTex for consistency, including labels)
        # Note: MathTex does not support Chinese directly. Use Text for Chinese parts.
        point_label = Text("切点 P: ", font_size=40, color=MY_WHITE)
        point_formula = MathTex("(a, a^2)", font_size=40, color=MY_WHITE)
        point_group = VGroup(point_label, point_formula).arrange(RIGHT, buff=0.2)

        derivative_label = Text("导数/斜率 k: ", font_size=40, color=MY_WHITE)
        derivative_formula = MathTex("f'(x)=2x \\implies k=2a", font_size=40, color=MY_WHITE)
        derivative_group = VGroup(derivative_label, derivative_formula).arrange(RIGHT, buff=0.2)

        tangent_eq_label = Text("切线方程: ", font_size=40, color=MY_WHITE)
        tangent_eq_formula = MathTex("y = 2a(x - a) + a^2", font_size=40, color=MY_WHITE)
        tangent_eq_group = VGroup(tangent_eq_label, tangent_eq_formula).arrange(RIGHT, buff=0.2)

        # Arrange the groups
        formulas = VGroup(point_group, derivative_group, tangent_eq_group).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        formulas.next_to(summary_title, DOWN, buff=0.8)

        # 引导性提问
        question = Text(
            "你认为切线方程还能帮助我们解决哪些类型的问题？🤔💡",
            font_size=32,
            color=MY_LIGHT_GRAY,
            # Use t2c for highlighting parts of the Text
            t2c={"切线方程": MY_ORANGE, "解决": MY_ORANGE}
        )
        question.to_edge(DOWN, buff=1.0)

        # 4. 动画与相机特效
        self.play(FadeIn(summary_title, scale=0.8), run_time=1.5)
        self.wait(0.5)

        # 逐一展示公式 (Animate Text and MathTex parts separately)
        self.play(FadeIn(point_group[0]), Write(point_group[1]), run_time=1.5)
        self.wait(0.3)
        self.play(FadeIn(derivative_group[0]), Write(derivative_group[1]), run_time=1.5)
        self.wait(0.3)
        self.play(FadeIn(tangent_eq_group[0]), Write(tangent_eq_group[1]), run_time=1.5)
        self.wait(1)

        # 显示提问
        self.play(FadeIn(question, shift=UP * 0.3), run_time=1.5)
        self.wait(1)

        # 镜头轻微放大，强调回顾内容
        summary_group = VGroup(summary_title, formulas)
        # Scale down the frame (zoom in) and center on the summary
        self.play(self.camera.frame.animate.scale(0.9).move_to(summary_group.get_center()), run_time=2)
        self.wait(3)


# --- Main execution block ---
if __name__ == "__main__":
    # 基本配置
    config.pixel_height = 1080  # 设置分辨率高
    config.pixel_width = 1920  # 设置分辨率宽
    config.frame_rate = 30  # 设置帧率
    config.output_file = "CombinedScene"  # 指定输出文件名

    # 临时设置输出目录, 必须使用 #(output_video)
    # 注意：'#(output_video)' 是一个占位符，需要外部程序（如Java）替换成实际路径
    # 如果直接运行此 Python 脚本，需要手动替换或修改此行
    config.media_dir = "04"

    scene = CombinedScene()
    scene.render()
    print("Scene rendering finished.")
