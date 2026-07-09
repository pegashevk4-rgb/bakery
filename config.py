import os
from datetime import timedelta

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///:memory:"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = _bool_env("FLASK_DEBUG", False)

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@bakery-demo.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin12345")

    # Сессия куки живёт 30 дней, чтобы гостевая корзина не терялась слишком быстро
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    WTF_CSRF_TIME_LIMIT = None
