from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship("Order", backref="user", lazy="dynamic")
    cart_items = db.relationship(
        "CartItem", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(400), nullable=False, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(60), nullable=False, index=True)
    emoji = db.Column(db.String(8), nullable=False, default="🥐")
    is_available = db.Column(db.Boolean, default=True, nullable=False)

    image_filename = db.Column(db.String(200), nullable=True)  # ← добавляем

    def __repr__(self) -> str:
        return f"<Product {self.name}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "category": self.category,
            "emoji": self.emoji,
            "image_filename": self.image_filename,  # ← тоже сюда
        }



class CartItem(db.Model):
    """
    Позиция корзины. Принадлежит либо авторизованному пользователю (user_id),
    либо гостевой сессии (session_id) — ровно одному из двух.
    Когда гость авторизуется, его гостевая корзина переносится на аккаунт
    (см. merge_guest_cart_into_user в app/routes/auth.py), поэтому у
    авторизованных пользователей корзина не пропадает между заходами.
    """

    __tablename__ = "cart_items"
    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
        db.UniqueConstraint(
            "session_id", "product_id", name="uq_cart_session_product"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    session_id = db.Column(db.String(64), nullable=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product")

    @property
    def subtotal(self):
        return round(float(self.product.price) * self.quantity, 2)


class Order(db.Model):
    __tablename__ = "orders"

    STATUS_NEW = "new"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    contact_name = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(40), nullable=False)
    contact_email = db.Column(db.String(255), nullable=False)

    delivery_type = db.Column(db.String(20), nullable=False, default="pickup")
    address = db.Column(db.String(400), nullable=True)
    payment_method = db.Column(db.String(30), nullable=False, default="cash")

    status = db.Column(db.String(20), nullable=False, default=STATUS_NEW)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        "OrderItem", backref="order", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order #{self.id}>"


class OrderItem(db.Model):
    """
    Снимок товара на момент покупки: имя и цена сохраняются отдельно от
    Product, чтобы будущее изменение цены/названия товара не искажало
    историю уже оформленных заказов.
    """

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_name = db.Column(db.String(150), nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    @property
    def subtotal(self):
        return round(float(self.product_price) * self.quantity, 2)

