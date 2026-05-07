import sys
sys.path.insert(0, "/opt/clinsight")
from backend.core.config import settings
print(f"use_mock={settings.use_mock}")
print(f"vision_url={settings.vllm_vision_url}")
print(f"text_url={settings.vllm_text_url}")
