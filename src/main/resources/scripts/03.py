# -*- coding: utf-8 -*-
from manim import *
import numpy as np
import random
from manim.utils.color.BS381 import DARK_GREEN # 虽然未使用，但按要求导入

# 定义一些自定义颜色
MY_BLUE = "#2E6F95"
MY_GOLD = "#F2C641"
MY_ORANGE = "#E87A33"
MY_GREY = "#D1D1D1"
MY_DARK_BLUE = "#1A3A4F" # 用于背景

class CombinedScene(MovingCameraScene):
    """
    一个组合场景，演示如何求解函数 f(x)=x^2 的切线方程。
    包含五个子场景，按顺序播放。
    """
    def construct(self):
        # 统一设置，确保相机初始状态
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        #################################
        # 场景01：欢迎介绍与星空背景
        #################################
        self.play_scene_01()

        #################################
        # 场景02：切线概念与问题背景介绍
        #################################
        self.play_scene_02()

        #################################
        # 场景03：切线求解步骤展示
        #################################
        self.play_scene_03()

        #################################
        # 场景04：理论原理与数学公式解析
        #################################
        self.play_scene_04()

        #################################
        # 场景05：总结与回顾
        #################################
        self.play_scene_05()

    def play_scene_01(self):
        """播放场景01：欢迎介绍与星空背景"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 背景
        bg1 = Rectangle(width=self.camera.frame_width, height=self.camera.frame_height)
        bg1.set_fill(color=MY_DARK_BLUE, opacity=1)
        bg1.set_stroke(width=0)
        bg1.set_z_index(-1) # 背景在最底层
        self.add(bg1)

        # 场景编号
        scene_label1 = Text("01", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label1)

        # 星空效果
        star_tracker = ValueTracker(0) # 用于控制闪烁动画的时间
        stars = VGroup()
        num_stars = 100 # 增加星星数量以填充背景
        for _ in range(num_stars):
            # 随机位置
            x = random.uniform(-self.camera.frame_width / 2 * 1.1, self.camera.frame_width / 2 * 1.1) # 稍微超出边界防止边缘空旷
            y = random.uniform(-self.camera.frame_height / 2 * 1.1, self.camera.frame_height / 2 * 1.1)
            # 创建星星点
            star = Dot(point=np.array([x, y, 0]), radius=random.uniform(0.01, 0.04), color=WHITE)
            # 设置初始透明度
            base_opacity = random.uniform(0.2, 0.6)
            star.set_opacity(base_opacity)
            # 添加闪烁更新器
            phase = random.uniform(0, TAU) # 随机相位，使闪烁不同步
            amplitude = random.uniform(0.1, 0.3) # 随机振幅
            frequency = random.uniform(1.5, 2.5) # 随机频率
            # 使用 updater 更新透明度
            # 使用 get_fill_opacity() 读取基础透明度，确保 updater 独立
            star.add_updater(lambda m, dt, base=star.get_fill_opacity(), amp=amplitude, freq=frequency, ph=phase: m.set_opacity(
                np.clip(base + amp * np.sin(star_tracker.get_value() * freq + ph), 0, 1)
            ))
            stars.add(star)
        self.add(stars)
        # 启动时间跟踪器
        star_tracker.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(star_tracker) # 需要将 ValueTracker 添加到场景以使其更新

        # 标题
        title = Text("大家好，欢迎来到本期数学讲解视频", font_size=48, color=WHITE)
        title.to_edge(UP, buff=1.0)

        # 副标题
        subtitle_text1 = Text("如何求解函数 ", font_size=36, color=WHITE)
        subtitle_formula = MathTex("f(x)=x^2", font_size=36, color=MY_GOLD)
        subtitle_text2 = Text(" 的切线方程", font_size=36, color=WHITE)
        subtitle = VGroup(subtitle_text1, subtitle_formula, subtitle_text2).arrange(RIGHT, buff=0.2)
        subtitle.next_to(title, DOWN, buff=0.5)

        # 动画
        self.play(FadeIn(title, shift=DOWN*0.5), run_time=1.5)
        self.wait(0.5)
        # 分别动画化副标题的文本和公式部分
        self.play(
            FadeIn(subtitle_text1, shift=RIGHT*0.2),
            Write(subtitle_formula),
            FadeIn(subtitle_text2, shift=LEFT*0.2),
            run_time=2
        )
        self.wait(1)
        # 相机轻微移动
        self.play(self.camera.frame.animate.shift(0.2 * OUT), run_time=1, rate_func=there_and_back)
        self.wait(2)

        # 清理场景1的对象和更新器
        star_tracker.clear_updaters()
        stars.clear_updaters() # 停止星星闪烁
        self.remove(star_tracker) # 从场景移除 ValueTracker
        # 使用 Group(*self.mobjects) 淡出所有对象, 但要排除相机本身
        mobjects_to_fade = Group(*[m for m in self.mobjects if m is not self.camera])
        self.play(FadeOut(mobjects_to_fade), run_time=1)
        self.clear() # 清除所有 mobjects

    def play_scene_02(self):
        """播放场景02：切线概念与问题背景介绍"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 背景
        bg2 = Rectangle(width=self.camera.frame_width, height=self.camera.frame_height)
        bg2.set_fill(color=MY_GREY, opacity=1)
        bg2.set_stroke(width=0)
        bg2.set_z_index(-1)
        self.add(bg2)

        # 场景编号
        scene_label2 = Text("02", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label2)

        # 左侧文字说明
        explanation = Text(
            "切线是曲线在某一点的瞬时方向。\n\n对于函数 f(x)=x^2，\n切线反映了曲线在该点的斜率。",
            font_size=28, color=BLACK, line_spacing=1.2
        )
        explanation.to_edge(LEFT, buff=1.0) # 增加 buff

        # 右侧坐标系与图像
        axes = Axes(
            x_range=[-3.5, 3.5, 1],
            y_range=[-1, 12, 2], # 调整 y 范围以更好显示抛物线
            x_length=6,
            y_length=5,
            axis_config={"color": BLACK, "include_tip": True, "stroke_width": 2},
            x_axis_config={"numbers_to_include": np.arange(-3, 4, 1)},
            y_axis_config={"numbers_to_include": np.arange(0, 13, 2)},
        )
        axes.to_edge(RIGHT, buff=1.0) # 增加 buff
        # 添加坐标轴标签
        axis_labels = axes.get_axis_labels(x_label="x", y_label="f(x)")
        axis_labels.set_color(BLACK)

        # 绘制抛物线
        parabola = axes.plot(lambda x: x ** 2, x_range=[-3.2, 3.2], color=MY_BLUE, stroke_width=3)

        # 标记切点 (a=1)
        a = 1.0
        tangent_point_coord = np.array([a, a**2, 0])
        tangent_point_graph = axes.coords_to_point(*tangent_point_coord)
        dot = Dot(point=tangent_point_graph, color=RED, radius=0.1)
        dot_label = MathTex(f"({a}, {a**2})", color=RED, font_size=30).next_to(dot, UR, buff=0.1)

        # 脉动效果的时间跟踪器
        pulse_tracker = ValueTracker(0)
        pulse_tracker.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(pulse_tracker) # 添加到场景

        # 添加脉动更新器到 dot
        # 使用 get_center() 确保缩放中心正确
        dot.add_updater(lambda m: m.scale(1 + 0.1 * np.sin(pulse_tracker.get_value() * 4 * PI), about_point=m.get_center()))

        # 动画
        self.play(FadeIn(explanation, shift=LEFT*0.5), run_time=2)
        self.wait(0.5)
        self.play(Create(axes), Write(axis_labels), run_time=2)
        self.play(Create(parabola), run_time=2)
        self.play(FadeIn(dot, scale=0.5), Write(dot_label), run_time=1)
        self.wait(3)

        # 清理场景2的对象和更新器
        dot.clear_updaters()
        pulse_tracker.clear_updaters()
        self.remove(pulse_tracker)
        mobjects_to_fade = Group(*[m for m in self.mobjects if m is not self.camera])
        self.play(FadeOut(mobjects_to_fade), run_time=1)
        self.clear()

    def play_scene_03(self):
        """播放场景03：切线求解步骤展示"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 背景
        bg3 = Rectangle(width=self.camera.frame_width, height=self.camera.frame_height)
        bg3.set_fill(color=MY_GREY, opacity=1) # 保持浅灰背景
        bg3.set_stroke(width=0)
        bg3.set_z_index(-1)
        self.add(bg3)

        # 场景编号
        scene_label3 = Text("03", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label3)

        # 左侧推导步骤 (混合 Text 和 MathTex)
        step1_text = Text("步骤1: 确定切点 ", font_size=32, color=BLACK)
        step1_math = MathTex("(a, a^2)", font_size=36, color=MY_BLUE)
        step1_group = VGroup(step1_text, step1_math).arrange(RIGHT, buff=0.15)

        step2_text = Text("步骤2: 求导数和斜率 ", font_size=32, color=BLACK)
        step2_math = MathTex("f'(x)=2x \\implies f'(a)=2a", font_size=36, color=MY_BLUE)
        step2_group = VGroup(step2_text, step2_math).arrange(RIGHT, buff=0.15)

        step3_text = Text("步骤3: 点斜式方程 ", font_size=32, color=BLACK)
        step3_math = MathTex("y - a^2 = 2a(x - a)", font_size=36, color=MY_BLUE)
        step3_group = VGroup(step3_text, step3_math).arrange(RIGHT, buff=0.15)

        step4_text = Text("步骤4: 整理得切线方程 ", font_size=32, color=BLACK)
        step4_math = MathTex("y = 2a(x - a) + a^2", font_size=36, color=MY_ORANGE) # 最终结果用橙色
        step4_group = VGroup(step4_text, step4_math).arrange(RIGHT, buff=0.15)

        steps = VGroup(step1_group, step2_group, step3_group, step4_group).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        steps.to_edge(LEFT, buff=1.0)

        # 右侧图形展示
        axes3 = Axes(
            x_range=[-3.5, 3.5, 1],
            y_range=[-1, 12, 2],
            x_length=6,
            y_length=5,
            axis_config={"color": BLACK, "include_tip": True, "stroke_width": 2},
            x_axis_config={"numbers_to_include": np.arange(-3, 4, 1)},
            y_axis_config={"numbers_to_include": np.arange(0, 13, 2)},
        )
        axes3.to_edge(RIGHT, buff=1.0)
        axis_labels3 = axes3.get_axis_labels(x_label="x", y_label="f(x)").set_color(BLACK)
        parabola3 = axes3.plot(lambda x: x ** 2, x_range=[-3.2, 3.2], color=MY_BLUE, stroke_width=3)

        # 切点 (a=1)
        a_val = 1.0
        tangent_point_coord3 = np.array([a_val, a_val**2, 0])
        tangent_point_graph3 = axes3.coords_to_point(*tangent_point_coord3)
        dot3 = Dot(point=tangent_point_graph3, color=RED, radius=0.1)
        dot_label3 = MathTex(f"({a_val}, {a_val**2})", color=RED, font_size=30).next_to(dot3, DR, buff=0.1)

        # 计算切线
        slope = 2 * a_val
        # 切线函数: y = slope * (x - a_val) + a_val**2
        tangent_line_func = lambda x: slope * (x - a_val) + a_val**2
        # 使用 axes.plot 绘制切线，确保它在坐标系内
        tangent_line = axes3.plot(tangent_line_func, x_range=[-2, 3], color=MY_ORANGE, stroke_width=2.5) # 限制 x_range 使线不过长

        # 动画
        # 创建右侧图形
        self.play(Create(axes3), Write(axis_labels3), run_time=1.5)
        self.play(Create(parabola3), run_time=1.5)
        self.play(FadeIn(dot3, scale=0.5), Write(dot_label3), run_time=1)
        self.wait(0.5)

        # 逐步展示左侧步骤，并同步绘制切线
        # 分别对 Text 和 MathTex 应用动画
        self.play(FadeIn(steps[0][0]), Write(steps[0][1]), run_time=1.5) # 步骤1
        self.wait(1)
        self.play(FadeIn(steps[1][0]), Write(steps[1][1]), run_time=1.5) # 步骤2
        self.wait(1)
        self.play(FadeIn(steps[2][0]), Write(steps[2][1]), run_time=1.5) # 步骤3
        # 在步骤3后绘制切线
        self.play(Create(tangent_line), run_time=2)
        self.wait(1)
        self.play(FadeIn(steps[3][0]), Write(steps[3][1]), run_time=1.5) # 步骤4
        self.wait(3)

        # 清理场景3
        mobjects_to_fade = Group(*[m for m in self.mobjects if m is not self.camera])
        self.play(FadeOut(mobjects_to_fade), run_time=1)
        self.clear()

    def play_scene_04(self):
        """播放场景04：理论原理与数学公式解析"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 背景
        bg4 = Rectangle(width=self.camera.frame_width, height=self.camera.frame_height)
        bg4.set_fill(color=GREY_C, opacity=1) # 淡灰色背景
        bg4.set_stroke(width=0)
        bg4.set_z_index(-1)
        self.add(bg4)

        # 场景编号
        scene_label4 = Text("04", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label4)

        # 导数定义公式
        derivative_title = Text("理论基础 1: 导数定义", font_size=32, color=BLACK).to_edge(UP, buff=1.0).shift(LEFT*3)
        derivative_formula = MathTex(r"f'(x)=\lim_{h \to 0}\frac{f(x+h)-f(x)}{h}", font_size=48, color=MY_BLUE)
        derivative_formula.next_to(derivative_title, DOWN, buff=0.5)
        derivative_group = VGroup(derivative_title, derivative_formula)

        # 点斜式方程
        pointslope_title = Text("理论基础 2: 点斜式方程", font_size=32, color=BLACK).to_edge(DOWN, buff=2.0).shift(LEFT*3)
        point_slope_formula = MathTex(r"y - y_1 = m(x - x_1)", font_size=48, color=MY_BLUE)
        point_slope_formula.next_to(pointslope_title, UP, buff=0.5) # 注意是 UP
        pointslope_group = VGroup(pointslope_title, point_slope_formula)

        # 连接箭头
        arrow = CurvedArrow(
            derivative_formula.get_bottom() + RIGHT*0.5,
            point_slope_formula.get_top() + RIGHT*0.5,
            angle=-PI/2, # 使箭头弯曲向下
            color=YELLOW_D, # 使用深黄色
            stroke_width=6
        )
        arrow_label = Text("结合得到切线方程", font_size=28, color=BLACK).next_to(arrow, RIGHT, buff=0.3)

        # 动画
        # 分别对 Text 和 MathTex 应用动画
        self.play(FadeIn(derivative_group[0]), Write(derivative_group[1]), run_time=1.5)
        self.wait(1)
        self.play(FadeIn(pointslope_group[0]), Write(pointslope_group[1]), run_time=1.5)
        self.wait(1)
        # 使用 Create 替代 GrowArrow
        self.play(Create(arrow), FadeIn(arrow_label), run_time=2)
        self.wait(3)

        # 清理场景4
        mobjects_to_fade = Group(*[m for m in self.mobjects if m is not self.camera])
        self.play(FadeOut(mobjects_to_fade), run_time=1)
        self.clear()

    def play_scene_05(self):
        """播放场景05：总结与回顾"""
        # 重置相机
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)

        # 背景
        bg5 = Rectangle(width=self.camera.frame_width, height=self.camera.frame_height)
        bg5.set_fill(color=MY_DARK_BLUE, opacity=1) # 恢复深蓝色背景
        bg5.set_stroke(width=0)
        bg5.set_z_index(-1)
        self.add(bg5)

        # 场景编号
        scene_label5 = Text("05", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label5)

        # 总结标题
        summary_text = Text("总结", font_size=60, color=MY_GOLD) # 更大字号，金色
        summary_text.to_edge(UP, buff=1.0)

        # 核心公式回顾
        formula1_text = Text("1. 切点: ", font_size=36, color=WHITE)
        formula1_math = MathTex(r"(a, a^2)", font_size=40, color=MY_ORANGE)
        formula1 = VGroup(formula1_text, formula1_math).arrange(RIGHT, buff=0.2)

        formula2_text = Text("2. 斜率 (导数): ", font_size=36, color=WHITE)
        formula2_math = MathTex(r"f'(a)=2a", font_size=40, color=MY_ORANGE)
        formula2 = VGroup(formula2_text, formula2_math).arrange(RIGHT, buff=0.2)

        formula3_text = Text("3. 切线方程: ", font_size=36, color=WHITE)
        formula3_math = MathTex(r"y=2a(x-a)+a^2", font_size=40, color=MY_GOLD) # 最终方程用金色
        formula3 = VGroup(formula3_text, formula3_math).arrange(RIGHT, buff=0.2)

        formulas = VGroup(formula1, formula2, formula3).arrange(DOWN, aligned_edge=LEFT, buff=0.7)
        formulas.next_to(summary_text, DOWN, buff=1.0)

        # 引导性提问
        question = Text("思考：切线方程还能帮助我们解决哪些问题？\n（例如：近似计算、优化问题...）",
                        font_size=28, color=WHITE, line_spacing=1.0)
        question.to_edge(DOWN, buff=1.0)

        # 动画
        self.play(Write(summary_text), run_time=1.5)
        self.wait(0.5)
        # 逐条展示公式, 分别动画化 Text 和 MathTex
        self.play(FadeIn(formulas[0][0]), Write(formulas[0][1]), run_time=1)
        self.wait(0.5)
        self.play(FadeIn(formulas[1][0]), Write(formulas[1][1]), run_time=1)
        self.wait(0.5)
        self.play(FadeIn(formulas[2][0]), Write(formulas[2][1]), run_time=1)
        self.wait(1.5)
        # 显示问题并轻微放大
        self.play(FadeIn(question, shift=UP*0.3), self.camera.frame.animate.scale(1.05), run_time=2) # 稍微放大一点
        self.wait(4)
        # 结束前可以再缩小回来或保持
        # self.play(self.camera.frame.animate.scale(1/1.05), run_time=1)

        # 场景5结束，不需要显式清理，动画自然结束

# 主程序入口
if __name__ == "__main__":
    # 基本配置
    config.pixel_height = 1080  # 设置分辨率高
    config.pixel_width = 1920   # 设置分辨率宽
    config.frame_rate = 30      # 设置帧率
    config.output_file = "CombinedScene"  # 指定输出文件名

    # 使用 tempconfig 临时设置输出目录
    # java程序会对#(output_video)进行替换, 这里我们用一个实际的目录名如 "output_video"
    # 如果需要严格匹配 #(output_video)，请确保你的 Java 程序能正确处理这个占位符
    output_directory = "./output_video" # 使用实际目录名
    # output_directory = "./#(output_video)" # 如果需要占位符

    from manim import tempconfig
    with tempconfig({"media_dir": output_directory}):
        scene = CombinedScene()
        scene.render()