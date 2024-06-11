from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user

from . import db
from .models import Cat, User
from werkzeug.security import generate_password_hash, check_password_hash

authentication = Blueprint("authentication", __name__)


@authentication.route("/login")
def login():
    return render_template("login.html")


@authentication.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    raw_password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, raw_password):
        flash("You have entered invalid login details. Please try again.")
        return redirect(url_for("authentication.login"))

    login_user(user, remember=remember)
    return redirect(url_for("main.profile"))


@authentication.route("/signup")
def signup():
    return render_template("signup.html")


@authentication.route("/signup", methods=["POST"])
def signup_post():
    # Make sure user with that username does not already exist
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()
    if user:
        flash("A user with that username already exists!")
        return redirect(url_for("authentication.signup"))

    new_user = User(
        username=username,
        password=generate_password_hash(password, method="pbkdf2:sha256"),
    )

    db.session.add(new_user)
    db.session.commit()
    return redirect((url_for("authentication.login")))


@authentication.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

