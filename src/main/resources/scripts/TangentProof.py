from manim import *
import numpy as np

class TangentDerivation(MovingCameraScene):
    def construct(self):
        # 初始化场景
        self.setup_scene()
        self.introduce_parabola()
        self.show_tangent_point()
        self.derive_derivative()
        self.apply_point_slope()
        self.verify_example()
        self.conclude_proof()
    
    def setup_scene(self):
        # 创建星空背景和坐标系
        self.camera.background_color = "#0F0F1A"
        stars = StarField(radius=0.05, num_stars=200, color=WHITE).set_opacity(0.5)
        self.add(stars)
        
        # 初始化3D坐标系
        axes = ThreeDAxes(
            x_range=[-4,4], y_range=[0,16], z_range=[-4,4],
            axis_config={"color": GREY_D}
        ).set_opacity(0.3)
        self.axes = axes
        self.add(axes)
        
        # 设置初始相机角度
        self.camera.frame.set_euler_angles(
            theta=30*DEGREES,
            phi=45*DEGREES,
            gamma=0
        )
    
    def introduce_parabola(self):
        # 绘制抛物线
        parabola = self.axes.plot_parametric_curve(
            lambda t: np.array([t, t**2, 0]),
            color=GOLD,
            t_range=[-3.5, 3.5]
        )
        
        # 动态绘制抛物线
        self.play(Create(parabola, run_time=2))
        self.wait(0.5)
        
        # 添加动态切线
        self.tangent_group = VGroup()
        self.a_tracker = ValueTracker(1)
        
        def update_tangent(mob):
            a = self.a_tracker.get_value()
            line = Line(
                self.axes.c2p(a-2, (a-2)*(2*a - (a-2)), 0),
                self.axes.c2p(a+2, (a+2)*(2*a - (a+2)), 0),
                color=SILVER
            )
            mob.become(line)
            
        tangent = always_redraw(update_tangent)
        tangent_glow = GlowDot(color=ORANGE, radius=0.3).add_updater(
            lambda m: m.move_to(self.axes.c2p(self.a_tracker.get_value(), self.a_tracker.get_value()**2, 0))
        )
        
        self.tangent_group.add(tangent, tangent_glow)
        self.play(FadeIn(self.tangent_group))
        self.wait()
        
        # 创建参数滑块
        slider = NumberLine(
            x_range=[-3, 3], 
            length=6,
            include_numbers=True,
            color=GREY_B
        ).to_edge(DOWN)
        dot = Dot(color=BLUE).add_updater(
            lambda m: m.move_to(slider.n2p(self.a_tracker.get_value()))
        )
        a_label = DecimalNumber().add_updater(
            lambda m: m.set_value(self.a_tracker.get_value()).next_to(dot, UP)
        )
        
        self.play(
            FadeIn(slider),
            FadeIn(dot),
            FadeIn(a_label),
            self.camera.frame.animate.set_height(12).shift(DOWN*1.5),
            run_time=2
        )
        self.a_tracker.add_updater(lambda m, dt: m.increment_value(0.05 * dt))
        self.wait(4)
        self.a_tracker.clear_updaters()
    
    def show_tangent_point(self):
        # 突出显示切点坐标
        a = self.a_tracker.get_value()
        point = self.axes.c2p(a, a**2, 0)
        
        # 创建坐标标注
        coord_label = MathTex(f"(a, a^2)", color=ORANGE).scale(0.8)
        coord_label.add_background_rectangle(opacity=0.8, color=BLACK, buff=0.1)
        coord_label.add_updater(lambda m: m.next_to(
            self.axes.c2p(self.a_tracker.get_value(), self.a_tracker.get_value()**2, 0), 
            UR, 
            buff=0.1
        ))
        
        # 创建数学证明框
        proof_box = SurroundingRectangle(coord_label, color=WHITE, buff=0.2)
        
        self.play(
            Write(coord_label),
            Create(proof_box),
            self.a_tracker.animate.set_value(2),
            run_time=3
        )
        self.wait(2)
        
        self.coord_label = coord_label
        self.proof_box = proof_box
    
    def derive_derivative(self):
        # 导数推导过程
        derivation = VGroup(
            MathTex(r"f'(x) = \lim_{h \to 0} \frac{(x+h)^2 - x^2}{h}"),
            MathTex(r"= \lim_{h \to 0} \frac{x^2 + 2xh + h^2 - x^2}{h}"),
            MathTex(r"= \lim_{h \to 0} (2x + h)"),
            MathTex(r"= 2x")
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT)
        
        # 设置颜色
        derivation[0][0][7:12].set_color(RED)    # \lim部分
        derivation[1][0][4:15].set_color(GREEN)   # 展开部分
        derivation[2][0][4:8].set_color(BLUE)     # 简化部分
        
        # 创建推导面板
        panel = SurroundingRectangle(derivation, color=GREY_C, buff=0.3)
        panel.set_fill(BLACK, opacity=0.9)
        
        self.play(
            FadeIn(panel),
            Write(derivation[0]),
            self.camera.frame.animate.shift(LEFT*2)
        )
        self.wait()
        
        # 逐步显示推导步骤
        for i in range(1, 4):
            self.play(TransformFromCopy(derivation[i-1], derivation[i]))
            self.wait(0.5)
        
        # 强调最终结果
        final_result = derivation[-1].copy()
        self.play(
            final_result.animate.scale(1.5).set_color(GOLD).to_edge(UP),
            FadeOut(derivation[:-1]),
            FadeOut(panel)
        )
        self.wait(2)
        
        # 连接导数与切线斜率
        slope_arrow = Arrow(
            final_result.get_bottom(),
            self.coord_label.get_left(),
            color=TEAL,
            buff=0.2
        )
        
        self.play(Create(slope_arrow))
        self.wait()
        self.play(
            FadeOut(final_result),
            FadeOut(slope_arrow)
        )
    
    def apply_point_slope(self):
        # 点斜式应用
        point_slope_form = MathTex(
            r"y - y_1 = m(x - x_1)",
            substrings_to_isolate=["y_1", "m", "x_1"]
        ).to_edge(UP)
        
        # 设置颜色
        point_slope_form.set_color_by_tex("y_1", ORANGE)
        point_slope_form.set_color_by_tex("m", GREEN)
        point_slope_form.set_color_by_tex("x_1", BLUE)
        
        # 代入值后的方程
        substituted = MathTex(
            r"y - a^2 = 2a(x - a)",
            substrings_to_isolate=["a^2", "2a", "a"]
        ).next_to(point_slope_form, DOWN)
        
        substituted.set_color_by_tex("a^2", ORANGE)
        substituted.set_color_by_tex("2a", GREEN)
        substituted.set_color_by_tex("a", BLUE)
        
        # 最终方程
        final_eq = MathTex(r"y = 2ax - a^2").scale(1.2)
        final_eq_box = SurroundingRectangle(final_eq, color=RED, buff=0.2)
        
        self.play(Write(point_slope_form))
        self.wait()
        
        # 显示代入过程
        self.play(Transform(point_slope_form.copy(), substituted))
        self.wait()
        
        # 展开方程
        self.play(
            substituted.animate.shift(UP*0.5),
            FadeIn(final_eq, shift=DOWN),
            Create(final_eq_box)
        )
        self.wait(2)
        
        # 连接方程与切线
        self.play(
            final_eq.animate.next_to(self.tangent_group, UR, buff=1),
            FadeOut(final_eq_box),
            self.camera.frame.animate.shift(RIGHT*2 + UP*1)
        )
        self.wait()
    
    def verify_example(self):
        # 实例验证
        a_value = 2
        example_group = VGroup(
            MathTex(r"a = 2"),
            MathTex(r"f(a) = 2^2 = 4"),
            MathTex(r"m = 2 \times 2 = 4"),
            MathTex(r"y = 4x - 4")
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT)
        
        # 创建验证标记
        dot = Dot(color=RED).move_to(self.axes.c2p(2,4,0))
        line = self.axes.plot_parametric_curve(
            lambda t: np.array([t, 4*t -4, 0]),
            t_range=[0.5, 3.5],
            color=CYAN
        )
        
        self.play(
            self.a_tracker.animate.set_value(2),
            FadeIn(dot),
            run_time=2
        )
        self.wait()
        
        # 逐步显示计算过程
        for eq in example_group:
            self.play(Write(eq))
            self.wait(0.5)
        
        # 绘制验证切线
        self.play(Create(line), run_time=2)
        self.wait()
        
        # 显示唯一性证明
        test_points = VGroup(*[
            Dot(self.axes.c2p(x, 4*x -4, 0), color=RED)
            for x in np.linspace(1.5, 3.5, 10)
        ])
        
        self.play(
            LaggedStart(*[GrowFromCenter(p) for p in test_points], lag_ratio=0.1),
            run_time=3
        )
        self.wait()
        self.play(FadeOut(test_points))
    
    def conclude_proof(self):
        # 总结步骤
        steps = VGroup(
            Text("1. Identify Tangent Point"),
            Text("2. Calculate Derivative"),
            Text("3. Apply Point-Slope Form"),
            Text("4. Verify with Example")
        ).arrange(DOWN, aligned_edge=LEFT).scale(0.8)
        
        # 创建总结框
        box = SurroundingRectangle(steps, color=BLUE, buff=0.3)
        box.set_fill(BLACK, opacity=0.8)
        
        self.play(
            FadeIn(box),
            Write(steps),
            self.camera.frame.animate.move_to(ORIGIN).set_height(10),
            run_time=3
        )
        self.wait(3)
        
        # 结束动画
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=2
        )
        self.wait()

class StarField(VGroup):
    def __init__(self, radius=0.05, num_stars=200, color=WHITE, **kwargs):
        super().__init__(**kwargs)
        for _ in range(num_stars):
            star = Dot(
                point=np.array([
                    np.random.uniform(-7,7),
                    np.random.uniform(-4,4),
                    0
                ]),
                radius=radius * np.random.rand(),
                color=color,
                fill_opacity=np.random.uniform(0.3, 0.7)
            )
            self.add(star)
        self.star_animation = self.create_animation()
    
    def create_animation(self):
        animations = []
        for star in self:
            speed = 0.1 * star.radius
            animations.append(
                star.animate.shift(speed * np.random.randn(3)).set_opacity(
                    np.clip(star.get_fill_opacity() + 0.1 * np.random.randn(), 0.3, 0.7)
                )
            )
        return LaggedStart(*animations, lag_ratio=0.05)
# 渲染命令：manim -pqh TangentProof.py TangentDerivation