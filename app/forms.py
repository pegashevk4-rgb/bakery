from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class RegisterForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField(
        "Пароль", validators=[DataRequired(), Length(min=6, max=128)]
    )
    password_confirm = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password", message="Пароли не совпадают")],
    )


class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])


class CheckoutForm(FlaskForm):
    contact_name = StringField("Имя", validators=[DataRequired(), Length(min=2, max=120)])
    contact_phone = StringField(
        "Телефон", validators=[DataRequired(), Length(min=5, max=40)]
    )
    contact_email = StringField("E-mail", validators=[DataRequired(), Email()])

    delivery_type = SelectField(
        "Способ получения",
        choices=[("pickup", "Самовывоз"), ("delivery", "Доставка")],
        default="pickup",
    )
    address = TextAreaField("Адрес доставки", validators=[Optional(), Length(max=400)])

    payment_method = SelectField(
        "Способ оплаты",
        choices=[
            ("cash", "Наличными при получении"),
            ("card", "Картой при получении"),
            ("online", "Онлайн-оплата (демо)"),
        ],
        default="cash",
    )

    def validate(self, extra_validators=None):
        """Адрес обязателен, если выбрана доставка (кастомная серверная валидация)."""
        is_valid = super().validate(extra_validators=extra_validators)
        if self.delivery_type.data == "delivery" and not (self.address.data or "").strip():
            self.address.errors.append("Укажите адрес доставки")
            is_valid = False
        return is_valid
