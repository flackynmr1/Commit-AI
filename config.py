import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-key-change-in-production"

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "sqlite:///" + str(BASE_DIR / "app.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    STRIPE_STARTER_PRICE_ID = os.environ.get("STRIPE_STARTER_PRICE_ID", "")
    STRIPE_GROWTH_PRICE_ID = os.environ.get("STRIPE_GROWTH_PRICE_ID", "")
    STRIPE_AGENCY_PRICE_ID = os.environ.get("STRIPE_AGENCY_PRICE_ID", "")

    FRONTEND_URL = os.environ.get(
        "FRONTEND_URL",
        "http://localhost:5050"
    )

    JWT_SECRET_KEY = (
        os.environ.get("JWT_SECRET_KEY")
        or "jwt-secret-string"
    )

    JWT_ACCESS_TOKEN_EXPIRES = 3600

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
# JARVIS / Video Agent

AUDIO_DIR = "audio"

VOICE = "sv-SE-MattiasNeural"