import sys
path = sys.argv[1]
text = open(path).read()

# Add judge import after demo import
text = text.replace(
    "from backend.api.demo import router as demo_router",
    "from backend.api.demo import router as demo_router\nfrom backend.api.judge import router as judge_router"
)

# Add judge router after demo router
text = text.replace(
    "app.include_router(demo_router)",
    "app.include_router(demo_router)\napp.include_router(judge_router)"
)

open(path, "w").write(text)
print("JUDGE_ROUTER_ADDED")
