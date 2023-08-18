from datetime import timedelta
from hashlib import md5

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from app.constants import DB_PATH

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    encryptor = md5()

    app.permanent_session_lifetime = timedelta(minutes=30)
    app.secret_key = encryptor.digest()

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.debug = True
    login_manager = LoginManager()
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    CKEditor(app)
    Bootstrap(app)
    Gravatar(app,
             size=100,
             rating='g',
             default='retro',
             force_default=False,
             force_lower=False,
             use_ssl=False,
             base_url=None)

    from app.main import main
    app.register_blueprint(main)

    from app.auth import auth
    app.register_blueprint(auth)

    return app
