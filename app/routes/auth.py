from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user, current_user

from app.extensions import db
from app.forms import LoginForm, RegisterForm
from app.models import CartItem, Order, User

auth_bp = Blueprint("auth", __name__)


def merge_guest_cart_into_user(user: User) -> None:
    """
    При входе/регистрации переносим товары, добавленные в корзину как
    гость (по session_id), на аккаунт пользователя (user_id). Если товар
    уже есть в корзине аккаунта — количества складываются.
    """
    guest_session_id = session.get("session_id")
    if not guest_session_id:
        return

    guest_items = CartItem.query.filter_by(session_id=guest_session_id).all()
    for guest_item in guest_items:
        existing = CartItem.query.filter_by(
            user_id=user.id, product_id=guest_item.product_id
        ).first()
        if existing:
            existing.quantity += guest_item.quantity
            db.session.delete(guest_item)
        else:
            guest_item.session_id = None
            guest_item.user_id = user.id
    db.session.commit()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким e-mail уже зарегистрирован.", "error")
        else:
            user = User(name=form.name.data.strip(), email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            merge_guest_cart_into_user(user)
            login_user(user)
            flash("Регистрация успешна! Добро пожаловать.", "success")
            return redirect(url_for("main.index"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(form.password.data):
            flash("Неверный e-mail или пароль.", "error")
        else:
            merge_guest_cart_into_user(user)
            login_user(user)
            flash(f"С возвращением, {user.name}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.index"))

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    orders = current_user.orders.order_by(Order.created_at.desc()).all()
    return render_template("profile.html", orders=orders)
