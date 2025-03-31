import modal

# 构建镜像：
# - apt_install 安装 TeX Live、FFmpeg、pkg-config、cairo 开发包以及 pango 开发包
# - pip_install 安装 Python 包（numpy、manim、manimpango、latex、moviepy、requests）
# - add_local_dir 将本地 "scripts" 目录挂载到容器的 /scripts 目录
image = (
  modal.Image.debian_slim()
  .apt_install("texlive-full", "ffmpeg", "pkg-config", "libcairo2-dev", "libpango1.0-dev")
  .pip_install("numpy", "manim", "manimpango", "latex", "moviepy", "requests")
  .add_local_dir("scripts", "/scripts")
)

app = modal.App("example-run-local-script", image=image)


@app.function()
def run_script():
  with open("/scripts/fx_xx_cario.py", "r", encoding="utf-8") as f:
    script_content = f.read()
    print(script_content)
    exec(script_content, {'__name__': '__main__'})

  print("exec finished")
