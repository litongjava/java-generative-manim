# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from contextlib import contextmanager
from manim import *
from moviepy import AudioFileClip
import hashlib

CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


class CustomVoiceoverTracker:
    def __init__(self, audio_path, duration):
        self.audio_path = audio_path
        self.duration = duration


def get_cache_filename(text):
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{text_hash}.mp3")


@contextmanager
def custom_voiceover_tts(text, token="123456", base_url="https://uni-ai.fly.dev/api/manim/tts"):
    cache_file = get_cache_filename(text)

    if os.path.exists(cache_file):
        audio_file = cache_file
    else:
        input_text = requests.utils.quote(text)
        url = f"{base_url}?token={token}&input={input_text}"

        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"TTS 接口错误: {response.status_code} - {response.text}")

        with open(cache_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        audio_file = cache_file

    clip = AudioFileClip(audio_file)
    duration = clip.duration
    clip.close()

    tracker = CustomVoiceoverTracker(audio_file, duration)
    try:
        yield tracker
    finally:
        pass  # 根据需要决定是否清理缓存