import sys, traceback
sys.path.insert(0, "/opt/clinsight")
try:
    from backend.agents.graph import run_pipeline
    print("import_ok")
except Exception as e:
    print(f"import_fail: {e}")
    traceback.print_exc()
