from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

class SignInForm(FlaskForm): 
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Имя"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Пароль"})
    submit = SubmitField("Зарегистрироваться")

