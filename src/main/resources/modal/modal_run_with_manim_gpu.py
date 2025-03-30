import modal

image = (
  modal.Image.from_registry("nvidia/cuda:12.4.0-devel-ubuntu22.04", add_python="3.11")
  .run_commands("echo 'tzdata tzdata/Areas select Asia' | debconf-set-selections")
  .run_commands("echo 'tzdata tzdata/Zones/Asia select Shanghai' | debconf-set-selections")
  .env({"DEBIAN_FRONTEND": "noninteractive"})
  .apt_install("tzdata", "build-essential", "python3-dev", "tzdata", "texlive-full", "ffmpeg", "pkg-config",
               "libcairo2-dev", "libpango1.0-dev")

  .pip_install("numpy", "manim", "manimpango", "latex", "moviepy", "requests")
  .add_local_dir("scripts", "/scripts")
  .run_commands("ffmpeg -encoders | grep nven")
)

app = modal.App("example-run-local-script", image=image)


@app.function(gpu="A10G")
def run_script():
  with open("/scripts/manim_a_plus_b.py", "r", encoding="utf-8") as f:
    script_content = f.read()
    print(script_content)
    exec(script_content, {'__name__': '__main__'})
  print("exec finished")
