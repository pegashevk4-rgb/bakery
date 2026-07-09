import os
import uuid

from flask import Flask, session
from flask_wtf import CSRFProtect

from app.extensions import db, login_manager

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)

    # БЕЗ Config, чтобы ничего не подтягивало старые настройки БД.
    # Если нужны другие параметры из Config (SECRET_KEY и т.п.), их можно задать вручную.

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    # КРИТИЧЕСКОЕ МЕСТО: чистый in-memory SQLite, без файловой системы.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
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