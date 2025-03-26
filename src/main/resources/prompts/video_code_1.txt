from manim import *
import numpy as np

class ParabolaTangent(ThreeDScene):
    def construct(self):
        # 初始化场景
        self.setup_scene()
        self.create_parabola()
        self.animate_tangent_derivation()
        self.show_tangent_family()
        self.verify_numerically()
        self.final_transition()

    def setup_scene(self):
        # 设置星空背景和坐标系
        self.camera.background_color = "#000033"
        self.setup_stars()
        self.axes = ThreeDAxes(
            x_range=[-4,4], y_range=[0,16], z_range=[-4,4],
            axis_config={
                "color": GREY_A,
                "stroke_width": 2,
                "tip_config": {"length": 0.3}
            }
        ).set_opacity(0.3)
        self.add(self.axes)

        # 添加标题
        self.title = Text("如何求解抛物线切线方程？", font="Source Han Sans CN Bold",
                        t2c={"抛物线": BLUE, "切线": YELLOW}).scale(1.2)
        self.title.to_edge(UP).add_background_rectangle(opacity=0.7)
        self.play(Write(self.title), run_time=2)

    def setup_stars(self):
        # 创建星空背景
        stars = VGroup(*[Dot(point=np.random.uniform(-7,7,3),
                          radius=np.random.uniform(0.01,0.03),
                          color=WHITE,
                          fill_opacity=np.random.uniform(0.3,0.8))
                      for _ in range(200)])
        stars.set_color_by_gradient(BLUE_E, WHITE)
        self.add(stars)
        self.stars = stars

    def create_parabola(self):
        # 绘制抛物线及其动画
        parabola = self.axes.plot_parametric_curve(
            lambda t: np.array([t, t**2, 0]),
            color=BLUE_D,
            t_range=[-3,3]
        )
        parabola.set_shade_in_3d(True)

        # 添加流动光效
        glow = TracedPath(parabola.get_end, dissipating_time=0.5, 
                        stroke_color=BLUE_A, stroke_width=6)

        self.play(Create(parabola), run_time=3)
        self.add(glow)
        self.wait()
        self.parabola = parabola

    def animate_tangent_derivation(self):
        # 导数推导动画
        x0 = 2
        point = self.axes.c2p(x0, x0**2, 0)
        dot = Dot(point, color=GOLD, radius=0.1)
        self.play(GrowFromCenter(dot))

        # 创建可调节的割线
        h_tracker = ValueTracker(1)
        secant = always_redraw(lambda: self.get_secant_line(x0, h_tracker.get_value()))
        slope_text = always_redraw(lambda: self.get_slope_text(x0, h_tracker.get_value()))
        
        self.play(Create(secant), Write(slope_text))
        self.play(h_tracker.animate.set_value(0.1), run_time=5, rate_func=linear)
        self.wait()

        # 转换为切线
        tangent = self.axes.plot_parametric_curve(
            lambda t: np.array([t, 2*x0*t - x0**2, 0]),
            color=RED,
            t_range=[x0-2, x0+2]
        )
        self.play(ReplacementTransform(secant, tangent))
        self.remove(slope_text)
        self.tangent = tangent

        # 显示导数公式
        derivative_eq = MathTex(
            r"f'(x) = \lim_{h \to 0} \frac{(x+h)^2 - x^2}{h} = 2x",
            substrings_to_isolate=["\lim", "2x"]
        ).next_to(self.title, DOWN)
        derivative_eq.set_color_by_tex("\lim", RED)
        derivative_eq.set_color_by_tex("2x", GREEN)
        self.play(Write(derivative_eq))
        self.wait(2)

    def get_secant_line(self, x0, h):
        # 生成割线
        p1 = self.axes.c2p(x0, x0**2, 0)
        p2 = self.axes.c2p(x0+h, (x0+h)**2, 0)
        return Line(p1, p2, color=YELLOW, stroke_width=3)

    def get_slope_text(self, x0, h):
        # 显示斜率公式
        return MathTex(
            r"m_{\text{割}} = \frac{(x_0+h)^2 - x_0^2}{h} = ",
            f"{2*x0 + h:.2f}",
            color=YELLOW
        ).to_edge(DOWN)

    def show_tangent_family(self):
        # 展示切线族
        tangents = VGroup()
        colors = color_gradient([PURPLE, RED], 7)
        for t in np.linspace(-3, 3, 7):
            tangent = self.axes.plot_parametric_curve(
                lambda x: np.array([x, 2*t*x - t**2, 0]),
                color=colors[int(t+3)],
                t_range=[t-1.5, t+1.5]
            )
            tangents.add(tangent)

        self.play(
            LaggedStart(*[Create(t) for t in tangents], lag_ratio=0.2),
            run_time=4
        )
        self.wait()

        # 旋转3D视角
        self.move_camera(phi=60*DEGREES, theta=30*DEGREES, run_time=3)
        self.begin_ambient_camera_rotation(rate=0.1)

    def verify_numerically(self):
        # 数值验证表格
        table = MathTable(
            [[1.0, 1.0, 1.0],
             [1.1, 1.21, 1.2],
             [0.9, 0.81, 0.8]],
            row_labels=[MathTex("1.0"), MathTex("1.1"), MathTex("0.9")],
            col_labels=[
                MathTex("x"),
                MathTex(r"y_{\text{抛物线}}"),
                MathTex(r"y_{\text{切线}}")
            ],
            include_outer_lines=True
        ).scale(0.7).to_edge(LEFT)

        self.play(Create(table), run_time=2)
        self.wait(2)

        # 高亮差异区域
        diff_rects = VGroup(
            SurroundingRectangle(table.get_rows()[1][1:], color=RED),
            SurroundingRectangle(table.get_rows()[2][1:], color=BLUE)
        )
        self.play(Create(diff_rects))
        self.wait()

    def final_transition(self):
        # 最终过渡动画
        final_eq = MathTex(r"\boxed{y = 2x_0x - x_0^2}").scale(2)
        final_eq.set_color_by_gradient(BLUE, YELLOW)
        
        self.play(
            Transform(self.parabola, final_eq),
            FadeOut(self.tangent),
            run_time=3
        )
        self.wait(2)

        # 符号消散效果
        self.play(
            final_eq.animate.apply_function(lambda p: p + np.random.randn(3)),
            rate_func=there_and_back,
            run_time=3
        )
        self.wait()