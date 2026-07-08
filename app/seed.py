from app.extensions import db
from app.models import Product, User

PRODUCTS = [
    # Хлеб
    dict(
        name="Бородинский",
        description="Тёмный ржаной хлеб на закваске с кориандром",
        price=3.20,
        category="Хлеб",
        emoji="🍞",
        image_filename="borodinsky.jpg",
    ),
    dict(
        name="Багет французский",
        description="Хрустящая корочка, воздушный мякиш",
        price=2.80,
        category="Хлеб",
        emoji="🥖",
        image_filename="baguette-french.jpg",
    ),
    dict(
        name="Чиабатта",
        description="Итальянский хлеб с оливковым маслом",
        price=3.50,
        category="Хлеб",
        emoji="🍞",
        image_filename="ciabatta.jpg",
    ),

    # Булочки
    dict(
        name="Булочка с корицей",
        description="Классическая синнабон с кремовой глазурью",
        price=2.90,
        category="Булочки",
        emoji="🥐",
        image_filename="cinnamon-roll.jpg",
    ),
    dict(
        name="Булочка с маком",
        description="Сдобная булочка с маковой начинкой",
        price=2.10,
        category="Булочки",
        emoji="🥯",
        image_filename="poppy-roll.jpg",
    ),
    dict(
        name="Плетёнка с изюмом",
        description="Сдобное плетёное тесто с изюмом",
        price=2.60,
        category="Булочки",
        emoji="🥐",
        image_filename="braided-raisin.jpg",
    ),

    # Круассаны
    dict(
        name="Круассан классический",
        description="Слоёное масляное тесто, выпечка по французской технологии",
        price=2.70,
        category="Круассаны",
        emoji="🥐",
        image_filename="croissant-classic.jpg",
    ),
    dict(
        name="Круассан с миндалём",
        description="Круассан с миндальным кремом и лепестками",
        price=3.40,
        category="Круассаны",
        emoji="🥐",
        image_filename="croissant-almond.jpg",
    ),
    dict(
        name="Круассан с шоколадом",
        description="Пан-о-шоколя с двумя палочками тёмного шоколада",
        price=3.10,
        category="Круассаны",
        emoji="🍫",
        image_filename="croissant-choco.jpg",
    ),

    # Выпечка
    dict(
        name="Чизкейк Нью-Йорк",
        description="Классический сливочный чизкейк на песочной основе",
        price=4.50,
        category="Выпечка",
        emoji="🍰",
        image_filename="cheesecake-ny.jpg",
    ),
    dict(
        name="Эклер с кремом",
        description="Заварное тесто с ванильным кремом и шоколадной глазурью",
        price=2.80,
        category="Выпечка",
        emoji="🧁",
        image_filename="eclair-vanilla.jpg",
    ),
    dict(
        name="Тарт с ягодами",
        description="Песочный тарт с кремом-патисьер и сезонными ягодами",
        price=4.20,
        category="Выпечка",
        emoji="🥧",
        image_filename="berry-tart.jpg",
    ),

    # Напитки
    dict(
        name="Эспрессо",
        description="Классический двойной эспрессо из свежемолотых зёрен",
        price=1.80,
        category="Напитки",
        emoji="☕",
        image_filename="espresso.jpg",
    ),
    dict(
        name="Капучино",
        description="Эспрессо с молочной пенкой",
        price=2.40,
        category="Напитки",
        emoji="☕",
        image_filename="cappuccino.jpg",
    ),
    dict(
        name="Какао домашнее",
        description="Горячий шоколадный напиток со взбитыми сливками",
        price=2.60,
        category="Напитки",
        emoji="🍫",
        image_filename="cocoa-homemade.jpg",
    ),
]


def seed_if_empty(app):
    # товары
    if Product.query.first() is None:
        for data in PRODUCTS:
            db.session.add(Product(**data))
        db.session.commit()
        app.logger.info(
            "Каталог товаров заполнен тестовыми данными (%d шт.)",
            len(PRODUCTS),
        )

    # админ
    admin_email = app.config["ADMIN_EMAIL"]
    if User.query.filter_by(email=admin_email).first() is None:
        admin = User(
            name="Администратор",
            email=admin_email,
            is_admin=True,
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        app.logger.info("Создан администратор: %s", admin_email)