from flask import Blueprint, render_template, redirect, url_for, Response
from sqlalchemy.orm import joinedload
from analytics_module import AnalyticsSession, AttackLog
from io import StringIO
from decorators import login_required

log_bp = Blueprint("log", __name__)


@log_bp.route("/logs")
@login_required
def view_logs():
    with AnalyticsSession() as db:
        logs = db.query(AttackLog) \
            .options(joinedload(AttackLog.attack_type)) \
            .order_by(AttackLog.timestamp.desc()) \
            .limit(100).all()

    return render_template("logs.html", logs=logs)


@log_bp.route("/logs/download")
@login_required
def download_logs():
    with AnalyticsSession() as db:
        logs = db.query(AttackLog) \
            .options(joinedload(AttackLog.attack_type)) \
            .order_by(AttackLog.timestamp.desc()).all()

    output = StringIO()
    output.write("timestamp,reason,attack_type,query,score,source_ip,status\n")
    for log in logs:
        attack_type = log.attack_type.code if log.attack_type else "-"
        score_str = f"{log.score:.2f}" if log.score is not None else "-"
        output.write(
            f"{log.timestamp},{log.reason},{attack_type},{log.query},{score_str},{log.source_ip},{log.status}\n"
        )

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attack_logs.csv"}
    )


@log_bp.route("/logs/clear")
@login_required
def clear_logs():
    with AnalyticsSession() as db:
        db.query(AttackLog).delete()
        db.commit()

    return redirect(url_for("log.view_logs"))
