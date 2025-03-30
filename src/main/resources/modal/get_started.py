import subprocess

import modal

image = (
    # 1) Use an officially supported CUDA image
    modal.Image.from_registry("nvidia/cuda:12.4.0-devel-ubuntu22.04", add_python="3.11")
    # 2) Install cupy, a CUDA replacement for numpy
    .pip_install("cupy-cuda12x")
)

app = modal.App("example-gpu", image=image)


# 3) Attach a GPU to your function
@app.function(gpu="A10G")
def square(x=2):
    import cupy as cp

    subprocess.run(["nvidia-smi"])
    print(f"The square of {x} is {cp.square(x)}")
