from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    project_name: str = "ClinSight"
    version: str = "0.1.0"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Inference endpoints
    vllm_vision_url: str = "http://localhost:8000/v1"
    vllm_text_url: str = "http://localhost:8001/v1"
    use_mock: bool = True  # Local dev without GPU

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    cache_dir: Path = data_dir / "contingency_cache"
    image_dir: Path = data_dir / "images"

    class Config:
        env_file = ".env"

settings = Settings()
