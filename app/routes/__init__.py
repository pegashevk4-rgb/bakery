import os
from flask import Flask
from app.extensions import db 

def create_app():
    app = Flask(__name__)

    # базовые настройки, чтобы не было KeyError на DEBUG
    app.config.setdefault("DEBUG", False)

    # БД из переменной окружения (в Vercel настрой Environment Variable DATABASE_URL)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        # если хочешь временно без внешней БД — можно так, но это будет неpersistent:
        # "sqlite:////tmp/bakery.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    return app