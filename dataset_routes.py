from flask import Blueprint, request, jsonify
from external_db.db_connection import connect_to_database
from external_db.dataset_builder import build_dataset

dataset_bp = Blueprint("dataset", __name__)


@dataset_bp.route("/connect_db", methods=["POST"])
def connect_db_route():
    host = request.form.get("host")
    port = int(request.form.get("port", 5432))
    user = request.form.get("user")
    password = request.form.get("password")
    dbname = request.form.get("dbname")

    success = connect_to_database(host, port, user, password, dbname)

    if success:
        return jsonify(
            {
                "success": True,
                "message": f"Підключено до БД ({dbname})",
            }
        )

    return (
        jsonify(
            {
                "success": False,
                "message": f"Не вдалося підключитися до БД {dbname}",
            }
        ),
        400,
    )


@dataset_bp.route("/build_dataset", methods=["POST"])
def build_dataset_route():
    filename = request.form.get("filename")
    safe_count = int(request.form.get("safe_count", 100))
    mal_count = int(request.form.get("mal_count", 100))

    try:
        filepath = build_dataset(
            filename=filename,
            num_safe=safe_count,
            num_malicious=mal_count,
        )
        return jsonify(
            {
                "success": True,
                "message": f"Датасет збережено: {filepath}",
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Помилка генерації датасета: {str(e)}",
                }
            ),
            500,
        )
