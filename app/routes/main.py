from flask import Blueprint, render_template, request

from app.models import Product

main_bp = Blueprint("main", __name__)

CATEGORY_ORDER = ["Хлеб", "Булочки", "Круассаны", "Выпечка", "Напитки"]


@main_bp.route("/")
def index():
    # Фильтрация также дублируется на клиенте (см. static/js/main.js) для
    # мгновенного отклика без перезагрузки страницы, но сервер тоже умеет
    # отфильтровать каталог по ссылке вида /?category=Напитки&max_price=3 —
    # это работает и без JS, и как самостоятельный вход для шаринга ссылки.
    category = request.args.get("category", "").strip()
    max_price = request.args.get("max_price", "").strip()

    query = Product.query.filter_by(is_available=True)
    if category and category in CATEGORY_ORDER:
        query = query.filter_by(category=category)
    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            max_price = ""

    products = query.order_by(Product.category, Product.name).all()

    categories = CATEGORY_ORDER
    return render_template(
        "index.html",
        products=products,
        categories=categories,
        active_category=category,
        active_max_price=max_price,
    )
