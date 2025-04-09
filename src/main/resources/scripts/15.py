# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
import hashlib
from moviepy import AudioFileClip # Correct import

# --- Font Check (Optional but Recommended) ---
# import manimpango
# DEFAULT_FONT = "Noto Sans" # Example
# available_fonts = manimpango.list_fonts()
# final_font = None
# if DEFAULT_FONT in available_fonts:
#     final_font = DEFAULT_FONT
# else:
#     print(f"Warning: Font '{DEFAULT_FONT}' not found. Using Manim default.")
# # In setup: if final_font: Text.set_default(font=final_font)

# --- Custom Colors ---
MY_LIGHT_GRAY = "#f0f0f0"
MY_DARK_GRAY = "#555555"
MY_BLUE = "#007bff"
MY_RED = "#dc3545"
MY_GREEN = "#28a745"
MY_ORANGE = "#ffc107" # Matches cos θ
MY_PURPLE = "#800080" # Highlighting
MY_BLACK = "#000000"
MY_WHITE = "#ffffff"
MY_CONCLUSION_BG = "#001f3f" # Dark blue for conclusion
MY_CONCLUSION_FG = "#ffffff"
MY_CONCLUSION_SUB = "#cccccc"

# --- TTS Caching Setup ---
CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class CustomVoiceoverTracker:
    """Tracks audio path and duration for TTS."""
    def __init__(self, audio_path, duration):
        self.audio_path = audio_path
        self.duration = duration

def get_cache_filename(text):
    """Generates a unique filename based on the text hash."""
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}.mp3")

@contextmanager
def custom_voiceover_tts(text, token="123456", base_url="https://uni-ai.fly.dev/api/manim/tts"):
    """Fetches TTS audio, caches it, and provides path and duration."""
    cache_file = get_cache_filename(text)
    audio_file = cache_file

    if os.path.exists(cache_file):
        # print(f"Using cached TTS for: {text[:30]}...")
        pass # Use cached file
    else:
        # print(f"Requesting TTS for: {text[:30]}...")
        try:
            input_text_encoded = requests.utils.quote(text)
            url = f"{base_url}?token={token}&input={input_text_encoded}"
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            audio_file = cache_file
            # print("TTS downloaded and cached.")
        except requests.exceptions.RequestException as e:
            print(f"TTS API request failed: {e}")
            tracker = CustomVoiceoverTracker(None, 0)
            yield tracker
            return
        except Exception as e:
            print(f"An error occurred during TTS processing: {e}")
            if os.path.exists(cache_file): os.remove(cache_file) # Clean up partial file
            tracker = CustomVoiceoverTracker(None, 0)
            yield tracker
            return

    # Get duration
    duration = 0
    if audio_file and os.path.exists(audio_file):
        try:
            with AudioFileClip(audio_file) as clip:
                duration = clip.duration
            # print(f"Audio duration: {duration:.2f}s")
        except Exception as e:
            print(f"Error processing audio file {audio_file}: {e}")
            # If duration fails, treat as no audio
            audio_file = None
            duration = 0
    else:
        # print(f"TTS audio file not found or not created: {audio_file}")
        audio_file = None # Ensure audio_path is None if file doesn't exist

    tracker = CustomVoiceoverTracker(audio_file, duration)
    try:
        yield tracker
    finally:
        pass # Keep cache

# -----------------------------
# CombinedScene: Unit Circle to Cosine Graph
# -----------------------------
class CombinedScene(MovingCameraScene):
    """
    Visually explains the connection between the unit circle and the cosine function.
    """
    def setup(self):
        MovingCameraScene.setup(self)
        # Optional: Set default font here if checked
        # if final_font: Text.set_default(font=final_font)
        # Initialize theta tracker for animations involving angle
        self.theta_tracker = ValueTracker(0)
        # Store elements that need to be accessed across animations within a scene part
        self.unit_circle_elements = VGroup()
        self.graph_elements = VGroup()

    def construct(self):
        # --- Play Scenes Sequentially ---
        self.play_scene_01()
        self.clear_and_reset() # Clear before starting next scene

        self.play_scene_02()
        # Don't clear immediately, Scene 3 builds upon Scene 2 elements conceptually
        # We will handle element reuse/recreation within Scene 3

        self.play_scene_03()
        # Don't clear immediately, Scene 4 builds upon Scene 3 elements

        self.play_scene_04()
        self.clear_and_reset() # Clear before conclusion

        self.play_scene_05()
        # Final wait is handled in play_scene_05

    def get_scene_number(self, number_str, color=MY_BLACK):
        """Creates and positions the scene number."""
        scene_num = Text(number_str, font_size=24, color=color) # Allow color change
        scene_num.to_corner(UR, buff=0.3)
        scene_num.set_z_index(10)
        return scene_num

    def clear_and_reset(self):
        """Clears all objects and resets camera and trackers."""
        # Clear updaters from all mobjects first
        mobjects_to_clear = list(self.mobjects) # Make a copy
        for mob in mobjects_to_clear:
            # Check if mob exists and has the get_updaters method
            if mob is not None and hasattr(mob, 'get_updaters') and mob.get_updaters():
                mob.clear_updaters()

        # Fade out all valid mobjects
        valid_mobjects = [m for m in self.mobjects if m is not None]
        if valid_mobjects:
            self.play(FadeOut(Group(*valid_mobjects)), run_time=0.5)

        self.clear() # Clears self.mobjects

        # Reset camera
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        # Reset any camera rotation if needed (MovingCameraScene uses frame properties)
        # self.camera.frame.set_theta(0) # Example if rotation was used

        # Reset trackers
        self.theta_tracker.set_value(0)

        # Clear stored groups
        self.unit_circle_elements = VGroup()
        self.graph_elements = VGroup()

        self.wait(0.1)

    # --- Scene 1: Introduction to the Unit Circle ---
    def play_scene_01(self):
        """Scene 1: Introduces the unit circle and its components."""
        # Background
        bg1 = Rectangle(width=config.frame_width, height=config.frame_height,
                        fill_color=MY_LIGHT_GRAY, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg1)

        # Scene Number
        scene_num_01 = self.get_scene_number("01", color=MY_BLACK)
        self.add(scene_num_01)

        # Title
        title = Text("The Unit Circle", font_size=48, color=MY_BLACK).to_edge(UP, buff=0.5)

        # Coordinate Axes
        axes = Axes(
            x_range=[-1.5, 1.5, 1], y_range=[-1.5, 1.5, 1],
            x_length=6, y_length=6,
            axis_config={"color": MY_DARK_GRAY, "include_tip": True, "stroke_width": 2, "include_numbers": True}, # Add include_numbers
            x_axis_config={"numbers_to_include": [-1, 1]},
            y_axis_config={"numbers_to_include": [-1, 1]},
            tips=False # Tips are handled in axis_config
        ) # Removed add_coordinates, numbers handled by axis_config
        x_label = axes.get_x_axis_label("x", edge=RIGHT, direction=RIGHT, buff=0.2)
        y_label = axes.get_y_axis_label("y", edge=UP, direction=UP, buff=0.2)
        axes_labels = VGroup(x_label, y_label).set_color(MY_DARK_GRAY)

        # Unit Circle
        # Calculate radius in screen units based on axes
        radius_val = 1.0
        origin_point = axes.c2p(0, 0)
        radius_point = axes.c2p(radius_val, 0)
        screen_radius = np.linalg.norm(radius_point - origin_point)
        circle = Circle(radius=screen_radius, color=MY_BLUE, stroke_width=3, arc_center=origin_point)

        # Radius, Point P, Angle Theta (using ValueTracker and always_redraw)
        self.theta_tracker.set_value(PI / 4) # Start at a non-zero angle for visual interest

        radius = always_redraw(
            lambda: Line(
                axes.c2p(0, 0),
                axes.c2p(radius_val * np.cos(self.theta_tracker.get_value()), radius_val * np.sin(self.theta_tracker.get_value())),
                color=MY_RED, stroke_width=3
            )
        )
        p_dot = always_redraw(
            lambda: Dot(
                axes.c2p(radius_val * np.cos(self.theta_tracker.get_value()), radius_val * np.sin(self.theta_tracker.get_value())),
                color=MY_RED, radius=0.08
            )
        )
        p_label = always_redraw(
            lambda: MathTex("P", color=MY_RED, font_size=36).next_to(p_dot.get_center(), UR, buff=0.1)
        )
        theta_arc = always_redraw(
            lambda: Arc(
                radius=0.4 * screen_radius, # Scale arc radius relative to circle radius
                start_angle=0,
                angle=self.theta_tracker.get_value(),
                color=MY_GREEN,
                arc_center=axes.c2p(0, 0)
            )
        )
        theta_label = always_redraw(
            lambda: MathTex(r"\theta", color=MY_GREEN, font_size=36).move_to(
                # Position label along the arc
                axes.c2p(0,0) + Arc(radius=0.6 * screen_radius, angle=self.theta_tracker.get_value()).point_from_proportion(0.5)
            )
        )
        # Position radius label relative to the midpoint of the radius line
        radius_label = always_redraw(
             lambda: MathTex("r=1", color=MY_RED, font_size=30).next_to(radius.get_center(), UR, buff=0.05)
        )


        # Group elements for easier management if needed later
        self.unit_circle_elements.add(axes, axes_labels, circle, radius, p_dot, p_label, theta_arc, theta_label, radius_label)
        # Add elements with updaters to the scene so they are drawn
        self.add(radius, p_dot, p_label, theta_arc, theta_label, radius_label)

        # --- TTS ---
        voice_text_01 = "Let's start with the unit circle. This is a circle centered at the origin with a radius of exactly one. We have our standard x and y axes. A point P moves along the circle. The line connecting the origin to P is the radius, which always has length 1. The angle between the positive x-axis and this radius is called theta."
        with custom_voiceover_tts(voice_text_01) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path)
            else:
                print("Warning: Scene 1 TTS failed.")

            subtitle_voice = Text(voice_text_01, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)

            # --- Animation ---
            self.play(FadeIn(title), FadeIn(subtitle_voice), run_time=1.0)
            self.play(Create(axes), Write(axes_labels), run_time=1.5) # Axes Create
            self.play(GrowFromCenter(circle), run_time=1.5) # Unit Circle Grow
            # Animate creation of elements with updaters
            self.play(Create(radius), Create(p_dot), FadeIn(p_label), run_time=1.0)
            self.play(Create(theta_arc), FadeIn(theta_label), run_time=1.0) # Angle Theta Form
            self.play(FadeIn(radius_label), run_time=0.5) # r=1 label

            # Wait according to audio duration
            anim_duration = 1.0 + 1.5 + 1.5 + 1.0 + 1.0 + 0.5
            wait_time = max(0, tracker.duration - anim_duration - 0.5) # Subtract fadeout time
            if wait_time > 0:
                self.wait(wait_time)
            self.play(FadeOut(subtitle_voice), run_time=0.5)

        # Store elements needed for next scene (or recreate them)
        # Since clear_and_reset is called, we need to recreate
        self.wait(1) # Hold final frame

    # --- Scene 2: Introducing Cosine as the X-Coordinate ---
    def play_scene_02(self):
        """Scene 2: Defines cosine as the x-coordinate on the unit circle."""
        # Background
        bg2 = Rectangle(width=config.frame_width, height=config.frame_height,
                        fill_color=MY_LIGHT_GRAY, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg2)

        # Scene Number
        scene_num_02 = self.get_scene_number("02", color=MY_BLACK)
        self.add(scene_num_02)

        # Recreate Unit Circle elements from Scene 1
        axes = Axes(
            x_range=[-1.5, 1.5, 1], y_range=[-1.5, 1.5, 1], x_length=6, y_length=6,
            axis_config={"color": MY_DARK_GRAY, "include_tip": True, "stroke_width": 2, "include_numbers": True},
            x_axis_config={"numbers_to_include": [-1, 1]}, y_axis_config={"numbers_to_include": [-1, 1]},
            tips=False
        )
        x_label = axes.get_x_axis_label("x", edge=RIGHT, direction=RIGHT, buff=0.2).set_color(MY_DARK_GRAY)
        y_label = axes.get_y_axis_label("y", edge=UP, direction=UP, buff=0.2).set_color(MY_DARK_GRAY)
        axes_labels = VGroup(x_label, y_label)

        radius_val = 1.0
        origin_point = axes.c2p(0, 0)
        radius_point = axes.c2p(radius_val, 0)
        screen_radius = np.linalg.norm(radius_point - origin_point)
        circle = Circle(radius=screen_radius, color=MY_BLUE, stroke_width=3, arc_center=origin_point)

        # Reset theta tracker for animation start
        self.theta_tracker.set_value(0)

        radius = always_redraw(lambda: Line(axes.c2p(0, 0), axes.c2p(radius_val * np.cos(self.theta_tracker.get_value()), radius_val * np.sin(self.theta_tracker.get_value())), color=MY_RED, stroke_width=3))
        p_dot = always_redraw(lambda: Dot(axes.c2p(radius_val * np.cos(self.theta_tracker.get_value()), radius_val * np.sin(self.theta_tracker.get_value())), color=MY_RED, radius=0.08))
        p_label = always_redraw(lambda: MathTex("P", color=MY_RED, font_size=36).next_to(p_dot.get_center(), UR, buff=0.1))
        theta_arc = always_redraw(lambda: Arc(radius=0.4 * screen_radius, start_angle=0, angle=self.theta_tracker.get_value(), color=MY_GREEN, arc_center=axes.c2p(0, 0)))
        theta_label = always_redraw(lambda: MathTex(r"\theta", color=MY_GREEN, font_size=36).move_to(axes.c2p(0,0) + Arc(radius=0.6 * screen_radius, angle=self.theta_tracker.get_value()).point_from_proportion(0.5)))

        # Add static elements to scene first
        self.add(axes, axes_labels, circle)
        # Add elements with updaters
        self.add(radius, p_dot, p_label, theta_arc, theta_label)

        # New elements for Scene 2
        # Vertical Drop Line
        vert_line = always_redraw(
            lambda: DashedLine(
                p_dot.get_center(), # Start at P
                axes.c2p(radius_val * np.cos(self.theta_tracker.get_value()), 0), # End on x-axis
                color=MY_ORANGE, stroke_width=2
            )
        )
        # Point on X-axis
        x_intersect_dot = always_redraw(
            lambda: Dot(axes.c2p(radius_val * np.cos(self.theta_tracker.get_value()), 0), color=MY_ORANGE, radius=0.06)
        )
        # Label "cos θ"
        cos_label = always_redraw(
            lambda: MathTex(r"\cos \theta", color=MY_ORANGE, font_size=36).next_to(x_intersect_dot.get_center(), DOWN, buff=0.2)
        )
        # Coordinate Labels for P
        coord_label = always_redraw(
            lambda: MathTex(r"(\cos \theta, \sin \theta)", color=MY_RED, font_size=36).next_to(p_dot.get_center(), RIGHT, buff=0.15)
        )

        # Explanatory Text
        explanation_text = Text("Cosine (cos θ) is the x-coordinate of point P on the unit circle.",
                                font_size=36, color=MY_BLACK).to_edge(UP, buff=0.5)

        # Group new elements
        cosine_elements = VGroup(vert_line, x_intersect_dot, cos_label, coord_label)
        # Add the updaters to the scene
        self.add(vert_line, x_intersect_dot, cos_label, coord_label)

        # --- TTS ---
        voice_text_02 = "Now, let's focus on the coordinates of point P. If we drop a vertical line from P down to the x-axis, the x-coordinate of this intersection point is defined as the cosine of the angle theta, written as cos theta. The y-coordinate is the sine of theta. So, the coordinates of P are (cos theta, sin theta). Watch how the x-coordinate, cos theta, changes as the angle theta increases."
        with custom_voiceover_tts(voice_text_02) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path)
            else:
                print("Warning: Scene 2 TTS failed.")

            subtitle_voice = Text(voice_text_02, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)

            # --- Animation ---
            self.play(FadeIn(explanation_text), FadeIn(subtitle_voice), run_time=1.0)
            # Animate creation of elements with updaters
            self.play(Create(vert_line), Create(x_intersect_dot), run_time=1.0)
            self.play(FadeIn(cos_label), FadeIn(coord_label), run_time=1.0)

            # Animate rotation
            rotate_duration = 5.0
            self.play(self.theta_tracker.animate.set_value(PI), run_time=rotate_duration, rate_func=linear)

            # Wait according to audio duration
            anim_duration = 1.0 + 1.0 + 1.0 + rotate_duration
            wait_time = max(0, tracker.duration - anim_duration - 0.5)
            if wait_time > 0:
                self.wait(wait_time)
            self.play(FadeOut(subtitle_voice), run_time=0.5)

        # Store elements for next scene
        self.unit_circle_elements = VGroup(axes, axes_labels, circle, radius, p_dot, p_label, theta_arc, theta_label, vert_line, x_intersect_dot, cos_label, coord_label)
        # Keep explanation text? No, clear_and_reset will handle it.
        self.wait(1)

    # --- Scene 3: Graphing Cosine vs. Angle ---
    def play_scene_03(self):
        """Scene 3: Connects the unit circle's x-coordinate to the cosine graph."""
        # Background
        bg3 = Rectangle(width=config.frame_width, height=config.frame_height,
                        fill_color=MY_LIGHT_GRAY, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg3)

        # Scene Number
        scene_num_03 = self.get_scene_number("03", color=MY_BLACK)
        self.add(scene_num_03)

        # --- Left Side: Unit Circle (Smaller) ---
        # Recreate unit circle elements, scaled and positioned left
        axes_unit = Axes(
            x_range=[-1.5, 1.5, 1], y_range=[-1.5, 1.5, 1], x_length=4, y_length=4, # Smaller length
            axis_config={"color": MY_DARK_GRAY, "include_tip": False, "stroke_width": 2, "include_numbers": True}, # No tips needed here
            x_axis_config={"numbers_to_include": [-1, 1]}, y_axis_config={"numbers_to_include": [-1, 1]},
            tips=False
        )
        radius_val_unit = 1.0
        origin_point_unit = axes_unit.c2p(0, 0)
        radius_point_unit = axes_unit.c2p(radius_val_unit, 0)
        screen_radius_unit = np.linalg.norm(radius_point_unit - origin_point_unit)
        circle_unit = Circle(radius=screen_radius_unit, color=MY_BLUE, stroke_width=3, arc_center=origin_point_unit)

        # Reset theta for this animation
        self.theta_tracker.set_value(0)

        radius_unit = always_redraw(lambda: Line(axes_unit.c2p(0, 0), axes_unit.c2p(radius_val_unit * np.cos(self.theta_tracker.get_value()), radius_val_unit * np.sin(self.theta_tracker.get_value())), color=MY_RED, stroke_width=3))
        p_dot_unit = always_redraw(lambda: Dot(axes_unit.c2p(radius_val_unit * np.cos(self.theta_tracker.get_value()), radius_val_unit * np.sin(self.theta_tracker.get_value())), color=MY_RED, radius=0.06))
        theta_arc_unit = always_redraw(lambda: Arc(radius=0.3 * screen_radius_unit, start_angle=0, angle=self.theta_tracker.get_value(), color=MY_GREEN, arc_center=axes_unit.c2p(0, 0)))
        vert_line_unit = always_redraw(lambda: DashedLine(p_dot_unit.get_center(), axes_unit.c2p(radius_val_unit * np.cos(self.theta_tracker.get_value()), 0), color=MY_ORANGE, stroke_width=2))
        x_intersect_dot_unit = always_redraw(lambda: Dot(axes_unit.c2p(radius_val_unit * np.cos(self.theta_tracker.get_value()), 0), color=MY_ORANGE, radius=0.05))
        cos_label_unit = always_redraw(lambda: MathTex(r"\cos \theta", color=MY_ORANGE, font_size=30).next_to(x_intersect_dot_unit.get_center(), DOWN, buff=0.15))

        unit_circle_group_small = VGroup(axes_unit, circle_unit, radius_unit, p_dot_unit, theta_arc_unit, vert_line_unit, x_intersect_dot_unit, cos_label_unit)
        unit_circle_group_small.scale(0.8).to_edge(LEFT, buff=1.0)
        # Add the updaters to the scene
        self.add(radius_unit, p_dot_unit, theta_arc_unit, vert_line_unit, x_intersect_dot_unit, cos_label_unit)


        # --- Right Side: Cosine Graph ---
        axes_graph = Axes(
            x_range=[0, 2 * PI + 0.1, PI / 2], # Range 0 to 2pi, step pi/2
            y_range=[-1.2, 1.2, 1], # Range -1.2 to 1.2, step 1
            x_length=8, y_length=4,
            axis_config={"color": MY_DARK_GRAY, "include_tip": True, "stroke_width": 2, "include_numbers": True},
            x_axis_config={
                "include_numbers": False, # Disable default numbers on x-axis for custom Pi labels
            },
            # Ensure y-axis numbers are included via axis_config or y_axis_config
            y_axis_config={"numbers_to_include": [-1, 0, 1]},
            tips=False
        )
        # REMOVED the conflicting add_coordinates call

        # Manually add Pi labels for x-axis
        x_labels_pi = VGroup()
        custom_x_values_labels = {
            0: "0", # Add 0 label manually
            PI/2: r"\pi/2",
            PI: r"\pi",
            3*PI/2: r"3\pi/2",
            2*PI: r"2\pi"
        }
        for x_val, label_tex in custom_x_values_labels.items():
            label = MathTex(label_tex, font_size=24, color=MY_DARK_GRAY)
            label.next_to(axes_graph.c2p(x_val, 0), DOWN, buff=0.15)
            x_labels_pi.add(label)

        x_graph_label = axes_graph.get_x_axis_label(r"\theta", edge=DOWN, direction=DOWN, buff=0.3).set_color(MY_DARK_GRAY) # Increased buff
        y_graph_label = axes_graph.get_y_axis_label(r"\cos \theta", edge=LEFT, direction=LEFT, buff=0.2).set_color(MY_DARK_GRAY)
        axes_graph_labels = VGroup(x_graph_label, y_graph_label)
        graph_group = VGroup(axes_graph, axes_graph_labels, x_labels_pi).to_edge(RIGHT, buff=1.0)

        # Cosine function graph (create BEFORE animation)
        cosine_graph = axes_graph.plot(lambda x: np.cos(x), x_range=[0, 2 * PI], color=MY_ORANGE, stroke_width=3)

        # Moving dot on the graph
        moving_dot_graph = always_redraw(
            lambda: Dot(
                axes_graph.input_to_graph_point(self.theta_tracker.get_value(), cosine_graph), # Use input_to_graph_point
                color=MY_RED, radius=0.08
            )
        )
        # Line connecting unit circle x-value to graph dot
        connecting_line = always_redraw(
            lambda: DashedLine(
                x_intersect_dot_unit.get_center(), # Start at cos(theta) point on unit circle x-axis
                moving_dot_graph.get_center(),     # End at the moving dot on the graph
                stroke_width=1, color=MY_DARK_GRAY, dash_length=0.05
            )
        )

        # Group graph elements (add cosine_graph here)
        self.graph_elements.add(graph_group, cosine_graph, moving_dot_graph, connecting_line)
        # Add graph updaters
        self.add(moving_dot_graph, connecting_line)

        # --- TTS ---
        voice_text_03 = "Now, let's visualize how the cosine value relates to its graph. On the left, we have our unit circle. On the right, we'll plot the angle theta on the horizontal axis and the value of cos theta (the x-coordinate from the unit circle) on the vertical axis. As the angle theta increases from 0 to 2 pi on the unit circle, watch how the corresponding cos theta value traces out the familiar cosine wave on the graph."
        with custom_voiceover_tts(voice_text_03) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path)
            else:
                print("Warning: Scene 3 TTS failed.")

            subtitle_voice = Text(voice_text_03, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)

            # --- Animation ---
            self.play(FadeIn(subtitle_voice), run_time=0.5)
            # Bring in elements (add cosine_graph here, but don't animate yet)
            self.play(FadeIn(unit_circle_group_small, shift=RIGHT), Create(graph_group), run_time=2.0)
            # Add dynamic elements that depend on theta_tracker *after* axes/circle exist
            self.add(moving_dot_graph, connecting_line) # Add dynamic elements

            # Synchronized animation: Rotate radius and Create graph
            graph_creation_duration = 6.0
            self.play(
                self.theta_tracker.animate.set_value(2 * PI), # Rotate full circle
                Create(cosine_graph), # Draw the graph simultaneously
                run_time=graph_creation_duration,
                rate_func=linear # Ensure smooth, constant speed
            )
            # No need to replace trace now

            # Wait according to audio duration
            anim_duration = 0.5 + 2.0 + graph_creation_duration
            wait_time = max(0, tracker.duration - anim_duration - 0.5)
            if wait_time > 0:
                self.wait(wait_time)
            self.play(FadeOut(subtitle_voice), run_time=0.5)

        # Store elements for next scene
        self.unit_circle_elements = unit_circle_group_small
        # self.graph_elements already contains [graph_group, cosine_graph, moving_dot_graph, connecting_line]
        self.wait(1)

    # --- Scene 4: Highlighting Key Features ---
    def play_scene_04(self):
        """Scene 4: Highlights key points (max, min, zeros) on the cosine graph."""
        # Background (reuse light gray)
        bg4 = Rectangle(width=config.frame_width, height=config.frame_height,
                        fill_color=MY_LIGHT_GRAY, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg4) # Add background if cleared, otherwise it persists

        # Scene Number
        scene_num_04 = self.get_scene_number("04", color=MY_BLACK)
        self.add(scene_num_04)

        # Ensure elements from Scene 3 are present and remove updaters
        # Remove updaters from unit circle elements
        for mob in self.unit_circle_elements:
             if mob is not None and hasattr(mob, 'clear_updaters') and mob.get_updaters(): mob.clear_updaters()

        # Identify and remove updater elements from graph_elements
        # Check if graph_elements has enough items before accessing indices
        if len(self.graph_elements) >= 4:
            graph_group = self.graph_elements.submobjects[0]
            cosine_graph_obj = self.graph_elements.submobjects[1]
            moving_dot_graph = self.graph_elements.submobjects[2]
            connecting_line = self.graph_elements.submobjects[3]

            # Clear updaters and remove from scene and group
            moving_dot_graph.clear_updaters()
            connecting_line.clear_updaters()
            self.remove(moving_dot_graph, connecting_line)
            # Remove by object identity to be safe
            self.graph_elements.remove(moving_dot_graph)
            self.graph_elements.remove(connecting_line)
        elif len(self.graph_elements) >= 2:
             # Fallback if updaters were already removed or structure changed
             graph_group = self.graph_elements.submobjects[0]
             cosine_graph_obj = self.graph_elements.submobjects[1]
             print("Warning: Updater elements not found as expected in graph_elements for Scene 4.")
        else:
             print("Error: graph_elements structure incorrect for Scene 4.")
             return


        # Add the static elements back (or ensure they are still added)
        self.add(self.unit_circle_elements, self.graph_elements) # Adds graph_group and cosine_graph_obj

        # Retrieve axes_graph for calculations
        axes_graph = None
        if isinstance(graph_group, VGroup): # graph_group is a VGroup
             for sub_item in graph_group:
                 if isinstance(sub_item, Axes):
                     axes_graph = sub_item
                     break
        if not axes_graph:
            print("Error: Could not find axes_graph in graph_group")
            return # Cannot proceed without axes

        # Title
        title = Text("Key Values and Properties of Cosine", font_size=36, color=MY_BLACK).to_edge(UP, buff=0.5)

        # Key angles and values
        key_angles = [0, PI / 2, PI, 3 * PI / 2, 2 * PI]
        key_values = [1, 0, -1, 0, 1]
        # Use input_to_graph_point to get points on the actual graph curve
        # cosine_graph_obj is already correctly identified
        # Ensure cosine_graph_obj has points before calling input_to_graph_point
        if not cosine_graph_obj.has_points():
             print("Error: cosine_graph_obj has no points in Scene 4!")
             # Attempt to regenerate points if possible, though this indicates a deeper issue
             # cosine_graph_obj.generate_points() # This might not work depending on how it was created
             return

        key_points_graph_coords = [axes_graph.input_to_graph_point(angle, cosine_graph_obj) for angle in key_angles]


        # Vertical Dashed Lines and Labels
        v_lines = VGroup()
        v_labels = VGroup()
        for angle in key_angles:
            # Use get_vertical_line from axes, ensuring it ends on the axis line
            # Use i2gp (input to graph point) to get the point on the curve for the line start
            line = axes_graph.get_vertical_line(axes_graph.i2gp(angle, cosine_graph_obj), color=MY_DARK_GRAY, stroke_width=1, line_func=DashedLine)
            label_text = ""
            if np.isclose(angle, 0): label_text = "0"
            elif np.isclose(angle, PI/2): label_text = r"\pi/2"
            elif np.isclose(angle, PI): label_text = r"\pi"
            elif np.isclose(angle, 3*PI/2): label_text = r"3\pi/2"
            elif np.isclose(angle, 2*PI): label_text = r"2\pi"

            if label_text:
                # Find existing label if it exists, otherwise create new
                existing_label = None
                for lbl_group in graph_group: # Search within graph_group
                    if isinstance(lbl_group, VGroup): # x_labels_pi is a VGroup
                        for lbl in lbl_group:
                            # Check if MathTex and matches text (approximate for floats if needed)
                            if isinstance(lbl, MathTex) and lbl.tex_string == label_text:
                                existing_label = lbl
                                break
                    if existing_label: break

                if existing_label:
                    v_labels.add(existing_label) # Add existing label
                else: # Create new if not found (shouldn't happen with current logic)
                    label = MathTex(label_text, font_size=24, color=MY_DARK_GRAY).next_to(axes_graph.c2p(angle, 0), DOWN, buff=0.15)
                    v_labels.add(label)
                v_lines.add(line)


        # Horizontal Dashed Lines and Labels
        h_lines = VGroup()
        h_labels = VGroup()
        for val in [-1, 0, 1]:
             # Use get_horizontal_line from axes
            line = axes_graph.get_horizontal_line(axes_graph.c2p(0, val), color=MY_DARK_GRAY, stroke_width=1, line_func=DashedLine)
            # Check if label exists in axes numbers
            label = axes_graph.get_y_axis().get_number_mobject(val)
            if label is None: # Create if not found
                 label = MathTex(str(val), font_size=24, color=MY_DARK_GRAY)
                 label.next_to(axes_graph.c2p(0, val), LEFT, buff=0.15)
            else: # Reposition if found
                 label.next_to(axes_graph.c2p(0, val), LEFT, buff=0.15)

            h_lines.add(line)
            h_labels.add(label)

        # Highlighting Key Points
        highlights = VGroup()
        for point_coord in key_points_graph_coords:
            # Use Circle for highlighting
            highlight = Circle(radius=0.15, color=MY_PURPLE, fill_opacity=0.3, stroke_width=0).move_to(point_coord)
            highlights.add(highlight)

        # Arrows from Unit Circle to Graph Points
        # Retrieve unit circle axes
        axes_unit = None
        for item in self.unit_circle_elements:
             if isinstance(item, Axes):
                 axes_unit = item
                 break
        if not axes_unit:
             print("Error: Could not find axes_unit in self.unit_circle_elements")
             return

        radius_val_unit = 1.0 # Should match Scene 3
        unit_circle_points_coords = [
            axes_unit.c2p(radius_val_unit * np.cos(angle), radius_val_unit * np.sin(angle)) for angle in key_angles
        ]
        arrows = VGroup()
        for i, angle in enumerate(key_angles):
            start_point = unit_circle_points_coords[i] # Point on unit circle
            end_point = key_points_graph_coords[i]     # Corresponding point on graph
            # Ensure start and end points are valid numpy arrays
            if isinstance(start_point, np.ndarray) and isinstance(end_point, np.ndarray):
                 # Check for NaN or Inf values which can cause issues
                 if not np.any(np.isnan(start_point)) and not np.any(np.isnan(end_point)) and \
                    not np.any(np.isinf(start_point)) and not np.any(np.isinf(end_point)):
                     arrow = Arrow(start_point, end_point, buff=0.1, color=MY_PURPLE, stroke_width=2, max_tip_length_to_length_ratio=0.1)
                     arrows.add(arrow)
                 else:
                     print(f"Warning: Skipping arrow {i} due to NaN/Inf coordinates. Start: {start_point}, End: {end_point}")
            else:
                 print(f"Warning: Invalid coordinate type for arrow {i}. Start: {type(start_point)}, End: {type(end_point)}")


        # --- TTS ---
        voice_text_04 = "Let's examine some key features. When theta is 0, cos theta is 1, the maximum value. At pi/2, cos theta is 0. At pi, cos theta reaches its minimum, -1. At 3 pi/2, it's 0 again. And at 2 pi, it returns to 1, completing one cycle. These points correspond directly to the x-coordinates on the unit circle at those angles."
        with custom_voiceover_tts(voice_text_04) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path)
            else:
                print("Warning: Scene 4 TTS failed.")

            subtitle_voice = Text(voice_text_04, font_size=28, color=MY_BLACK, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)

            # --- Animation ---
            self.play(FadeIn(title), FadeIn(subtitle_voice), run_time=1.0)
            # Ensure labels are added before animating them
            self.add(v_labels, h_labels)
            self.play(Create(v_lines), Create(h_lines), FadeIn(v_labels), FadeIn(h_labels), run_time=2.0)

            # Highlight points sequentially
            highlight_anims = []
            for i in range(len(highlights)): # Iterate through highlights created
                 # Indicate uses Flash by default, which is good here
                highlight_anims.append(Indicate(highlights[i], color=MY_PURPLE, scale_factor=1.5, run_time=0.8))
                if i < len(arrows): # Check if arrow exists for this index
                    highlight_anims.append(Create(arrows[i], run_time=0.8))
                highlight_anims.append(Wait(0.3)) # Pause between highlights

            if highlight_anims: # Only play if there are animations
                self.play(Succession(*highlight_anims))

            # Wait according to audio duration
            highlight_duration = len(highlights) * (0.8 + 0.3) + len(arrows) * 0.8 # Approx duration
            anim_duration = 1.0 + 2.0 + highlight_duration
            wait_time = max(0, tracker.duration - anim_duration - 0.5)
            if wait_time > 0:
                self.wait(wait_time)
            self.play(FadeOut(subtitle_voice), run_time=0.5)

        # Keep elements for potential fade in next scene
        self.wait(1)

    # --- Scene 5: Conclusion ---
    def play_scene_05(self):
        """Scene 5: Concludes the explanation."""
        # Background
        bg5 = Rectangle(width=config.frame_width, height=config.frame_height,
                        fill_color=MY_CONCLUSION_BG, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg5)

        # Scene Number
        scene_num_05 = self.get_scene_number("05", color=MY_CONCLUSION_SUB) # Lighter color for dark bg
        self.add(scene_num_05)

        # Faded Elements (reuse from previous state, apply opacity)
        # Ensure they are added before applying opacity if they weren't already
        # Remove updaters if any persist
        for mob in self.unit_circle_elements:
             if mob is not None and hasattr(mob, 'clear_updaters') and mob.get_updaters(): mob.clear_updaters()
        for mob in self.graph_elements:
             if mob is not None and hasattr(mob, 'clear_updaters') and mob.get_updaters(): mob.clear_updaters()

        # Add elements if they are not already in the scene (e.g., after clear_and_reset)
        # This might require recreating them if clear_and_reset was called before this scene
        # Assuming they persist from Scene 4:
        self.add(self.unit_circle_elements, self.graph_elements)
        faded_elements = VGroup(self.unit_circle_elements, self.graph_elements)

        # Position faded elements side-by-side nicely
        self.unit_circle_elements.move_to(LEFT * (config.frame_width / 4))
        self.graph_elements.move_to(RIGHT * (config.frame_width / 4))
        # Apply fade effect *after* positioning
        faded_elements.set_opacity(0.3)

        # Final Text
        final_text = Text("Cosine: The x-coordinate on the Unit Circle!",
                          font_size=48, color=MY_CONCLUSION_FG, weight=BOLD)
        final_text.move_to(ORIGIN + UP * 0.5)

        thanks_text = Text("Thank You!", font_size=36, color=MY_CONCLUSION_SUB)
        thanks_text.next_to(final_text, DOWN, buff=0.5)

        # --- TTS ---
        voice_text_05 = "So, remember: the cosine of an angle theta is simply the x-coordinate of the point where the terminal side of the angle intersects the unit circle. Understanding this connection is key to mastering trigonometry. Thank you for watching!"
        with custom_voiceover_tts(voice_text_05) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path)
            else:
                print("Warning: Scene 5 TTS failed.")

            subtitle_voice = Text(voice_text_05, font_size=28, color=MY_CONCLUSION_SUB, width=config.frame_width - 2, should_center=True).to_edge(DOWN, buff=0.4)

            # --- Animation ---
            # Fade in faded elements (optional, could start with them visible)
            self.play(FadeIn(faded_elements), run_time=1.0) # Fade them in gently
            self.play(FadeIn(subtitle_voice), run_time=0.5)
            self.play(Write(final_text), run_time=2.0)
            self.play(FadeIn(thanks_text), run_time=1.0)

            # Slight zoom on final text
            self.play(self.camera.frame.animate.scale(0.9).move_to(final_text.get_center()), run_time=1.5)

            # Wait according to audio duration
            anim_duration = 1.0 + 0.5 + 2.0 + 1.0 + 1.5
            wait_time = max(0, tracker.duration - anim_duration - 0.5)
            if wait_time > 0:
                self.wait(wait_time)
            self.play(FadeOut(subtitle_voice), run_time=0.5)

        self.wait(2) # Hold final screen

# --- Main execution block ---
if __name__ == "__main__":
    # Basic configuration
    config.pixel_height = 1080
    config.pixel_width = 1920
    config.frame_rate = 30
    config.output_file = "CombinedScene"
    config.disable_caching = True

    # Set output directory using placeholder
    config.media_dir = r"#(output_path)" # Use raw string for placeholder

    # Create and render the scene
    scene = CombinedScene()
    scene.render()

    print(f"Scene rendering finished. Output in: {config.media_dir}")