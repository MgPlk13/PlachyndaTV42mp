from functools import wraps

from flask import session, redirect, url_for, abort, request


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            session["next_url"] = request.url
            return redirect(url_for("auth.login"))

        return view_func(*args, **kwargs)

    return wrapped_view


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not session.get("logged_in"):
                return redirect(url_for("auth.login"))

            user_role = session.get("role")
            if user_role not in roles:
                return abort(403)

            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator
