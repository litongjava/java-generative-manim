import modal

# 1) Create a Modal App
app = modal.App("example-get-started")


# 2) Add this decorator to run in the cloud
@app.function()
def square(x=2):
    print(f"The square of {x} is {x**2}")  # This runs on a remote worker!