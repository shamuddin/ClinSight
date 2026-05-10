import os
os.environ["HF_HOME"] = "/shared-docker/hf_cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/shared-docker/hf_cache"

from huggingface_hub import snapshot_download

print("Downloading Qwen2.5-VL-7B-Instruct...")
snapshot_download(repo_id="Qwen/Qwen2.5-VL-7B-Instruct", local_files_only=False)
print("Vision model downloaded.")

print("Downloading Qwen3.5-35B-A3B...")
snapshot_download(repo_id="Qwen/Qwen3.5-35B-A3B", local_files_only=False)
print("Text model downloaded.")
