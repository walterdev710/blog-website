from flask import Flask, render_template,request, redirect, url_for, flash, abort
from forms import RegisterForm, LoginForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from functools import wraps
from dotenv import load_dotenv
import os
import requests
import datetime
import smtplib

load_dotenv()

API_URL = "https://api.npoint.io/c790b4d5cab58020d391"
all_blogs = requests.get(API_URL).json()
MY_EMAIL = "walterdev710@outlook.com"
MY_PASS = os.getenv("MY_PASSWORD")

today = datetime.datetime.now()
formatted_now = today.strftime("on %B %d, %Y")

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

Bootstrap(app)
db = SQLAlchemy(app=app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id:Mapped[int] = mapped_column(primary_key=True)
    email:Mapped[str] = mapped_column(unique=True)
    password:Mapped[str]
    name:Mapped[str]=mapped_column(unique=True)
    

# with app.app_context():
#     db.create_all()

login_manager = LoginManager()
login_manager.init_app(app=app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return function(*args, **kwargs)
    return wrapper



@app.route("/")
def home_page():
    return render_template("index.html", posts=all_blogs, now=formatted_now, user=current_user)

@app.route("/about")
def get_about_page():
    return render_template("about.html")

@app.route("/post/<int:id>")
def get_post_page(id):
    requested_post = None
    for post in all_blogs:
        if post["id"] == id:
            requested_post = post
    return render_template("post.html", post=requested_post, now=formatted_now, user=current_user)

@app.route('/contact', methods=["POST", "GET"])
def get_contact_page():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        user_email = data["user_email"]
        user_number = data["user_number"]
        user_text = data["user_text"]
        sending_email(username, user_email, user_number, user_text)
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False, user=current_user)

def sending_email(name, email, number, message):
    with smtplib.SMTP("smtp-mail.outlook.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASS)
        connection.sendmail(
            from_addr=MY_EMAIL, 
            to_addrs="abdullabek710@gmail.com", 
            msg=f"Subject:Message From User\n\nName: {name}\nEmail: {email}\nPhone Number:{number}\nMessage:{message}"
        )


@app.route("/register", methods=["POST", "GET"])
def get_register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead")
            return redirect(url_for("get_login_page"))
        else:
            secure_pass = generate_password_hash(password=form.password.data, method='scrypt', salt_length=16)
            new_user = User(
                email = form.email.data,
                password = secure_pass,
                name = form.name.data
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return redirect(url_for('home_page'))

    return render_template('register.html', form=form, user=current_user)

@app.route("/login", methods=["POST", "GET"])
def get_login_page():
    form = LoginForm()
    if form.validate_on_submit():
        usr_email = form.email.data
        usr_password = form.password.data
        selected_usr = User.query.filter_by(email=usr_email).first()
        #? Email doesn't exist 
        if not selected_usr:
            flash("This email doesn't exist in database")
            return redirect(url_for("get_login_page"))
        #? Password incorrect
        elif not check_password_hash(selected_usr.password, usr_password):
            flash("Password incorrect. Please try again")
            return redirect(url_for('get_login_page'))
        else:
            login_user(selected_usr)            
            return redirect(url_for('home_page'))
         
    return render_template('login.html', form=form, user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))
    

if __name__ == "__main__":
    app.run(debug=True)