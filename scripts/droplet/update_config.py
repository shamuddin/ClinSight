import re

with open('/shared-docker/backend/core/config.py', 'r') as f:
    content = f.read()

content = content.replace(
    'vllm_text_url: str = "http://localhost:8001/v1"',
    'vllm_text_url: str = "http://localhost:30000/v1"'
)

with open('/shared-docker/backend/core/config.py', 'w') as f:
    f.write(content)

print("Config updated.")
