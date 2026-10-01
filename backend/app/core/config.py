from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Leukemia Detection Platform"
    secret_key: str = "dev-change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'leukemia.db').as_posix()}"
    upload_dir: Path = BACKEND_DIR / "uploads"
    model_dir: Path = ROOT_DIR / "ml" / "saved_models"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    seed_demo_users: bool = True


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.model_dir.mkdir(parents=True, exist_ok=True)
