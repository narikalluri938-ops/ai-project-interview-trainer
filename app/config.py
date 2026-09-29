import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-12345")
    
    # Database
    db_file = INSTANCE_DIR / "interview_trainer.db"
    default_db_uri = f"sqlite:///{db_file.as_posix()}"
    raw_db_url = os.getenv("DATABASE_URL", default_db_uri).strip()
    
    # Handle cloud providers (Render, Heroku) that supply 'postgres://' instead of 'postgresql://'
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    elif raw_db_url.startswith("sqlite:///instance/"):
        raw_db_url = default_db_uri

    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Provider settings
    AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").lower()
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max request payload
    PROPAGATE_EXCEPTIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    AI_PROVIDER = "mock"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # In production, require SECRET_KEY from environment; fallback to dynamic token if missing
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_hex(32)

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
