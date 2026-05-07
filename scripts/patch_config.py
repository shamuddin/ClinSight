# Patching /opt/clinsight/backend/core/config.py to use single server
from pathlib import Path

text = '''from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    project_name: str = "ClinSight"
    version: str = "0.1.0"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8002
    vllm_vision_url: str = "http://127.0.0.1:8000/v1"
    vllm_text_url: str = "http://127.0.0.1:8000/v1"
    use_mock: bool = False
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    cache_dir: Path = data_dir / "contingency_cache"
    image_dir: Path = data_dir / "images"
    class Config:
        env_file = ".env"
'''

p = Path("/opt/clinsight/backend/core/config.py")
p.write_text(text)
print("patched")
