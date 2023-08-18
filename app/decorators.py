from flask_login.utils import current_user
from flask import abort, redirect, url_for


def admin_only(function):
    def wrapper(*args, **kwargs):
        if current_user:
            if current_user.is_anonymous or not current_user.superuser:
                return abort(status=403)
            else:
                return function()
        else:
            return redirect(url_for("login"), *args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper
