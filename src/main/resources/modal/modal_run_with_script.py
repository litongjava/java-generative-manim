import modal

# 创建镜像，并将本地 "scripts" 目录挂载到容器中的 /scripts 目录
image = modal.Image.debian_slim().pip_install("numpy").add_local_dir("scripts", "/scripts")

# 创建 Modal 应用，并指定使用更新后的镜像
app = modal.App("example-run-local-script", image=image)

@app.function()
def run_script():
    # 例如读取并执行 /scripts/numpy_square.py 脚本
    with open("/scripts/numpy_square.py", "r", encoding="utf-8") as f:
        script_content = f.read()
    exec(script_content)
