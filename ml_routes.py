from flask import Blueprint, jsonify
from train_from_db import train_from_db

ml_bp = Blueprint("ml_bp", __name__)


@ml_bp.route("/train_model", methods=["POST"])
def train_model_route():
    try:
        report, roc_auc = train_from_db()
        return jsonify(
            {
                "success": True,
                "message": "Модель успішно перенавчена",
                "roc_auc": roc_auc,
                "report": report,
            }
        )
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": (
                    "Виникла помилка під час навчання моделі: "
                    f"{str(e)}"
                ),
            }
        )
