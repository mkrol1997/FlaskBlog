from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.forms import LoginForm, RegisterForm
from app.models import User

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=request.form["email"],
            password=generate_password_hash(password=request.form["password"], salt_length=8),
            name=request.form["name"]
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except exc.IntegrityError:
            flash("User already exist. Please log in.")
            return redirect(url_for(".login"))
        else:
            login_user(new_user)
            return redirect(url_for("main.get_all_posts"))

    else:
        return render_template("register.html", form=form)


@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form["email"]).first()
        if user:
            if check_password_hash(user.password, request.form["password"]):
                login_user(user)
                return redirect(url_for("main.get_all_posts"))
            else:
                flash("Wrong password")
                return redirect(url_for(".login"))
        else:
            flash("This email is not registered")
            return redirect(url_for(".login"))
    else:
        return render_template("login.html", form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.get_all_posts'))
