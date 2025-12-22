import logging

from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from external_db.db_connection import connect_from_params, get_current_uri, get_engine

tester_bp = Blueprint("tester", __name__)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@tester_bp.route("/check_query", methods=["POST"])
def check_query():
    engine = get_engine()
    if engine is None:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": (
                        "Немає активного підключення до БД. "
                        "Спочатку підключіться."
                    ),
                }
            ),
            400,
        )

    data = request.get_json() or {}
    sql = data.get("query", "").strip()

    if not sql:
        return jsonify({"status": "error", "message": "Порожній SQL-запит"}), 400

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            if result.returns_rows:
                rows = [dict(r._mapping) for r in result]
                return (
                    jsonify(
                        {
                            "status": "success",
                            "message": "Запит виконано успішно",
                            "rows": rows,
                        }
                    ),
                    200,
                )

            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Запит виконано (без результату)",
                    }
                ),
                200,
            )

    except SQLAlchemyError as e:
        error_msg = str(e.__cause__ or e)
        logger.error(f"SQL Error: {error_msg}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"SQL помилка: {error_msg}",
                }
            ),
            400,
        )

    except Exception as e:
        logger.exception("Непередбачена помилка у /check_query")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Внутрішня помилка: {str(e)}",
                }
            ),
            500,
        )


@tester_bp.route("/tester")
def tester_page():
    current_uri = get_current_uri()
    return render_template("tester.html", current_uri=current_uri)


@tester_bp.route("/connect_db", methods=["GET", "POST"])
def connect_db():
    if request.method == "POST":
        db_type = request.form.get("db_type")
        host = request.form.get("host")
        port = request.form.get("port")
        dbname = request.form.get("dbname")
        user = request.form.get("user")
        password = request.form.get("password")
        file_path = request.form.get("file_path")

        result = connect_from_params(
            db_type=db_type,
            host=host,
            port=int(port) if port else None,
            dbname=dbname,
            user=user,
            password=password,
            file_path=file_path,
        )

        if result["success"]:
            logger.info(f"Підключено до БД: {result['message']}")
            return redirect(url_for("tester.tester_page"))

        logger.error(f"Помилка підключення: {result['message']}")
        return render_template("connect_db.html", result=result)

    return render_template("connect_db.html", result=None)
