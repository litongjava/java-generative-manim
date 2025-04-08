# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
import hashlib
import manimpango # For font checking

from moviepy import AudioFileClip # Correct import for AudioFileClip
# Removed the problematic import for contrasting_color

# --- Font Check ---
DEFAULT_FONT = "Noto Sans CJK SC" # Example desired font
available_fonts = manimpango.list_fonts()
final_font = None

if DEFAULT_FONT in available_fonts:
    print(f"Font '{DEFAULT_FONT}' found.")
    final_font = DEFAULT_FONT
else:
    print(f"Warning: Font '{DEFAULT_FONT}' not found. Trying fallback fonts...")
    # Fallback fonts suitable for English/Math primarily
    fallback_fonts = ["Arial", "DejaVu Sans", "Liberation Sans", "Microsoft YaHei"]
    found_fallback = False
    for font in fallback_fonts:
        if font in available_fonts:
            print(f"Switched to fallback font: '{font}'")
            final_font = font
            found_fallback = True
            break
    if not found_fallback:
        print(f"Warning: Neither the specified '{DEFAULT_FONT}' nor any fallback fonts were found. Using Manim's default font.")
        # final_font remains None

# --- Custom Colors ---
MY_LIGHT_BLUE = "#ADD8E6"
MY_LIGHT_YELLOW = "#FFFFE0"
MY_LIGHT_GREEN = "#90EE90"
MY_LIGHT_PURPLE = "#E6E6FA"
MY_DARK_BLUE = "#1E3A8A"
MY_WHITE = "#FFFFFF"
MY_BLACK = "#000000"
MY_ORANGE = "#FFA500"
MY_RED = "#DC2626" # Red for emphasis
MY_BLUE = "#3B82F6" # Blue for blocks
MY_GREEN = "#10B981" # Green for blocks

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
    # Use a language code prefix if supporting multiple languages
    lang_prefix = "en_" # Assuming English for this script
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{lang_prefix}{text_hash}.mp3")


@contextmanager
def custom_voiceover_tts(text, token="123456", base_url="https://uni-ai.fly.dev/api/manim/tts"):
    """
    Fetches TTS audio, caches it, and provides path and duration.
    Usage: with custom_voiceover_tts("text") as tracker: ...
    """
    cache_file = get_cache_filename(text)
    audio_file = cache_file  # Initialize audio_file

    if os.path.exists(cache_file):
        audio_file = cache_file
        # print(f"Using cached TTS for: {text[:30]}...")
    else:
        # print(f"Requesting TTS for: {text[:30]}...")
        try:
            # URL encode the input text to handle special characters
            input_text_encoded = requests.utils.quote(text)
            url = f"{base_url}?token={token}&input={input_text_encoded}"

            response = requests.get(url, stream=True, timeout=60)  # Added timeout
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            with open(cache_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            audio_file = cache_file
            # print("TTS downloaded and cached.")

        except requests.exceptions.RequestException as e:
            print(f"TTS API request failed: {e}")
            # Fallback: create a dummy tracker with zero duration
            tracker = CustomVoiceoverTracker(None, 0)
            yield tracker
            return  # Exit context manager
        except Exception as e:
             # Clean up potentially incomplete cache file on error
            if os.path.exists(cache_file):
                os.remove(cache_file)
            print(f"An error occurred during TTS processing: {e}")
            tracker = CustomVoiceoverTracker(None, 0)
            yield tracker
            return # Exit context manager


    # Ensure audio file exists before processing with MoviePy
    if audio_file and os.path.exists(audio_file):
        try:
            # Use context manager for AudioFileClip
            with AudioFileClip(audio_file) as clip:
                duration = clip.duration
            # print(f"Audio duration: {duration:.2f}s")
            tracker = CustomVoiceoverTracker(audio_file, duration)
        except Exception as e:
            print(f"Error processing audio file {audio_file}: {e}")
            # Fallback if audio file is corrupted or invalid
            if os.path.exists(cache_file): # Clean up potentially bad cache file
                try:
                    os.remove(cache_file)
                except OSError as rm_err:
                    print(f"Error removing corrupted cache file {cache_file}: {rm_err}")
            tracker = CustomVoiceoverTracker(None, 0)
    else:
        # Fallback if audio file was not created or found
        print(f"TTS audio file not found or not created: {audio_file}")
        tracker = CustomVoiceoverTracker(None, 0)

    try:
        yield tracker
    finally:
        # No cleanup needed here as we are caching
        pass

# --- Helper Function for Creating Grids ---
def create_grid(rows, cols, square_size=0.4, spacing=0.05, color=BLUE):
    """Creates a VGroup representing a grid of squares."""
    grid = VGroup()
    total_width = cols * square_size + (cols - 1) * spacing
    total_height = rows * square_size + (rows - 1) * spacing
    start_x = -total_width / 2 + square_size / 2
    start_y = total_height / 2 - square_size / 2

    for r in range(rows):
        for c in range(cols):
            # Use a fixed contrasting color like black for the stroke
            stroke_col = MY_BLACK # <<< CHANGED HERE
            square = Square(side_length=square_size, color=color, fill_color=color, fill_opacity=0.7, stroke_width=1, stroke_color=stroke_col) # Use stroke_col here
            x = start_x + c * (square_size + spacing)
            y = start_y - r * (square_size + spacing)
            square.move_to([x, y, 0])
            grid.add(square)
    return grid

# --- Combined Scene ---
class CombinedScene(MovingCameraScene):
    """
    Combines all scenes for the graphical proof of the associative property
    of multiplication: (7 x 5) x 2 = 7 x (5 x 2).
    """
    def setup(self):
        """Set default font if found."""
        MovingCameraScene.setup(self)
        if final_font:
            Text.set_default(font=final_font)

    def construct(self):
        # --- Play Scenes Sequentially ---
        self.play_scene_01()
        self.clear_and_reset()

        self.play_scene_02()
        # Don't clear yet, Scene 3 builds on Scene 2's result visually
        # self.clear_and_reset() # Keep elements for Scene 3

        self.play_scene_03()
        # Don't clear yet, Scene 4 uses results from 2 and 3
        # self.clear_and_reset() # Keep elements for Scene 4

        self.play_scene_04()
        self.clear_and_reset()

        self.play_scene_05()
        self.clear_and_reset()

        # End of animation message
        final_message = Text("Animation finished, thanks for watching! 😄", font_size=48, color=MY_WHITE)
        bg_final = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=MY_BLACK, fill_opacity=1,
                             stroke_width=0).set_z_index(-10)
        self.add(bg_final)
        self.play(FadeIn(final_message))
        self.wait(2)

    def get_scene_number(self, number_str):
        """Creates and positions the scene number."""
        scene_num = Text(number_str, font_size=24, color=MY_WHITE)
        scene_num.to_corner(UR, buff=0.3)
        scene_num.set_z_index(10)
        return scene_num

    def clear_and_reset(self):
        """Clears all objects and resets the camera."""
        # Clear updaters from all mobjects
        mobjects_to_clear = list(self.mobjects) # Create a copy to iterate over
        for mob in mobjects_to_clear:
            if mob is not None and hasattr(mob, 'get_updaters') and mob.get_updaters():
                mob.clear_updaters()

        # Use Group for fading out potentially mixed object types
        valid_mobjects = [m for m in self.mobjects if m is not None]
        all_mobjects_group = Group(*valid_mobjects)

        if all_mobjects_group:
            self.play(FadeOut(all_mobjects_group, shift=DOWN * 0.5), run_time=0.5)

        self.clear() # Clears self.mobjects

        # Reset camera
        self.camera.frame.move_to(ORIGIN)
        self.camera.frame.set(width=config.frame_width, height=config.frame_height)
        # self.camera.frame.set_euler_angles(theta=0, phi=0, gamma=0) # Reset rotation if any

        self.wait(0.1)

    # --- Scene 1: Introduction ---
    def play_scene_01(self):
        """Scene 1: Introduction and problem presentation."""
        bg_color = MY_LIGHT_BLUE
        text_color = MY_BLACK

        # Background
        bg1 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=bg_color, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg1)

        # Scene Number
        scene_num_01 = self.get_scene_number("01").set_color(text_color)
        self.add(scene_num_01)

        # Title
        title = Text("Graphical Proof of Associative Property of Multiplication", font_size=48, color=text_color)
        title.to_edge(UP, buff=0.8)

        # Expressions
        expr1_math = MathTex("(7 \\times 5) \\times 2", font_size=60, color=text_color)
        expr2_math = MathTex("7 \\times (5 \\times 2)", font_size=60, color=text_color)
        question_mark = MathTex("?", font_size=60, color=MY_ORANGE)

        # Arrange expressions and question mark
        proof_line = VGroup(expr1_math, question_mark, expr2_math).arrange(RIGHT, buff=0.5)
        proof_line.next_to(title, DOWN, buff=1.0)

        # --- TTS Integration ---
        voice_text_01 = "Hello! Today, we'll explore the associative property of multiplication using graphics. We want to visually prove that multiplying 7 by 5, then by 2, gives the same result as multiplying 7 by the result of 5 times 2. Is (7 times 5) times 2 equal to 7 times (5 times 2)?"
        with custom_voiceover_tts(voice_text_01) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("Warning: Scene 1 TTS audio failed or has zero duration.")

            subtitle_voice = Text(
                voice_text_01, font_size=32, color=text_color,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # Animations
            self.play(FadeIn(title), run_time=1.5)
            self.play(FadeIn(subtitle_voice, run_time=0.5)) # Show subtitle early

            self.play(Write(expr1_math), run_time=1.5)
            self.play(Write(question_mark), run_time=0.5)
            self.play(Write(expr2_math), run_time=1.5)

            # Camera zoom
            self.play(self.camera.frame.animate.scale(0.9).move_to(proof_line.get_center() + UP*0.5), run_time=1.0)

            # Calculate wait time
            anim_time = 1.5 + 0.5 + 1.5 + 0.5 + 1.5 + 1.0 # Animation time
            if tracker.duration > 0:
                remaining_time = tracker.duration - anim_time - 1.0 # Subtract fade out time
                if remaining_time > 0:
                    self.wait(remaining_time)
            else:
                self.wait(1.0) # Wait if no audio

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        # Store expressions for next scenes if needed (or recreate)
        self.expr1_math_obj = expr1_math
        self.expr2_math_obj = expr2_math
        self.proof_line_obj = proof_line
        self.title_obj = title
        # Keep elements for potential transition, or clear them in clear_and_reset

    # --- Scene 2: Visualize (7 x 5) x 2 ---
    def play_scene_02(self):
        """Scene 2: Visualize (7 x 5) x 2 and rearrange."""
        bg_color = MY_LIGHT_YELLOW
        text_color = MY_BLACK
        block_color_1 = MY_BLUE
        block_color_2 = MY_RED

        # Clear previous scene elements before adding new background
        self.clear_and_reset()

        # Background
        bg2 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=bg_color, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg2)

        # Scene Number
        scene_num_02 = self.get_scene_number("02").set_color(text_color)
        self.add(scene_num_02)

        # Title/Label for this part
        viz_label = Text("Visualizing (7 x 5) x 2", font_size=36, color=text_color).to_edge(UP, buff=0.5)
        self.add(viz_label)

        # Create 7x5 grid
        rows1, cols1 = 7, 5
        grid1 = create_grid(rows1, cols1, color=block_color_1)
        grid1_label = MathTex(f"{rows1} \\times {cols1}", font_size=30, color=text_color).next_to(grid1, DOWN, buff=0.2)

        # Create the second 7x5 grid
        grid2 = create_grid(rows1, cols1, color=block_color_2)

        # Group the two grids
        group_7x5x2 = VGroup(grid1, grid2).arrange(RIGHT, buff=0.5)
        group_7x5x2.move_to(ORIGIN + DOWN * 0.5).scale(0.9) # Position and scale

        # Label for the combined group
        brace = Brace(group_7x5x2, direction=DOWN, color=text_color)
        group_label = brace.get_tex("(7 \\times 5) \\times 2", font_size=36).set_color(text_color)

        # Target arrangement: 7x10 grid
        rows_target, cols_target = 7, 10
        target_grid_pos = ORIGIN + DOWN * 0.5 # Same center as group_7x5x2
        # Use a distinct color for the target grid
        target_grid_color = MY_GREEN
        target_squares = VGroup(*[
            # Use MY_BLACK for stroke color directly
            Square(side_length=0.4, color=target_grid_color, fill_color=target_grid_color, fill_opacity=0.7, stroke_width=1, stroke_color=MY_BLACK)
            for _ in range(rows_target * cols_target)
        ]).arrange_in_grid(rows=rows_target, cols=cols_target, buff=0.05).move_to(target_grid_pos).scale(0.9)

        # --- TTS Integration ---
        voice_text_02 = "Let's first visualize (7 times 5) times 2. We start with a block representing 7 times 5, containing 35 small squares. The expression means we need two of these blocks. Here's the second one. Together, these represent (7 times 5) times 2. Now, let's rearrange all these 70 squares into one single rectangle. We can arrange them into a rectangle with 7 rows and 10 columns."
        with custom_voiceover_tts(voice_text_02) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("Warning: Scene 2 TTS audio failed or has zero duration.")

            subtitle_voice = Text(
                voice_text_02, font_size=32, color=text_color,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # Animations
            self.play(FadeIn(subtitle_voice, run_time=0.5))
            self.play(Create(grid1), Write(grid1_label), run_time=2.0)
            self.wait(0.5)
            # Position grid2 initially off-screen or faded, then move/fade in
            grid2.next_to(grid1, RIGHT, buff=0.5)
            self.play(FadeIn(grid2, shift=RIGHT*0.5), run_time=1.5)
            self.wait(0.5)
            self.play(GrowFromCenter(brace), Write(group_label), run_time=1.5)
            self.wait(1.0) # Pause before rearrangement

            # Rearrangement animation
            # Create a combined list of squares from grid1 and grid2
            all_squares_start = VGroup(*grid1.submobjects, *grid2.submobjects)
            # Create target squares for the transform animation
            target_squares_transform = target_squares.copy() # Use a copy for the transform target

            self.play(
                FadeOut(grid1_label, brace, group_label), # Fade out labels
                # Transform squares individually
                Transform(all_squares_start, target_squares_transform, lag_ratio=0.01, run_time=3.0)
            )
            # After transform, all_squares_start holds the transformed squares
            # We might want to replace it with a clean target_grid for future use
            self.remove(all_squares_start) # Remove the transformed group
            self.add(target_squares) # Add the clean target grid

            # Label the final rearranged grid
            rearranged_label = MathTex("= 7 \\times 10 = 70", font_size=36, color=text_color).next_to(target_squares, DOWN, buff=0.3)
            self.play(Write(rearranged_label), run_time=1.0)

            # Calculate wait time
            anim_time = 0.5 + 2.0 + 0.5 + 1.5 + 0.5 + 1.5 + 1.0 + 3.0 + 1.0 # Animation time
            if tracker.duration > 0:
                remaining_time = tracker.duration - anim_time - 1.0 # Subtract fade out time
                if remaining_time > 0:
                    self.wait(remaining_time)
            else:
                self.wait(1.0) # Wait if no audio

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        # Store the final grid for Scene 4
        self.final_grid_scene2 = target_squares
        self.final_label_scene2 = rearranged_label
        self.viz_label_scene2 = viz_label # Keep track of labels to fade out later

    # --- Scene 3: Visualize 7 x (5 x 2) ---
    def play_scene_03(self):
        """Scene 3: Visualize 7 x (5 x 2) and rearrange."""
        bg_color = MY_LIGHT_GREEN
        text_color = MY_BLACK
        block_color = MY_GREEN # Use a single color for these blocks

        # Fade out elements from Scene 2 before adding new background
        # Keep the final grid if needed for comparison later, otherwise fade it out too.
        # Let's fade out everything from Scene 2 for a clean start for Scene 3's visualization
        self.play(FadeOut(Group(*self.mobjects))) # Fade out everything currently on screen
        self.clear() # Clear mobjects list

        # Background
        bg3 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=bg_color, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg3)

        # Scene Number
        scene_num_03 = self.get_scene_number("03").set_color(text_color)
        self.add(scene_num_03)

        # Title/Label for this part
        viz_label = Text("Visualizing 7 x (5 x 2)", font_size=36, color=text_color).to_edge(UP, buff=0.5)
        self.add(viz_label)

        # Create 5x2 grid
        rows2, cols2 = 5, 2
        base_grid = create_grid(rows2, cols2, color=block_color)
        base_grid_label = MathTex(f"{rows2} \\times {cols2}", font_size=30, color=text_color).next_to(base_grid, DOWN, buff=0.2)

        # Replicate it 7 times
        num_replications = 7
        group_7_of_5x2 = VGroup(*[base_grid.copy() for _ in range(num_replications)])
        group_7_of_5x2.arrange(RIGHT, buff=0.3) # Arrange horizontally
        group_7_of_5x2.move_to(ORIGIN + DOWN * 0.5).scale(0.8) # Position and scale

        # Label for the combined group
        brace = Brace(group_7_of_5x2, direction=DOWN, color=text_color)
        group_label = brace.get_tex(f"{num_replications} \\times ({rows2} \\times {cols2})", font_size=36).set_color(text_color)

        # Target arrangement: 7x10 grid (same as Scene 2)
        rows_target, cols_target = 7, 10
        target_grid_pos = ORIGIN + DOWN * 0.5 # Position for rearranged grid
        # Use a distinct color for this target grid
        target_grid_color = MY_ORANGE
        target_squares = VGroup(*[
            # Use MY_BLACK for stroke color directly
            Square(side_length=0.4, color=target_grid_color, fill_color=target_grid_color, fill_opacity=0.7, stroke_width=1, stroke_color=MY_BLACK)
            for _ in range(rows_target * cols_target)
        ]).arrange_in_grid(rows=rows_target, cols=cols_target, buff=0.05).move_to(target_grid_pos).scale(0.9)

        # --- TTS Integration ---
        voice_text_03 = "Next, let's visualize 7 times (5 times 2). We start with a block representing 5 times 2, containing 10 small squares. The expression means we need seven of these blocks. Here they are. Together, these represent 7 times (5 times 2). Now, let's rearrange all these 70 squares into one single rectangle. Notice, we can arrange them into the exact same rectangle as before: 7 rows and 10 columns."
        with custom_voiceover_tts(voice_text_03) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("Warning: Scene 3 TTS audio failed or has zero duration.")

            subtitle_voice = Text(
                voice_text_03, font_size=32, color=text_color,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # Animations
            self.play(FadeIn(subtitle_voice, run_time=0.5))
            # Show the base 5x2 grid first
            self.play(Create(base_grid), Write(base_grid_label), run_time=1.5)
            self.wait(0.5)
            # Replicate the base grid
            self.play(
                LaggedStart(*[FadeIn(g, shift=UP*0.2) for g in group_7_of_5x2], lag_ratio=0.1),
                FadeOut(base_grid, base_grid_label), # Remove the initial base grid
                run_time=2.5
            )
            self.wait(0.5)
            self.play(GrowFromCenter(brace), Write(group_label), run_time=1.5)
            self.wait(1.0) # Pause before rearrangement

            # Rearrangement animation
            all_squares_start = VGroup()
            for g in group_7_of_5x2:
                all_squares_start.add(*g.submobjects)

            target_squares_transform = target_squares.copy()

            self.play(
                FadeOut(brace, group_label), # Fade out labels
                Transform(all_squares_start, target_squares_transform, lag_ratio=0.01, run_time=3.0)
            )
            self.remove(all_squares_start)
            self.add(target_squares) # Add the clean target grid

            # Label the final rearranged grid
            rearranged_label = MathTex("= 7 \\times 10 = 70", font_size=36, color=text_color).next_to(target_squares, DOWN, buff=0.3)
            self.play(Write(rearranged_label), run_time=1.0)

            # Calculate wait time
            anim_time = 0.5 + 1.5 + 0.5 + 2.5 + 0.5 + 1.5 + 1.0 + 3.0 + 1.0 # Animation time
            if tracker.duration > 0:
                remaining_time = tracker.duration - anim_time - 1.0 # Subtract fade out time
                if remaining_time > 0:
                    self.wait(remaining_time)
            else:
                self.wait(1.0) # Wait if no audio

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        # Store results for Scene 4
        self.final_grid_scene3 = target_squares
        self.final_label_scene3 = rearranged_label
        self.viz_label_scene3 = viz_label

    # --- Scene 4: Equivalence Proof ---
    def play_scene_04(self):
        """Scene 4: Show equivalence side-by-side."""
        bg_color = MY_LIGHT_PURPLE
        text_color = MY_BLACK

        # Fade out elements from Scene 3
        self.play(FadeOut(Group(*self.mobjects)))
        self.clear()

        # Background
        bg4 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=bg_color, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg4)

        # Scene Number
        scene_num_04 = self.get_scene_number("04").set_color(text_color)
        self.add(scene_num_04)

        # --- Left Side: (7 x 5) x 2 ---
        left_pos = LEFT * (config.frame_width / 4) + UP * 0.5
        # Recreate the initial visualization for (7x5)x2
        grid1_left = create_grid(7, 5, color=MY_BLUE).scale(0.6)
        grid2_left = create_grid(7, 5, color=MY_RED).scale(0.6)
        group_left = VGroup(grid1_left, grid2_left).arrange(RIGHT, buff=0.3).move_to(left_pos)
        label_left = MathTex("(7 \\times 5) \\times 2", font_size=36, color=text_color).next_to(group_left, UP, buff=0.3)
        calc_left = MathTex("= 35 \\times 2 = 70", font_size=36, color=text_color).next_to(group_left, DOWN, buff=0.3)
        left_group = VGroup(label_left, group_left, calc_left)

        # --- Right Side: 7 x (5 x 2) ---
        right_pos = RIGHT * (config.frame_width / 4) + UP * 0.5
        # Recreate the initial visualization for 7x(5x2)
        base_grid_right = create_grid(5, 2, color=MY_GREEN).scale(0.6)
        group_right = VGroup(*[base_grid_right.copy() for _ in range(7)])
        group_right.arrange(RIGHT, buff=0.15).move_to(right_pos) # Arrange horizontally
        label_right = MathTex("7 \\times (5 \\times 2)", font_size=36, color=text_color).next_to(group_right, UP, buff=0.3)
        calc_right = MathTex("= 7 \\times 10 = 70", font_size=36, color=text_color).next_to(group_right, DOWN, buff=0.3)
        right_group = VGroup(label_right, group_right, calc_right)

        # --- Center: Equals Sign ---
        equals_sign = MathTex("=", font_size=80, color=MY_ORANGE).move_to(UP * 0.5) # Position between the groups

        # --- TTS Integration ---
        voice_text_04 = "So, we saw that the grouping (7 times 5) times 2, which is 35 times 2, equals 70. We also saw that the grouping 7 times (5 times 2), which is 7 times 10, also equals 70. Both ways of grouping lead to the same total number of squares, 70. This visually confirms that (7 times 5) times 2 is equal to 7 times (5 times 2)."
        with custom_voiceover_tts(voice_text_04) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("Warning: Scene 4 TTS audio failed or has zero duration.")

            subtitle_voice = Text(
                voice_text_04, font_size=32, color=text_color,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)

            # Animations
            self.play(FadeIn(subtitle_voice, run_time=0.5))

            # Show left side
            self.play(
                FadeIn(group_left, shift=RIGHT*0.5),
                Write(label_left),
                Write(calc_left),
                run_time=2.0
            )
            self.wait(0.5)
            # Show right side
            self.play(
                FadeIn(group_right, shift=LEFT*0.5),
                Write(label_right),
                Write(calc_right),
                run_time=2.0
            )
            self.wait(0.5)
            # Show equals sign
            self.play(Write(equals_sign), run_time=1.0)

            # Calculate wait time
            anim_time = 0.5 + 2.0 + 0.5 + 2.0 + 0.5 + 1.0 # Animation time
            if tracker.duration > 0:
                remaining_time = tracker.duration - anim_time - 1.0 # Subtract fade out time
                if remaining_time > 0:
                    self.wait(remaining_time)
            else:
                self.wait(1.0) # Wait if no audio

            self.play(FadeOut(subtitle_voice), run_time=1.0)

        self.wait(1)

    # --- Scene 5: Conclusion ---
    def play_scene_05(self):
        """Scene 5: Conclusion and general form."""
        bg_color = MY_DARK_BLUE
        text_color = MY_WHITE

        # Background
        bg5 = Rectangle(width=config.frame_width, height=config.frame_height, fill_color=bg_color, fill_opacity=1.0, stroke_width=0).set_z_index(-10)
        self.add(bg5)

        # Scene Number
        scene_num_05 = self.get_scene_number("05").set_color(text_color)
        self.add(scene_num_05)

        # Conclusion Text
        conclusion_text_part1 = Text("Conclusion: We visually proved the associative property:", font_size=40, color=text_color)
        conclusion_formula = MathTex("(7 \\times 5) \\times 2 = 7 \\times (5 \\times 2)", font_size=48, color=MY_ORANGE)
        conclusion_group = VGroup(conclusion_text_part1, conclusion_formula).arrange(DOWN, buff=0.4)
        conclusion_group.move_to(UP * 2.0)

        # General Form
        general_text = Text("General Form:", font_size=40, color=text_color)
        general_formula = MathTex("(a \\times b) \\times c = a \\times (b \\times c)", font_size=48, color=MY_WHITE)
        general_group = VGroup(general_text, general_formula).arrange(DOWN, buff=0.4)
        general_group.move_to(DOWN * 0.5)

        # Encouragement Text
        encouragement_text = Text("Think: Does this property apply to other operations like addition? 🤔", font_size=36, color=MY_LIGHT_BLUE)
        encouragement_text.to_edge(DOWN, buff=1.0)

        # --- TTS Integration ---
        voice_text_05 = "In conclusion, using these graphical representations, we have demonstrated the associative property of multiplication for this example: (7 times 5) times 2 equals 7 times (5 times 2). This property holds true for any numbers and is written generally as (a times b) times c equals a times (b times c). Can you think if this property applies to other operations like addition or subtraction? Thanks for watching!"
        with custom_voiceover_tts(voice_text_05) as tracker:
            if tracker.audio_path and tracker.duration > 0:
                self.add_sound(tracker.audio_path, time_offset=0)
            else:
                print("Warning: Scene 5 TTS audio failed or has zero duration.")

            subtitle_voice = Text(
                voice_text_05, font_size=32, color=text_color,
                width=config.frame_width - 2, should_center=True
            ).to_edge(DOWN, buff=0.5)
            # Adjust position if overlapping with encouragement text
            subtitle_voice.next_to(encouragement_text, UP, buff=0.3)

            # Animations
            self.play(FadeIn(subtitle_voice, run_time=0.5))

            self.play(FadeIn(conclusion_text_part1, shift=UP*0.2), run_time=1.5)
            self.play(Write(conclusion_formula), run_time=2.0)
            self.wait(1.0)
            self.play(FadeIn(general_text, shift=UP*0.2), run_time=1.5)
            self.play(Write(general_formula), run_time=2.0)
            self.wait(1.0)
            self.play(FadeIn(encouragement_text, shift=UP*0.2), run_time=1.5)

            # Camera zoom out
            self.play(self.camera.frame.animate.scale(1.1), run_time=1.0) # Zoom out slightly

            # Calculate wait time
            anim_time = 0.5 + 1.5 + 2.0 + 1.0 + 1.5 + 2.0 + 1.0 + 1.5 + 1.0 # Animation time
            if tracker.duration > 0:
                remaining_time = tracker.duration - anim_time - 1.0 # Subtract fade out time
                if remaining_time > 0:
                    self.wait(remaining_time)
            else:
                self.wait(1.0) # Wait if no audio

            self.play(FadeOut(subtitle_voice), run_time=1.0)

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
    config.media_dir = r"#(output_path)" # Use raw string for path robustness

    # Set default font for Text objects if found
    if final_font:
        Text.set_default(font=final_font)
        print(f"Using font: {final_font}")
    else:
        print("Using Manim's default font.")


    # Create and render the scene
    scene = CombinedScene()
    scene.render()

    print(f"Scene rendering finished. Output in: {config.media_dir}")