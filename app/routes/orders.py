from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import CheckoutForm
from app.models import Order, OrderItem
from app.routes.cart import cart_summary, get_cart_items

orders_bp = Blueprint("orders", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@orders_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, total, count = cart_summary()
    if not items:
        flash("Ваша корзина пуста — добавьте что-нибудь вкусное перед оформлением заказа.", "info")
        return redirect(url_for("main.index"))

    form = CheckoutForm()
    if current_user.is_authenticated and not form.is_submitted():
        form.contact_name.data = current_user.name
        form.contact_email.data = current_user.email

    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            contact_name=form.contact_name.data.strip(),
            contact_phone=form.contact_phone.data.strip(),
            contact_email=form.contact_email.data.strip().lower(),
            delivery_type=form.delivery_type.data,
            address=(form.address.data or "").strip() or None,
            payment_method=form.payment_method.data,
            total=total,
        )
        db.session.add(order)
        db.session.flush()  # получаем order.id до коммита

        for item in items:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                )
            )
            db.session.delete(item)

        db.session.commit()
        return redirect(url_for("orders.order_success", order_id=order.id))

    return render_template("checkout.html", form=form, items=items, total=total)


@orders_bp.route("/order/<int:order_id>/success")
def order_success(order_id):
    order = db.get_or_404(Order, order_id)
    # Владелец заказа (если он авторизован) или гость с тем же e-mail в этой
    # сессии могут увидеть чек; чужие авторизованные пользователи — нет.
    if order.user_id and (
        not current_user.is_authenticated or current_user.id != order.user_id
    ):
        abort(404)
    return render_template("order_success.html", order=order)


@orders_bp.route("/admin/orders")
@login_required
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin_orders.html", orders=orders)
