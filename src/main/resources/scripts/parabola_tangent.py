from manim import *
import numpy as np
import random


class CombinedScene(MovingCameraScene):
    def construct(self):
        #################################
        # 场景01：欢迎介绍界面
        #################################
        bg = Rectangle(width=self.camera.frame_width,
                       height=self.camera.frame_height)
        bg.set_fill(color=BLUE_D, opacity=1)
        bg.set_stroke(width=0)
        bg.set_z_index(-1)  # 背景在最底层
        self.add(bg)

        scene_label = Text("01", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label)

        # 创建用于星空闪烁的 ValueTracker 与星星
        star_tracker = ValueTracker(0)
        stars = VGroup()
        num_stars = 40
        for _ in range(num_stars):
            x = random.uniform(-self.camera.frame_width / 2, self.camera.frame_width / 2)
            y = random.uniform(-self.camera.frame_height / 2, self.camera.frame_height / 2)
            star = Dot(point=np.array([x, y, 0]), radius=0.03, color=WHITE)
            star.set_opacity(0.3)
            phase = random.uniform(0, 2 * np.pi)
            star.add_updater(lambda m, dt, phase=phase: m.set_opacity(
                0.3 + 0.2 * np.abs(np.sin(star_tracker.get_value() * 2 * np.pi + phase))
            ))
            stars.add(star)
        self.add(stars)
        star_tracker.add_updater(lambda m, dt: m.increment_value(dt))

        title = Text("大家好，欢迎来到本期数学讲解视频", font_size=48, color=WHITE)
        title.to_edge(UP)
        subtitle_text1 = Text("如何求解函数 ", font_size=36, color=WHITE)
        subtitle_formula = MathTex("f(x)=x^2", font_size=36)
        subtitle_text2 = Text(" 的切线方程", font_size=36, color=WHITE)
        subtitle = VGroup(subtitle_text1, subtitle_formula, subtitle_text2).arrange(RIGHT, buff=0.2)
        subtitle.next_to(title, DOWN, buff=0.5)

        self.play(FadeIn(title), run_time=1)
        self.play(Write(subtitle), run_time=1.5)
        self.play(self.camera.frame.animate.shift(0.2 * OUT), run_time=0.5)
        self.wait(1)
        star_tracker.clear_updaters()
        stars.clear_updaters()
        self.wait(1)

        self.play(FadeOut(Group(*self.mobjects)), run_time=1)
        self.clear()
        self.camera.frame.set(width=self.camera.frame_width, height=self.camera.frame_height)

        #################################
        # 场景02：问题背景与概念介绍
        #################################
        bg2 = Rectangle(width=self.camera.frame_width,
                        height=self.camera.frame_height)
        bg2.set_fill(color=GREY_E, opacity=1)
        bg2.set_stroke(width=0)
        bg2.set_z_index(-1)
        self.add(bg2)

        scene_label = Text("02", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label)

        explanation = Text(
            "切线是曲线在某一点的瞬时方向，在函数 f(x)=x^2 中，切线反映了曲线在该点的斜率变化。",
            font_size=28, color=BLACK)
        explanation.to_edge(LEFT).shift(LEFT * 0.5)

        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-1, 16, 3],
            x_length=6,
            y_length=5,
            tips=True)
        axes.to_edge(RIGHT).shift(RIGHT * 0.5)
        axes.set_stroke(color=LIGHT_GREY, width=2)
        parabola = axes.plot(lambda x: x ** 2, x_range=[-3, 3], color=BLUE)

        a = 1
        tangent_point = axes.coords_to_point(a, a ** 2)
        dot = Dot(point=tangent_point, color=RED)
        dot.set_opacity(1)
        dot.add_updater(lambda m, dt: m.scale(1 + 0.1 * np.sin(self.renderer.time * 2 * np.pi)))

        self.play(Create(axes), run_time=2)
        self.play(Create(parabola), run_time=2)
        self.play(FadeIn(dot), run_time=1)
        self.play(FadeIn(explanation), run_time=2)
        self.wait(2)
        dot.clear_updaters()

        self.play(FadeOut(Group(*self.mobjects)), run_time=1)
        self.clear()
        self.camera.frame.set(width=self.camera.frame_width, height=self.camera.frame_height)

        #################################
        # 场景03：求解切线基本步骤展示
        #################################
        bg3 = Rectangle(width=self.camera.frame_width,
                        height=self.camera.frame_height)
        bg3.set_fill(color=GREY_E, opacity=1)
        bg3.set_stroke(width=0)
        bg3.set_z_index(-1)
        self.add(bg3)

        scene_label = Text("03", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label)

        step1 = MathTex(r"(a, a^2)", font_size=36)
        step2 = MathTex(r"f'(x)=2x,\quad f'(a)=2a", font_size=36)
        step3 = MathTex(r"y - a^2 = 2a(x - a)", font_size=36)
        step4 = MathTex(r"y = 2a(x - a) + a^2", font_size=36)
        steps = VGroup(step1, step2, step3, step4).arrange(DOWN, aligned_edge=LEFT, buff=0.8)
        steps.to_edge(LEFT).shift(RIGHT * 0.5)

        axes3 = Axes(
            x_range=[-4, 4, 1],
            y_range=[-1, 16, 3],
            x_length=6,
            y_length=6,
            tips=True)
        axes3.to_edge(RIGHT).shift(RIGHT * -0.5)
        axes3.set_stroke(color=LIGHT_GREY, width=2)
        parabola3 = axes3.plot(lambda x: x ** 2, x_range=[-3, 3], color=BLUE)
        tangent_point3 = axes3.coords_to_point(a, a ** 2)
        dot3 = Dot(point=tangent_point3, color=RED)
        dot3.set_opacity(1)
        # 计算切线（斜率 2，对应方向向量 [1, 2, 0]）
        direction = np.array([1, 2, 0])
        direction = direction / np.linalg.norm(direction)
        line_length = 6
        start_point = tangent_point3 - direction * (line_length / 2)
        end_point = tangent_point3 + direction * (line_length / 2)
        tangent_line = Line(start_point, end_point, color=ORANGE)

        self.play(FadeIn(steps[0]), run_time=1)
        self.wait(1)
        self.play(ReplacementTransform(steps[0].copy(), steps[1]), run_time=1)
        self.wait(1)
        self.play(ReplacementTransform(steps[1].copy(), steps[2]), run_time=1)
        self.wait(1)
        self.play(ReplacementTransform(steps[2].copy(), steps[3]), run_time=1)
        self.play(Create(axes3), run_time=2)
        self.play(Create(parabola3), run_time=2)
        self.play(FadeIn(dot3), run_time=1)
        self.play(Create(tangent_line), run_time=2)
        # 保持静态，不做额外的相机动画
        self.wait(2)

        self.play(FadeOut(Group(*self.mobjects)), run_time=1)
        self.clear()
        self.camera.frame.set(width=self.camera.frame_width, height=self.camera.frame_height)

        #################################
        # 场景04：理论原理与数学公式解析
        #################################
        bg4 = Rectangle(width=self.camera.frame_width,
                        height=self.camera.frame_height)
        bg4.set_fill(color=GREY_C, opacity=1)
        bg4.set_stroke(width=0)
        bg4.set_z_index(-1)
        self.add(bg4)

        scene_label = Text("04", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label)

        derivative_formula = MathTex(r"f'(x)=\lim_{h \to 0}\frac{f(x+h)-f(x)}{h}", font_size=36)
        derivative_formula.to_edge(UP)
        point_slope_formula = MathTex(r"y - y_1 = m(x - x_1)", font_size=36)
        point_slope_formula.to_edge(DOWN)
        self.play(FadeIn(derivative_formula), run_time=1.5)
        self.play(FadeIn(point_slope_formula), run_time=1.5)
        arrow = Arrow(start=LEFT, end=RIGHT, color=YELLOW)
        arrow.next_to(derivative_formula, RIGHT, buff=1)
        self.play(Create(arrow), run_time=1)
        self.wait(2)

        self.play(FadeOut(Group(*self.mobjects)), run_time=1)
        self.clear()
        self.camera.frame.set(width=self.camera.frame_width, height=self.camera.frame_height)

        #################################
        # 场景05：总结与回顾
        #################################
        # 背景直接使用相机 frame 的副本，确保始终覆盖视图
        bg5 = Rectangle(width=self.camera.frame_width,
                        height=self.camera.frame_height)
        bg5.set_fill(color=BLUE_D, opacity=1)
        bg5.set_stroke(width=0)
        bg5.set_z_index(-1)
        self.add(bg5)

        scene_label = Text("05", font_size=24, color=RED).to_corner(UR, buff=0.5)
        self.add(scene_label)

        summary_text = Text("总结", font_size=48, color=GOLD)
        summary_text.to_edge(UP)
        formula1 = MathTex(r"(a, a^2)", font_size=36)
        formula2 = MathTex(r"f'(x)=2x", font_size=36)
        formula3 = MathTex(r"y=2a(x-a)+a^2", font_size=36)
        formulas = VGroup(formula1, formula2, formula3).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        formulas.next_to(summary_text, DOWN, buff=1)
        question = Text("你认为切线方程还能帮助我们解决哪些类型的问题？", font_size=28, color=WHITE)
        question.to_edge(DOWN)
        self.play(FadeIn(summary_text), run_time=1)
        self.play(Write(formulas), run_time=2)
        self.play(FadeIn(question), run_time=1.5)
        self.wait(3)


if __name__ == "__main__":
    from manim import tempconfig

    # 使用 tempconfig 临时设置输出目录（这里指定输出到 "./output_video" 目录）
    with tempconfig({
        "media_dir": "./output_video",
    }):
        scene = CombinedScene()
        scene.render()
