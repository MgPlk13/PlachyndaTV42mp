from flask import Blueprint, request, render_template, redirect, url_for, session
from decorators import login_required

auth_bp = Blueprint("auth", __name__)

USERS = {
    "devops": {"password": "1234", "role": "admin"},
    "analyst": {"password": "5678", "role": "viewer"},
    "guest": {"password": "0000", "role": "guest"},
}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = USERS.get(username)
        if user and user["password"] == password:
            session["logged_in"] = True
            session["username"] = username
            session["role"] = user["role"]
            next_url = session.pop("next_url", None)
            if next_url:
                return redirect(next_url)

            return redirect(url_for("log.view_logs"))

        return render_template("login.html", error="Невірний логін або пароль")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
