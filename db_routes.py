from flask import Blueprint, request, jsonify
from external_db.db_connection import connect_from_params

db_bp = Blueprint("db", __name__)


@db_bp.route("/connect_db", methods=["POST"])
def connect_db():
    host = request.form.get("host")
    port = int(request.form.get("port"))
    user = request.form.get("user")
    password = request.form.get("password")
    dbname = request.form.get("dbname")

    result = connect_from_params(
        db_type="postgresql",
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
    )

    if result["success"]:
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Підключення успішне до {dbname}",
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "success": False,
                "message": f"Помилка підключення: {result['message']}",
            }
        ),
        400,
    )
