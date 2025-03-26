from manim import *
import numpy as np
CYAN = "#00FFFF"

################################################################################
# 全局配置说明：
# - 字体使用“思源黑体 CN Bold”用于中文，数学公式采用 LaTeX 格式，使用 Latin Modern Math 字体。
# - 颜色方案、动画速率、相机运动等全局参数均按照场景提示要求设定。
################################################################################

###########################################################################
# 场景1：开场动画 (5秒)
###########################################################################
class OpeningAnimation(ThreeDScene):
    def construct(self):
        # 设置相机初始角度：从上方俯视，俯角约60°（即离垂直30°）
        self.set_camera_orientation(phi=60 * DEGREES, theta=0)

        # 创建深蓝色渐变星空背景，使用渐变填充的矩形模拟
        bg = Rectangle(width=config.frame_width, height=config.frame_height)
        # 注意：manim支持用列表设置渐变颜色
        bg.set_fill(color=[BLUE_D, BLUE_E], opacity=1)
        bg.set_stroke(width=0)
        self.add(bg)
        self.play(FadeIn(bg), run_time=1)

        # 创建中央浮现的发光网格坐标系：x轴为黄色，y轴为青色，z轴半透明
        axes = ThreeDAxes(
            x_range=[-config.frame_width / 2, config.frame_width / 2, 1],
            y_range=[-config.frame_height / 2, config.frame_height / 2, 1],
            z_range=[-5, 5, 1],
            x_length=config.frame_width,
            y_length=config.frame_height,
            z_length=5
        )
        axes.get_x_axis().set_color(YELLOW)
        axes.get_y_axis().set_color(CYAN)
        # 用 set_stroke 设置 z 轴的透明度
        # axes.get_z_axis().set_stroke(color=WHITE, stroke_opacity=0.3)
        self.play(Create(axes), run_time=2)

        # 创建红色抛物线 f(x)=x^2，添加流光效果：颜色渐变从白色到蓝色
        parabola = FunctionGraph(
            lambda x: x**2,
            x_range=[-3, 3],
            color=RED
        )
        parabola.set_color_by_gradient(WHITE, BLUE)
        self.play(Create(parabola), run_time=3)

        # 创建金色光标沿抛物线滑动，并添加残留粒子轨迹效果（残影持续0.5秒）
        cursor = Dot(color=GOLD, radius=0.1)
        traced_path = TracedPath(cursor.get_center, stroke_color=GOLD, stroke_width=4, dissipating_time=0.5)
        self.add(traced_path)
        self.play(MoveAlongPath(cursor, parabola), run_time=3, rate_func=linear)

        # 在抛物线顶端（此处取点(2,4)以便与后续场景衔接）生成立体金属风标题
        title = Text("如何求解抛物线切线方程？", font="思源黑体 CN Bold", font_size=48)
        title.set_color_by_gradient(GOLD, ORANGE)
        title.move_to(np.array([2, 4.5, 0]))
        self.play(Write(title), run_time=2)

        # 利用 move_camera 实现相机推进与缩放效果（由于 ThreeDCamera 没有 frame 属性）
        self.move_camera(zoom=1/1.5, run_time=3)
        self.wait(1)


###########################################################################
# 场景2：几何定义演示 (8秒)
###########################################################################
class GeometryDefinitionScene(Scene):
    def construct(self):
        # 创建右侧半透明黑板，用于展示切线定义文字
        blackboard = Rectangle(
            width=config.frame_width / 2,
            height=config.frame_height,
            fill_color=BLACK,
            fill_opacity=0.5
        )
        blackboard.to_edge(RIGHT)
        self.add(blackboard)

        # 绘制蓝色抛物线 f(x)=x^2
        parabola = FunctionGraph(lambda x: x**2, x_range=[-3, 3], color=BLUE)
        self.play(Create(parabola), run_time=2)

        # 在抛物线上点 (2,4) 处添加旋转的金色标记
        point_marker = Dot(point=np.array([2, 4, 0]), color=GOLD, radius=0.15)
        self.play(FadeIn(point_marker), run_time=1)
        self.play(Rotate(point_marker, angle=2 * PI, run_time=2))

        # 右侧黑板显示切线定义：与曲线仅接触于一点且方向一致的直线
        definition_text = MathTex(
            r"\text{切线定义：与曲线仅接触于一点且方向一致的直线}",
            font_size=36, color=WHITE
        )
        definition_text.to_edge(RIGHT)
        self.play(Write(definition_text), run_time=2)

        # 底部字幕同步显示语音文本（白色楷体，带淡灰色投影效果）
        subtitle = Text("（语音同步：方向一致）", font="思源黑体 CN Bold", font_size=24, color=WHITE)
        subtitle.set_style(stroke_color=GREY, stroke_width=1)
        subtitle.to_edge(DOWN)
        self.play(FadeIn(subtitle), run_time=1)

        # 使用 ReplacementTransform 将标记转换为红色切线方程 y = 4x - 4（在点 (2,4) 处）
        tangent_eq = MathTex(r"y = 4x - 4", font_size=36, color=RED)
        tangent_eq.move_to(point_marker.get_center() + UP * 0.5)
        self.play(ReplacementTransform(point_marker.copy(), tangent_eq), run_time=2)

        # 使用 Indicate 动画三次闪烁切线与抛物线的唯一交点
        self.play(Indicate(tangent_eq, scale_factor=1.2), run_time=1)
        self.play(Indicate(tangent_eq, scale_factor=1.2), run_time=1)
        self.play(Indicate(tangent_eq, scale_factor=1.2), run_time=1)

        # 从黑板处发出紫色箭头指向切线，同时将黑板文字中“方向一致”高亮
        arrow = Arrow(start=definition_text.get_left(), end=tangent_eq.get_center(), color=PURPLE)
        self.play(Create(arrow), run_time=1)
        self.play(definition_text.animate.set_color_by_tex("方向一致", YELLOW), run_time=1)

        # 显示公式特效：点斜式经过动态填充和波浪扩散效果转换为切线公式
        formula_initial = MathTex(r"\underbrace{y - y_0 = m(x - x_0)}_{\text{点斜式}}", font_size=36)
        formula_boxed = MathTex(r"\boxed{y = 2x_0x - x_0^2}", font_size=36)
        formula_initial.next_to(parabola, UP, buff=1)
        formula_boxed.next_to(formula_initial, DOWN, buff=0.5)
        self.play(Write(formula_initial), run_time=2)
        self.play(ApplyWave(formula_initial, amplitude=0.1, run_time=2))
        self.wait(0.5)
        self.play(ReplacementTransform(formula_initial.copy(), formula_boxed), run_time=2)
        self.wait(1)


###########################################################################
# 场景3：导数推导过程 (12秒)
###########################################################################
class DerivativeDerivationScene(ThreeDScene):
    def construct(self):
        # 设置三维相机视角：侧视视角（theta=60°, phi=30°）
        self.set_camera_orientation(phi=30 * DEGREES, theta=60 * DEGREES)

        # 左侧显示全息投影效果的微分符号 df/dx
        diff_symbol = MathTex(r"\frac{df}{dx}", font_size=48, color=TEAL)
        diff_symbol.to_edge(LEFT, buff=1).shift(UP * 1)
        self.play(FadeIn(diff_symbol), run_time=1)

        # 右侧分层显示导数推导过程
        derivation = VGroup(
            MathTex(r"f(x) = x^2", font_size=36),
            MathTex(r"f'(x) = \lim_{h \to 0} \frac{(x+h)^2 - x^2}{h}", font_size=36),
            MathTex(r"= \lim_{h \to 0} (2x + h)", font_size=36),
            MathTex(r"= 2x \quad \textcolor{green}{\checkmark}", font_size=36)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT, buff=1)
        self.play(Write(derivation), run_time=3)

        # 对极限符号“lim”添加脉冲红色边框
        lim_rect = SurroundingRectangle(derivation[1].get_part_by_tex(r"\lim"), color=RED)
        self.play(Create(lim_rect), run_time=1)
        self.play(FadeOut(lim_rect), run_time=0.5)

        # 对最终结果“2x”进行放大（150%）并添加持续旋转的光环
        final_result = derivation[3].get_part_by_tex("2x")
        self.play(final_result.animate.scale(1.5), run_time=1)
        halo = Circle(radius=final_result.get_width(), color=YELLOW, stroke_width=2)
        halo.move_to(final_result)
        self.play(Create(halo), run_time=1)
        self.play(Rotate(halo, angle=TAU, run_time=2, rate_func=linear))

        # 展开 (x+h)^2 项：逐项显示 x^2, 2xh, h^2
        expansion = VGroup(
            MathTex(r"x^2", font_size=28),
            MathTex(r"+ 2xh", font_size=28),
            MathTex(r"+ h^2", font_size=28)
        ).arrange(RIGHT, buff=0.2)
        expansion.next_to(derivation[1], DOWN, buff=0.5)
        self.play(FadeIn(expansion), run_time=2)

        # 交互演示：用 ValueTracker 模拟可拖动滑块控制 h 值，实时更新割线斜率
        h_tracker = ValueTracker(2)
        x0 = 1  # 固定选取 x0=1
        secant_formula = always_redraw(lambda: MathTex(
            r"m_{\text{割}} = \frac{(1+%.2f)^2 - 1^2}{%.2f}" % (h_tracker.get_value(), h_tracker.get_value()),
            font_size=36, color=ORANGE
        ).to_edge(DOWN))
        self.add(secant_formula)
        # 动画：将 h 从 2 逐渐变为 0.1，模拟割线向切线的过渡
        self.play(h_tracker.animate.set_value(0.1), run_time=4, rate_func=linear)
        self.wait(1)


###########################################################################
# 场景4：切线簇三维演示 (10秒)
###########################################################################
class TangentFamily3DScene(ThreeDScene):
    def construct(self):
        # 初始视角：标准二维俯视图
        self.set_camera_orientation(phi=90 * DEGREES, theta=0)

        # 创建参数化切线族：方程 y = 2t*x - t^2，t ∈ [-3, 3]
        tangent_lines = VGroup()
        t_values = np.linspace(-3, 3, 13)
        for t in t_values:
            # 定义切线函数
            func = lambda x, t=t: 2 * t * x - t**2
            line = FunctionGraph(
                lambda x, t=t: func(x),
                x_range=[-4, 4],
                # 根据 t 值映射颜色：HSV 色彩空间
                color=Color(hsv_to_rgb(((t + 3) / 6, 0.9, 0.7)))
            )
            # 高亮 t=1 的切线，其他设为半透明
            if np.isclose(t, 1, atol=0.1):
                line.set_color(WHITE)
                line.set_stroke(width=4)
            else:
                line.set_opacity(0.5)
            tangent_lines.add(line)
        self.play(Create(tangent_lines), run_time=3)

        # 为每条切线沿其上发射流动光点，速度与 |t| 成正比
        dots = VGroup()
        for t, line in zip(t_values, tangent_lines):
            dot = Dot(color=WHITE, radius=0.05)
            dot.move_to(line.points[0])
            # 使用 updater 使光点沿切线不断循环运动
            dot.add_updater(lambda m, dt, line=line, t=t: m.move_to(
                interpolate(line.points[0], line.points[-1], (self.time * abs(t)) % 1)
            ))
            dots.add(dot)
        self.add(dots)

        # 相机绕 z 轴旋转360°（6秒）
        self.play(self.camera.frame.animate.rotate(angle=TAU, axis=OUT), run_time=6, rate_func=linear)

        # 切换为螺旋上升视角：调整 phi 和 theta
        self.move_camera(phi=60 * DEGREES, theta=45 * DEGREES, run_time=2)

        # 特写：当展示 t=0 的水平切线时，镜头推进至该切线（缩放比例3:1）
        for t, line in zip(t_values, tangent_lines):
            if np.isclose(t, 0, atol=0.1):
                self.play(self.camera.frame.animate.move_to(line.get_center()).set(width=line.get_width() / 3), run_time=2)
                break
        self.wait(1)


###########################################################################
# 场景5：应用案例验证 (15秒)
###########################################################################
class ApplicationVerificationScene(Scene):
    def construct(self):
        # 分屏布局：左半屏为动态坐标系显示 x0=1 处的切线构造；右半屏为数值验证表格
        # 左半屏：创建坐标系、抛物线和切线（x0=1 处的切线 y=2x-1）
        axes = Axes(x_range=[0, 3, 1], y_range=[0, 5, 1], x_length=4, y_length=4)
        axes.to_edge(LEFT, buff=0.5)
        parabola = axes.plot(lambda x: x**2, color=BLUE)
        tangent = axes.plot(lambda x: 2 * x - 1, color=RED)
        self.play(Create(axes), Create(parabola), run_time=2)
        self.play(Create(tangent), run_time=2)

        # 在两条曲线上添加移动游标，初始位置在 x=1 处
        cursor = Dot(color=YELLOW)
        cursor.move_to(axes.coords_to_point(1, 1))
        self.play(FadeIn(cursor), run_time=1)

        # 添加垂直连线，实时连接抛物线与切线在游标处的对应值
        v_line = always_redraw(lambda:
            Line(
                axes.coords_to_point(cursor.get_center()[0], parabola.underlying_function(cursor.get_center()[0])),
                axes.coords_to_point(cursor.get_center()[0], tangent.underlying_function(cursor.get_center()[0])),
                color=PURPLE
            )
        )
        self.add(v_line)

        # 右半屏：显示数值验证表格
        table = MathTable(
            [["x", "抛物线值", "切线值"],
             ["1.0", "1.0", "1.0"],
             ["1.1", "{\\color{red}1.21}", "{\\color{blue}1.2}"],
             ["0.9", "{\\color{red}0.81}", "{\\color{blue}0.8}"]],
            include_outer_lines=True
        )
        table.scale(0.7)
        table.to_edge(RIGHT, buff=0.5)
        self.play(Create(table), run_time=2)

        # 动画：游标从 x=1 移动至 x=1.5，并同时观察抛物线与切线间的差异变化
        self.play(cursor.animate.move_to(axes.coords_to_point(1.5, 1.5**2)), run_time=3)

        # 触发公式变形动画：从 y_{切线}=2x-1 变形为展开形式
        formula_initial = MathTex(r"y_{\text{切线}} = 2x - 1", font_size=36)
        formula_transformed = MathTex(r"y = 2(1+\Delta x) - 1 = 2\Delta x + 1", font_size=36)
        formula_initial.to_edge(DOWN)
        formula_transformed.to_edge(DOWN)
        self.play(Write(formula_initial), run_time=2)
        self.wait(1)
        self.play(ReplacementTransform(formula_initial, formula_transformed), run_time=2)
        self.wait(2)


###########################################################################
# 场景6：总结升华 (7秒)
###########################################################################
class SummaryScene(Scene):
    def construct(self):
        # 创建多重嵌套的背景坐标系：
        # 1. 笛卡尔坐标系
        cartesian = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            background_line_style={"stroke_color": GREY}
        )
        # 2. 极坐标示意（圆形）
        polar = Circle(radius=3, color=BLUE, stroke_width=1, fill_opacity=0.1)
        # 3. 简单的微分流形示意（点和线）
        manifold = VGroup(
            Dot(point=ORIGIN, color=WHITE),
            Line(ORIGIN, UP, color=YELLOW)
        )
        background_group = VGroup(cartesian, polar, manifold)
        self.add(background_group)

        # 中央悬浮发光的核心公式，并叠加流动的麦克斯韦方程组纹理效果
        core_formula = MathTex(r"\boxed{y = 2x_0x - x_0^2}", font_size=48)
        maxwell_texture = Text("∇·E=ρ/ε₀   ∇×B=μ₀J+μ₀ε₀∂E/∂t", font_size=20, color=WHITE)
        maxwell_texture.scale(0.8)
        core_formula.add(maxwell_texture)
        self.play(FadeIn(core_formula, scale=0.5), run_time=2)

        # 文字特效：将“数学原理的统一性”拆分为单个汉字，沿抛物线轨迹飞入并组合成方阵
        phrase = "数学原理的统一性"
        chars = VGroup(*[Text(char, font="思源黑体 CN Bold", font_size=36, color=ORANGE) for char in phrase])
        # 每个字符从屏幕上方飞入
        for i, char in enumerate(chars):
            char.move_to(5 * UP)
            self.play(char.animate.move_to(LEFT * 2 + UP * (i - 1)), run_time=0.5)
        cube_array = VGroup(*chars)
        self.play(cube_array.animate.arrange_in_grid(rows=2, buff=0.5), run_time=2)

        # 终幕过渡：所有数学符号转化为星光并渐渐消散
        self.play(FadeOut(core_formula, run_time=2), FadeOut(background_group, run_time=2), FadeOut(cube_array, run_time=2))
        # 最后聚焦于微分符号 "d"，模拟其转化为宇宙飞船飞向星空深处
        d_symbol = MathTex(r"d", font_size=72, color=PURPLE)
        d_symbol.move_to(ORIGIN)
        self.play(FadeIn(d_symbol), run_time=1)
        self.play(d_symbol.animate.shift(UP * 3 + RIGHT * 3).scale(0.5), run_time=3)
        self.wait(1)


################################################################################
# 使用说明：
# 运行时可在命令行指定渲染对应的场景，例如：
#   manim -pqh your_file.py OpeningAnimation
# 或者：
#   manim -pqh your_file.py SummaryScene
################################################################################
