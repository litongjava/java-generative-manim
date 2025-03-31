import subprocess

import modal

image = (
  modal.Image.from_registry("nvidia/cuda:12.2.0-devel-ubuntu22.04", add_python="3.10")
  .env({"DEBIAN_FRONTEND": "noninteractive", "TZ": "Asia/Shanghai"})
  .apt_install("tzdata")
  .run_commands("ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' > /etc/timezone")
  .apt_install("build-essential", "ffmpeg", "ghostscript", "dvisvgm", "texlive-full")
  .apt_install("python3-dev", "pkg-config")
  .apt_install("libcairo2-dev", "libpango1.0-dev", "clang")
  .run_commands("pip install --upgrade pip setuptools wheel")
  .pip_install("numpy", "manim", "latex", "moviepy", "requests")
  .pip_install("manimpango")
  .add_local_dir("scripts", "/scripts")
)

app = modal.App("example-run-local-script", image=image)


@app.function(gpu="A10G")
def run_script():
  with open("/scripts/fx_xx.py", "r", encoding="utf-8") as f:
    script_content = f.read()
    print(script_content)
    exec(script_content, {'__name__': '__main__'})
  print("exec finished")
