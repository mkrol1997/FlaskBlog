from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash

from flask_login import login_user, login_required, current_user, logout_user
from forms import CreatePostForm, LoginForm, RegisterForm, CommentForm
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash
from constants import DB_PATH
from app import db
from app.models import *
import os
from app import create_app
from flask_login import LoginManager
from app.decorators import admin_only

app = create_app()

with app.app_context():
    if not os.path.exists(DB_PATH):
        db.create_all()

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            new_user = User(email=request.form["email"], password=generate_password_hash(password=request.form["password"], salt_length=8), name=request.form["name"])
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_all_posts"))
        except exc.IntegrityError:
            flash("User already exist. Please log in.")
            return redirect(url_for("login"))
    else:
        return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form["email"]).first()
        if user:
            if check_password_hash(user.password, request.form["password"]):
                login_user(user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Wrong password")
                return redirect(url_for("login"))
        else:
            flash("This email is not registered")
            return redirect(url_for("login"))
    else:
        return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if request.method == "POST":
        try:
            comment = Comment(text=request.form.get('comment'), author_id=current_user.id, post_id=requested_post.id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=post_id))
        except AttributeError:
            flash("You need to login or register to comment")
            return redirect(url_for("login"))
    else:
        return render_template("post.html", post=requested_post, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    else:
        return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run()
