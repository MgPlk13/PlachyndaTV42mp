import traceback

from flask import Flask, render_template
from sqlalchemy import create_engine

from analytics_routes import analytics_bp
from auth_module import auth_bp
from config_db import DATABASE_URI, SECRET_KEY
from dataset_routes import dataset_bp
from db_routes import db_bp
from log_module import log_bp
from ml_routes import ml_bp
from tester_routes import tester_bp

try:
    from realtime_routes import realtime_bp

    _HAS_REALTIME = True
except Exception as e:
    realtime_bp = None
    _HAS_REALTIME = False
    print("realtime_routes не импортирован:", e)
    traceback.print_exc()

app = Flask(__name__)
app.secret_key = SECRET_KEY

engine = create_engine(DATABASE_URI)

if _HAS_REALTIME and realtime_bp is not None:
    try:
        app.register_blueprint(realtime_bp)
        print("realtime_bp registered")
    except Exception as e:
        print("Не удалось зарегистрировать realtime_bp:", e)
        traceback.print_exc()
else:
    print("Пропущена регистрация realtime_bp")

app.register_blueprint(db_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(ml_bp)
app.register_blueprint(tester_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(log_bp)
app.register_blueprint(dataset_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dos_sim")
def dos_sim():
    return render_template("dos_sim.html")


if __name__ == "__main__":
    app.run(debug=True)
