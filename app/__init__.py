from datetime import timedelta
from hashlib import md5

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor

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

    return app
