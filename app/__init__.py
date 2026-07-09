import os
import uuid

from flask import Flask, session
from flask_wtf import CSRFProtect

from app.extensions import db, login_manager

csrf = CSRFProtect()

# На Vercel файловая система /var/task доступна только на чтение,
# поэтому sqlite с файловым бэкендом там работать не будет.
IS_VERCEL = os.environ.get("VERCEL") == "1" or os.path.isdir("/var/task")


def _resolve_database_uri(raw_uri: str) -> str:
    """Приводим URI БД к безопасному виду.

    - На Vercel любой относительный sqlite-путь заменяется на in-memory.
    - Локально относительные sqlite-пути резолвятся в абсолютные,
      чтобы SQLAlchemy не создавала каталог instance/.
    """
    if not raw_uri.startswith("sqlite:///"):
        return raw_uri  # PostgreSQL и прочие — как есть

    path = raw_uri[len("sqlite:///"):]

    # Абсолтный путь (Windows: C:\... или Unix: /...) — уже готов
    if os.path.isabs(path):
        return raw_uri

    # Относительный путь — на Vercel нельзя писать на диск
    if IS_VERCEL:
        return "sqlite:///:memory:"

    # Локально — резолвим относительно корня проекта, а не CWD
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return "sqlite:///" + os.path.join(project_root, path)


def create_app():
    app = Flask(__name__)

    # Базовые настройки напрямую из окружения
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = _resolve_database_uri(
        os.environ.get("DATABASE_URL", "sqlite:///:memory:")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["ADMIN_EMAIL"] = os.environ.get("ADMIN_EMAIL", "admin@bakery-demo.com")
    app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "admin12345")
    app.config.setdefault("DEBUG", False)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    @app.before_request
    def ensure_guest_session_id():
        session.permanent = True
        if "session_id" not in session:
            session["session_id"] = uuid.uuid4().hex

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.cart import cart_bp
    from app.routes.orders import orders_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp)

    @app.context_processor
    def inject_cart_count():
        from app.routes.cart import get_cart_items

        items = get_cart_items()
        count = sum(item.quantity for item in items)
        return {"cart_count": count}

    with app.app_context():
        db.create_all()
        from app.seed import seed_if_empty

        seed_if_empty(app)

    return app