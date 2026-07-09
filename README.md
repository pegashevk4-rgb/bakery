# 🥖 Пекарь&Ки — демо интернет-булочная

Учебный full-stack проект: витрина с фильтрами → корзина → регистрация/вход →
оформление заказа → личный кабинет → простая админка со списком заказов.

**Стек:** Flask + SQLAlchemy + Flask-Login + Flask-WTF, SQLite, чистый HTML/CSS/JS.

## Быстрый старт

```bash
cd bakery
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # затем при желании подправьте значения

python run.py
```

Откройте **http://localhost:5000** — каталог, БД (`bakery.db`) и админ-аккаунт
создаются автоматически при первом запуске.

**Тестовый администратор** (см. `.env` → `ADMIN_EMAIL` / `ADMIN_PASSWORD`):
- e-mail: `admin@bakery-demo.com`
- пароль: `admin12345`
- Панель: `/admin/orders` (доступна только после входа под этим аккаунтом)

## Структура проекта

```
bakery/
├── app/
│   ├── __init__.py         # фабрика приложения, регистрация блюпринтов
│   ├── extensions.py       # db, login_manager
│   ├── models.py           # User, Product, CartItem, Order, OrderItem
│   ├── forms.py            # WTForms: регистрация, вход, оформление заказа
│   ├── seed.py             # наполнение каталога и создание админа
│   ├── routes/
│   │   ├── main.py         # витрина + серверная фильтрация
│   │   ├── auth.py         # регистрация / вход / выход / перенос гостевой корзины
│   │   ├── cart.py         # JSON API корзины (add / update / remove)
│   │   └── orders.py       # оформление заказа, чек, админ-список заказов
│   ├── templates/
│   │   ├── base.html, index.html, cart.html, _cart_items.html
│   │   ├── checkout.html, order_success.html
│   │   ├── login.html, register.html, profile.html, admin_orders.html
│   └── static/
│       ├── css/style.css
│       └── js/main.js, cart.js
├── config.py
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

## Как это работает (короткий дизайн-план)

- **Корзина.** У каждого гостя есть `session_id` (создаётся в `before_request`).
  Позиции корзины хранятся в таблице `cart_items` с привязкой либо к
  `user_id`, либо к `session_id`. При входе/регистрации гостевая корзина
  переносится на аккаунт (`merge_guest_cart_into_user`), поэтому у
  зарегистрированных пользователей корзина не теряется между визитами.
- **Фильтры на витрине** работают на клиенте (мгновенно, без перезагрузки) —
  JS читает `data-category`/`data-price` у карточек. Тот же фильтр умеет
  работать и на сервере через `?category=...&max_price=...` — рабочая ссылка
  даже без JS.
- **Оформление заказа**: серверная валидация через Flask-WTF (email,
  длина полей, обязательный адрес при доставке), плюс CSRF-защита на всех
  формах и JSON-запросах (токен передаётся в заголовке `X-CSRFToken`).
- **Заказ** сохраняет снимок товаров (`OrderItem.product_name/price`) —
  изменение цены в каталоге в будущем не искажает историю старых заказов.
- **Админка** — один защищённый роут `/admin/orders` со списком всех заказов
  (`is_admin`-флаг у пользователя), без отдельной CRUD-панели, как и просили
  в задаче.

## Переменные окружения (`.env`)

| Переменная | Назначение | Пример |
|---|---|---|
| `SECRET_KEY` | ключ сессий/CSRF | сгенерировать: `python -c "import secrets;print(secrets.token_hex(32))"` |
| `DATABASE_URL` | строка подключения к БД | `sqlite:///bakery.db` или `postgresql://user:pass@host:5432/db` |
| `FLASK_DEBUG` | режим отладки | `True` локально, `False` в проде |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | учётка админа, создаваемая при первом запуске | — |

## Переход на PostgreSQL

Проект уже использует SQLAlchemy, поэтому переезд — это просто смена
`DATABASE_URL` и установка драйвера:

```bash
pip install psycopg2-binary
# .env
DATABASE_URL=postgresql://user:password@host:5432/bakery
```

Таблицы создаются автоматически при старте (`db.create_all()`); для
продакшена лучше подключить Flask-Migrate/Alembic, если планируете менять
схему после запуска.

## Деплой (Render / Railway / VPS)

**Render / Railway (проще всего):**
1. Запушьте проект в GitHub-репозиторий.
2. Создайте новый Web Service, укажите:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn run:app`
3. Добавьте переменные окружения из `.env` (обязательно свой `SECRET_KEY`,
   `FLASK_DEBUG=False`).
4. Подключите managed PostgreSQL (Render/Railway дают его в один клик) и
   пропишите выданный `DATABASE_URL`.
5. Добавьте `gunicorn` в `requirements.txt` (`pip install gunicorn` локально,
   затем `pip freeze | grep gunicorn >> requirements.txt`).

**VPS (Ubuntu + nginx + gunicorn, вручную):**
1. `git clone`, создать venv, `pip install -r requirements.txt gunicorn`.
2. Запустить как systemd-сервис: `gunicorn -w 3 -b 127.0.0.1:8000 run:app`.
3. nginx как reverse proxy на `127.0.0.1:8000` + сертификат через
   `certbot` (Let's Encrypt) для HTTPS.
4. `.env` с продовым `SECRET_KEY`, `FLASK_DEBUG=False`, реальным
   `DATABASE_URL` (Postgres), правами на файл `0600`.

**Что доработать перед продом:**
- HTTPS обязателен (cookies сессии/CSRF рассчитаны на защищённое соединение —
  можно дополнительно включить `SESSION_COOKIE_SECURE=True` в `config.py`).
- Секреты — только через переменные окружения, не в репозитории.
- SQLite подходит для демо, но для реальной нагрузки — Postgres (см. выше).
- Логирование/мониторинг ошибок (например, Sentry).
- Реальная оплата (Stripe/PayPal) вместо демо-выбора способа оплаты.
- Rate limiting на `/auth/login` и `/auth/register` (например, Flask-Limiter)
  для защиты от брутфорса.
