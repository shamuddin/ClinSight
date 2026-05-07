import sys
sys.path.insert(0, "/opt/clinsight")

# Write the correct config
config_content = '''from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    project_name: str = "ClinSight"
    version: str = "0.1.0"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8002
    vllm_vision_url: str = "http://localhost:8000/v1"
    vllm_text_url: str = "http://localhost:8001/v1"
    use_mock: bool = False
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    cache_dir: Path = data_dir / "contingency_cache"
    image_dir: Path = data_dir / "images"
    class Config:
        env_file = ".env"

settings = Settings()
'''

with open('/opt/clinsight/backend/core/config.py', 'w') as f:
    f.write(config_content)

print('config_written')

# Verify
from backend.core.config import settings
print(f"mock={settings.use_mock} vision={settings.vllm_vision_url} text={settings.vllm_text_url}")
