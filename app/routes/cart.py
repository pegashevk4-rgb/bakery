from flask import Blueprint, jsonify, render_template, request, session
from flask_login import current_user

from app.extensions import db
from app.models import CartItem, Product

cart_bp = Blueprint("cart", __name__)


def _owner_filter():
    """
    Возвращает словарь-фильтр для CartItem: по user_id для авторизованных
    пользователей, иначе по session_id гостя.
    """
    if current_user.is_authenticated:
        return {"user_id": current_user.id}
    return {"session_id": session["session_id"]}


def get_cart_items():
    return (
        CartItem.query.filter_by(**_owner_filter())
        .join(Product)
        .order_by(CartItem.id)
        .all()
    )


def cart_summary():
    items = get_cart_items()
    total = round(sum(item.subtotal for item in items), 2)
    count = sum(item.quantity for item in items)
    return items, total, count


def _serialize_items(items):
    return [
        {
            "product_id": item.product_id,
            "name": item.product.name,
            "emoji": item.product.emoji,
            "price": float(item.product.price),
            "quantity": item.quantity,
            "subtotal": item.subtotal,
        }
        for item in items
    ]


@cart_bp.route("/", methods=["GET"])
def view_cart():
    items, total, count = cart_summary()
    return render_template("cart.html", items=items, total=total, count=count)


@cart_bp.route("/api", methods=["GET"])
def api_cart_state():
    items, total, count = cart_summary()
    return jsonify({"items": _serialize_items(items), "total": total, "count": count})


@cart_bp.route("/api/add", methods=["POST"])
def api_add():
    data = request.get_json(silent=True) or request.form
    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Некорректные данные"}), 400

    quantity = max(1, quantity)
    product = Product.query.filter_by(id=product_id, is_available=True).first()
    if product is None:
        return jsonify({"error": "Товар не найден"}), 404

    owner = _owner_filter()
    item = CartItem.query.filter_by(product_id=product_id, **owner).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(product_id=product_id, quantity=quantity, **owner)
        db.session.add(item)
    db.session.commit()

    items, total, count = cart_summary()
    return jsonify({"items": _serialize_items(items), "total": total, "count": count})


@cart_bp.route("/api/update", methods=["POST"])
def api_update():
    data = request.get_json(silent=True) or request.form
    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity"))
    except (TypeError, ValueError):
        return jsonify({"error": "Некорректные данные"}), 400

    owner = _owner_filter()
    item = CartItem.query.filter_by(product_id=product_id, **owner).first()
    if item is None:
        return jsonify({"error": "Товар не найден в корзине"}), 404

    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = min(quantity, 99)
    db.session.commit()

    items, total, count = cart_summary()
    return jsonify({"items": _serialize_items(items), "total": total, "count": count})


@cart_bp.route("/api/remove", methods=["POST"])
def api_remove():
    data = request.get_json(silent=True) or request.form
    try:
        product_id = int(data.get("product_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Некорректные данные"}), 400

    owner = _owner_filter()
    item = CartItem.query.filter_by(product_id=product_id, **owner).first()
    if item:
        db.session.delete(item)
        db.session.commit()

    items, total, count = cart_summary()
    return jsonify({"items": _serialize_items(items), "total": total, "count": count})
