# -*- coding: utf-8 -*-
import random
import numpy as np
from manim import *

# 尝试导入 DARK_GREEN，如果失败则定义一个替代颜色
try:
    from manim.utils.color.BS381 import DARK_GREEN
except ImportError:
    DARK_GREEN = GREEN_E  # 如果导入失败，使用一个备用绿色

# 自定义颜色
MY_DEEP_BLUE = "#1E3A8A"  # 深蓝色
MY_LIGHT_GRAY = "#F3F4F6"  # 浅灰色
MY_GOLD = "#FBBF24"  # 金色
MY_ORANGE = "#F97316"  # 橙色


class CombinedScene(MovingCameraScene):
    """
    合并所有场景的 Manim 动画类。
    用于演示如何求解函数 f(x) = x^2 的切线方程。
    """

    def setup(self):
        """初始化场景自定义时间跟踪器"""
        # 将 self.time 改为 self.scene_time 避免与 Manim 内部属性冲突
        self.scene_time = 0
        # 调用父类的 setup 方法（如果需要）
        super().setup()

    def construct(self):
        """构建动画的主要方法"""
        # --- 场景一 ---
        self.scene_01_intro()
        self.wait(1)  # 场景间过渡等待
        self.clear_scene_objects()

        # --- 场景二 ---
        self.scene_02_concept()
        self.wait(1)
        self.clear_scene_objects()

        # --- 场景三 ---
        self.scene_03_steps()
        self.wait(1)
        self.clear_scene_objects()

        # --- 场景四 ---
        self.scene_04_theory()
        self.wait(1)
        self.clear_scene_objects()

        # --- 场景五 ---
        self.scene_05_summary()
        self.wait(2)  # 结束前等待

    def clear_scene_objects(self):
        """清除当前场景的所有对象并重置相机"""
        # 移除所有对象的更新器，防止在 FadeOut 期间继续更新
        for mob in self.mobjects:
            mob.clear_updaters()

        # 使用 Group(*self.mobjects) 包含所有类型的对象
        # 过滤掉 None 对象，以防万一
        mobjects_to_fade = [m for m in self.mobjects if m is not None]
        if mobjects_to_fade:  # 检查是否为空
            self.play(FadeOut(Group(*mobjects_to_fade)))
        self.clear()  # 清除内部对象列表

        # 重置相机位置和缩放
        self.camera.frame.move_to(ORIGIN)
        # 使用 config 中的默认值或 camera 的属性来重置
        initial_width = config.frame_width
        initial_height = config.frame_height
        self.camera.frame.set(width=initial_width, height=initial_height)

        # 重置自定义时间跟踪器
        self.scene_time = 0

    def star_updater(self, mob, dt):
        """更新星星透明度的函数"""
        # 使用 self.scene_time
        self.scene_time += dt  # 更新场景时间
        # 从 mob 对象中获取预存的参数
        base_opacity = mob.base_opacity
        amplitude = mob.amplitude
        frequency = mob.frequency
        phase = mob.phase
        # 计算新的透明度
        new_opacity = base_opacity + amplitude * np.sin(frequency * self.scene_time + phase)
        # 限制透明度在 [0.1, 0.9] 范围内
        new_opacity = np.clip(new_opacity, 0.1, 0.9)  # 避免完全消失或完全不透明
        # 应用新的透明度
        mob.set_opacity(new_opacity)

    def scene_01_intro(self):
        """场景一：欢迎介绍与星空背景"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 1. 背景设计
        bg = Rectangle(
            width=self.camera.frame_width,  # 使用 config 或 camera 属性
            height=self.camera.frame_height,
            fill_color=MY_DEEP_BLUE,
            fill_opacity=1,
            stroke_width=0
        )
        bg.set_z_index(-10)  # 确保背景在最底层
        self.add(bg)

        # 创建星星
        stars = VGroup()
        num_stars = 150
        frame_width = self.camera.frame_width  # 使用 camera 属性
        frame_height = self.camera.frame_height
        for _ in range(num_stars):
            star = Dot(
                point=[random.uniform(-frame_width / 2, frame_width / 2),
                       random.uniform(-frame_height / 2, frame_height / 2),
                       0],
                radius=random.uniform(0.01, 0.03),
                color=WHITE
            )
            # 存储动画参数到 star 对象
            star.base_opacity = random.uniform(0.4, 0.7)
            star.amplitude = random.uniform(0.2, 0.3)
            star.frequency = random.uniform(0.5, 1.5)
            star.phase = random.uniform(0, 2 * PI)
            # 设置初始透明度
            star.set_opacity(star.base_opacity)
            # 添加更新器
            star.add_updater(self.star_updater)
            stars.add(star)

        self.add(stars)

        # 2. 场景编号
        scene_label_01 = Text("01", font_size=24, color=WHITE)
        scene_label_01.to_corner(UR, buff=0.5)
        self.add(scene_label_01)

        # 3. 主要内容
        title = Text("大家好，欢迎来到本期数学讲解视频", color=WHITE, font_size=48)
        title.shift(UP * 2.5)

        subtitle_part1 = Text("如何求解函数", color=WHITE, font_size=36)
        subtitle_part2 = MathTex("f(x)=x^2", color=WHITE, font_size=40)
        subtitle_part3 = Text("的切线方程", color=WHITE, font_size=36)

        subtitle = VGroup(subtitle_part1, subtitle_part2, subtitle_part3)
        subtitle.arrange(RIGHT, buff=0.2)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 4. 动画效果
        self.play(FadeIn(title))
        self.wait(0.5)
        # 分别动画 Text 和 MathTex
        self.play(FadeIn(subtitle_part1, shift=RIGHT))
        self.play(Write(subtitle_part2))
        self.play(FadeIn(subtitle_part3, shift=LEFT))
        self.wait(1)

        # 5. 相机运动
        # 轻微放大（视觉上是向内移动，聚焦）
        self.play(self.camera.frame.animate.scale(0.9), run_time=1.5)
        self.wait(1.5)

        # 在场景结束前移除更新器，防止影响后续场景
        # 使用 clear_updaters() 移除所有更新器
        stars.clear_updaters()

    def scene_02_concept(self):
        """场景二：切线概念与问题背景介绍"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 1. 背景与布局
        bg = Rectangle(
            width=self.camera.frame_width,
            height=self.camera.frame_height,
            fill_color=MY_LIGHT_GRAY,
            fill_opacity=1,
            stroke_width=0
        )
        bg.set_z_index(-10)
        self.add(bg)

        # 2. 场景编号
        scene_label_02 = Text("02", font_size=24, color=BLACK)
        scene_label_02.to_corner(UR, buff=0.5)
        self.add(scene_label_02)

        # 3. 内容呈现 - 左侧文字
        text_lines = VGroup(
            Text("切线是曲线在某一点的瞬时方向,", font_size=28, color=BLACK),
            Text("反映了曲线在该点的斜率变化。", font_size=28, color=BLACK),
            Text("对于函数", font_size=28, color=BLACK),
            MathTex("f(x)=x^2", font_size=32, color=BLUE),
            Text("我们需要找到其在某点的切线。", font_size=28, color=BLACK)
        )
        # 将 MathTex 嵌入 Text 行中
        line3 = VGroup(text_lines[2], text_lines[3]).arrange(RIGHT, buff=0.15)
        # 重新组合
        left_text = VGroup(text_lines[0], text_lines[1], line3, text_lines[4])
        # *** 修改点：使用 aligned_edge=LEFT ***
        left_text.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        left_text.to_edge(LEFT, buff=1.0)

        # 4. 内容呈现 - 右侧图形
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
            x_length=5,
            y_length=5,
            axis_config={"include_tip": True, "color": BLACK},
            x_axis_config={"numbers_to_include": np.arange(-2, 3, 1)},
            y_axis_config={"numbers_to_include": np.arange(0, 10, 2)},
        )
        # 不显示网格线，只显示坐标轴

        func = lambda x: x ** 2
        graph = axes.plot(func, color=BLUE, x_range=[-3, 3])
        graph_label = axes.get_graph_label(graph, label="f(x)=x^2").set_color(BLUE)

        # 切点
        a = 1
        tangent_point_coords = axes.c2p(a, func(a))  # 坐标系到屏幕坐标
        tangent_point_dot = Dot(point=tangent_point_coords, color=RED, radius=0.1)
        tangent_point_label = MathTex(f"({a}, {a ** 2})", font_size=24, color=RED)
        tangent_point_label.next_to(tangent_point_dot, UR, buff=0.1)

        # 组合右侧图形
        right_graph = VGroup(axes, graph, graph_label, tangent_point_dot, tangent_point_label)
        right_graph.to_edge(RIGHT, buff=1.0)

        # 垂直对齐
        right_graph.move_to([right_graph.get_center()[0], left_text.get_center()[1], 0])

        # 5. 动画与相机运动
        # 逐步显示左侧文字 (使用 FadeIn for Text, Write for MathTex)
        self.play(FadeIn(left_text[0]))
        self.play(FadeIn(left_text[1]))
        self.play(FadeIn(left_text[2][0]))  # "对于函数"
        self.play(Write(left_text[2][1]))  # f(x)=x^2
        self.play(FadeIn(left_text[3]))  # "我们需要..."
        self.wait(0.5)

        # 逐步显示右侧图形
        self.play(Create(axes), run_time=1.5)
        self.play(Create(graph), Write(graph_label), run_time=1.5)
        self.play(FadeIn(tangent_point_dot, scale=1.5), Write(tangent_point_label))

        # 添加点的脉动动画 (使用简单的 ScaleInPlace 动画)
        self.play(ScaleInPlace(tangent_point_dot, 1.2), rate_func=rate_functions.there_and_back, run_time=1)
        self.play(ScaleInPlace(tangent_point_dot, 1.2), rate_func=rate_functions.there_and_back, run_time=1)

        self.wait(1.5)

    def scene_03_steps(self):
        """场景三：切线求解步骤展示"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 1. 背景与网格
        bg = Rectangle(
            width=self.camera.frame_width,
            height=self.camera.frame_height,
            fill_color=MY_LIGHT_GRAY,
            fill_opacity=1,
            stroke_width=0
        )
        bg.set_z_index(-10)
        self.add(bg)

        # 添加隐约的网格
        grid = NumberPlane(
            x_range=(-config.frame_width / 2, config.frame_width / 2, 1),  # 使用 config 确保范围足够大
            y_range=(-config.frame_height / 2, config.frame_height / 2, 1),
            x_length=self.camera.frame_width,
            y_length=self.camera.frame_height,
            background_line_style={
                "stroke_color": GRAY_C,
                "stroke_width": 1,
                "stroke_opacity": 0.3  # 隐约显示
            },
            # 隐藏中轴线
            axis_config={"stroke_width": 0},
            x_axis_config={"stroke_width": 0},  # 明确隐藏 x 轴
            y_axis_config={"stroke_width": 0},  # 明确隐藏 y 轴
        )
        grid.set_z_index(-9)  # 在背景之上，但在内容之下
        self.add(grid)

        # 2. 场景编号
        scene_label_03 = Text("03", font_size=24, color=BLACK)
        scene_label_03.to_corner(UR, buff=0.5)
        self.add(scene_label_03)

        # 3. 推导步骤内容 (左侧)
        step1_text = Text("步骤1: 确定切点", font_size=28, color=BLACK)
        step1_math = MathTex("(a, a^2)", font_size=32, color=DARK_GREEN)
        step1 = VGroup(step1_text, step1_math).arrange(DOWN, aligned_edge=LEFT, buff=0.2)  # 使用 aligned_edge

        step2_text = Text("步骤2: 计算导数及斜率", font_size=28, color=BLACK)
        step2_math = MathTex("f'(x)=2x, \\quad f'(a)=2a", font_size=32, color=DARK_GREEN)
        step2 = VGroup(step2_text, step2_math).arrange(DOWN, aligned_edge=LEFT, buff=0.2)  # 使用 aligned_edge

        step3_text = Text("步骤3: 使用点斜式", font_size=28, color=BLACK)
        step3_math = MathTex("y - a^2 = 2a(x - a)", font_size=32, color=DARK_GREEN)
        step3 = VGroup(step3_text, step3_math).arrange(DOWN, aligned_edge=LEFT, buff=0.2)  # 使用 aligned_edge

        step4_text = Text("步骤4: 整理方程", font_size=28, color=BLACK)
        step4_math = MathTex("y = 2a(x - a) + a^2", font_size=32, color=DARK_GREEN)
        step4 = VGroup(step4_text, step4_math).arrange(DOWN, aligned_edge=LEFT, buff=0.2)  # 使用 aligned_edge

        steps_group = VGroup(step1, step2, step3, step4)
        # *** 修改点：使用 aligned_edge=LEFT ***
        steps_group.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        steps_group.to_edge(LEFT, buff=1.0)

        # 4. 右侧图形展示
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 9, 1],
            x_length=5,
            y_length=5,
            axis_config={"include_tip": True, "color": BLACK},  # 显示坐标轴箭头
            x_axis_config={"numbers_to_include": np.arange(-2, 3, 1)},
            y_axis_config={"numbers_to_include": np.arange(0, 10, 2)},
        )
        func = lambda x: x ** 2
        graph = axes.plot(func, color=BLUE, x_range=[-3, 3])

        a = 1  # 具体例子
        tangent_point_coords = axes.c2p(a, func(a))
        tangent_point_dot = Dot(point=tangent_point_coords, color=RED, radius=0.1)

        # 计算切线
        slope = 2 * a
        # 手动计算切线端点
        x_start = a - 1.5
        y_start = slope * (x_start - a) + func(a)
        x_end = a + 1.5
        y_end = slope * (x_end - a) + func(a)
        # 使用 Line 对象绘制切线段
        tangent_line = Line(
            axes.c2p(x_start, y_start),
            axes.c2p(x_end, y_end),
            color=MY_ORANGE,
            stroke_width=4
        )

        tangent_label = MathTex("y = 2a(x-a)+a^2", font_size=24, color=MY_ORANGE)
        # 将标签放在切线旁边
        tangent_label.next_to(tangent_line.get_center(), UP, buff=0.2)

        right_graph = VGroup(axes, graph, tangent_point_dot, tangent_line, tangent_label)
        right_graph.to_edge(RIGHT, buff=1.0)

        # 垂直对齐
        right_graph.move_to([right_graph.get_center()[0], steps_group.get_center()[1], 0])

        # 5. 动画效果
        # 显示右侧基础图形
        self.play(Create(axes), Create(graph), FadeIn(tangent_point_dot))
        self.wait(0.5)

        # 逐步显示左侧步骤和右侧切线
        # 使用 FadeIn for Text, Write for MathTex
        self.play(FadeIn(step1[0]), Write(step1[1]))
        self.wait(0.8)
        self.play(FadeIn(step2[0]), Write(step2[1]))
        self.wait(0.8)
        self.play(FadeIn(step3[0]), Write(step3[1]))
        # 同时显示切线
        self.play(Create(tangent_line), Write(tangent_label), run_time=1.5)
        self.wait(0.8)
        self.play(FadeIn(step4[0]), Write(step4[1]))

        self.wait(2)

    def scene_04_theory(self):
        """场景四：理论原理与数学公式解析"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 1. 背景
        bg = Rectangle(
            width=self.camera.frame_width,
            height=self.camera.frame_height,
            fill_color=MY_LIGHT_GRAY,  # 淡灰色背景
            fill_opacity=1,
            stroke_width=0
        )
        # 简单的几何纹理可以用 NumberPlane 代替
        grid = NumberPlane(
            x_range=(-config.frame_width / 2, config.frame_width / 2, 2),
            y_range=(-config.frame_height / 2, config.frame_height / 2, 2),
            x_length=self.camera.frame_width, y_length=self.camera.frame_height,
            background_line_style={"stroke_color": GRAY_C, "stroke_width": 1, "stroke_opacity": 0.2},
            axis_config={"stroke_width": 0},  # 隐藏轴线
            x_axis_config={"stroke_width": 0},
            y_axis_config={"stroke_width": 0},
        )
        bg.set_z_index(-10)
        grid.set_z_index(-9)
        self.add(bg, grid)

        # 2. 场景编号
        scene_label_04 = Text("04", font_size=24, color=BLACK)
        scene_label_04.to_corner(UR, buff=0.5)
        self.add(scene_label_04)

        # 3. 主要数学内容
        deriv_formula = MathTex(
            r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}",
            font_size=48, color=BLACK
        )
        deriv_formula.shift(UP * 1.5)
        deriv_title = Text("导数定义 (斜率)", font_size=24, color=DARK_GRAY)
        deriv_title.next_to(deriv_formula, UP, buff=0.3)

        ps_formula = MathTex(
            r"y - y_1 = m(x - x_1)",
            font_size=48, color=BLACK
        )
        ps_formula.shift(DOWN * 1.5)
        ps_title = Text("点斜式直线方程", font_size=24, color=DARK_GRAY)
        ps_title.next_to(ps_formula, UP, buff=0.3)

        # 连接箭头
        arrow = Arrow(
            deriv_formula.get_bottom() + DOWN * 0.2,
            ps_formula.get_top() + UP * 0.2,
            buff=0.1,
            color=MY_ORANGE,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.15
        )

        # 4. 动画与相机细节
        self.play(FadeIn(deriv_title), Write(deriv_formula), run_time=1.5)
        self.wait(0.5)
        self.play(FadeIn(ps_title), Write(ps_formula), run_time=1.5)
        self.wait(0.5)
        self.play(GrowArrow(arrow))

        # 高亮强调 (可选)
        self.play(Indicate(deriv_formula.get_part_by_tex("f'(x)"), color=MY_ORANGE, scale_factor=1.2))
        self.wait(0.3)
        self.play(Indicate(ps_formula.get_part_by_tex("m"), color=MY_ORANGE, scale_factor=1.2))  # m 代表斜率

        self.wait(2)

    def scene_05_summary(self):
        """场景五：总结与回顾"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 1. 背景
        bg = Rectangle(
            width=self.camera.frame_width,
            height=self.camera.frame_height,
            fill_color=BLACK,  # 深色背景
            fill_opacity=1,
            stroke_width=0
        )
        bg.set_z_index(-10)
        self.add(bg)

        # 2. 场景编号
        scene_label_05 = Text("05", font_size=24, color=WHITE)
        scene_label_05.to_corner(UR, buff=0.5)
        self.add(scene_label_05)

        # 3. 回顾内容
        summary_title = Text("总结", color=MY_GOLD, font_size=60)
        summary_title.to_edge(UP, buff=1.0)

        # 核心公式
        point_label = Text("切点:", font_size=32, color=WHITE)
        point_formula = MathTex("(a, a^2)", font_size=36, color=WHITE)
        point_group = VGroup(point_label, point_formula).arrange(RIGHT, buff=0.3)

        deriv_label = Text("导数 (斜率):", font_size=32, color=WHITE)
        deriv_formula = MathTex("f'(x)=2x \\implies m = 2a", font_size=36, color=WHITE)
        deriv_group = VGroup(deriv_label, deriv_formula).arrange(RIGHT, buff=0.3)

        tangent_label = Text("切线方程:", font_size=32, color=WHITE)
        tangent_formula = MathTex("y = 2a(x-a) + a^2", font_size=36, color=WHITE)
        tangent_group = VGroup(tangent_label, tangent_formula).arrange(RIGHT, buff=0.3)

        summary_content = VGroup(point_group, deriv_group, tangent_group)
        # *** 修改点：使用 aligned_edge=LEFT ***
        summary_content.arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        summary_content.next_to(summary_title, DOWN, buff=0.8)
        # 整体居中或靠左显示
        summary_content.center().shift(LEFT * 1.5)

        # 引导性提问
        question = Text(
            "你认为切线方程还能帮助我们解决哪些类型的问题？",
            font_size=28,
            color=GRAY_A,  # Default color for the rest of the text
            t2c={"切线方程": MY_ORANGE}  # Use t2c dictionary to color the substring
        )
        question.to_edge(DOWN, buff=1.0)

        # 4. 动画与相机特效
        self.play(FadeIn(summary_title, scale=1.2))
        self.wait(0.5)

        # 逐一显示公式 (FadeIn for Text, Write for MathTex)
        self.play(FadeIn(point_group[0]), Write(point_group[1]))
        self.wait(0.7)
        self.play(FadeIn(deriv_group[0]), Write(deriv_group[1]))
        self.wait(0.7)
        self.play(FadeIn(tangent_group[0]), Write(tangent_group[1]))
        self.wait(1)

        # 显示提问
        self.play(FadeIn(question, shift=UP))
        self.wait(1)

        # 最终相机放大聚焦
        self.play(self.camera.frame.animate.scale(0.9), run_time=1.5)
        self.wait(1)


# --- Main execution block ---
if __name__ == "__main__":
    # 基本配置
    config.pixel_height = 1080  # 设置分辨率高
    config.pixel_width = 1920  # 设置分辨率宽
    config.frame_rate = 30  # 设置帧率
    config.output_file = "CombinedScene"  # 指定输出文件名（可选，默认类名）

    # 临时设置输出目录（这里指定输出到 "./output_video" 目录）
    config.media_dir = "./02"
    scene = CombinedScene()
    scene.render()
