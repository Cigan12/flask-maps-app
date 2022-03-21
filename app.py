from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError



app = Flask(__name__)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maps.db'
app.config['SECRET_KEY'] = 'some secret'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"

@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id))


# MODELS
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Feedback(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(80), nullable=False)
    userid = db.Column(db.Integer, primary_key=False)

# FORMS
class SignUpForm(FlaskForm): 
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Имя"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Пароль"})
    submit = SubmitField("Зарегистрироваться")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("Имя уже занято")


class SignInForm(FlaskForm): 
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Имя"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Пароль"})
    submit = SubmitField("Войти")

class FeedBackForm(FlaskForm):
    theme = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Тема"})
    content = TextAreaField(validators=[InputRequired(), Length(min=4, max=200)], render_kw={"placeholder": "Сообщение"})
    submit = SubmitField("Отправить")


@app.route("/")
def home():
    return render_template("pages/home.html")

@app.route("/about")
def about():
    return render_template("pages/about.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
    return render_template("pages/signin.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('signin'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signin'))

    return render_template("pages/signup.html", form=form)

@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    form = FeedBackForm()
    if form.validate_on_submit():
        new_feedback = Feedback(theme=form.theme.data, content=form.content.data, userid=current_user.id)
        db.session.add(new_feedback)
        db.session.commit()
        return render_template("pages/feedback.html", form=form, sended=True)
    return render_template("pages/feedback.html", form=form, sended=False)

if __name__ == '__main__':
    app.run(debug=True)

