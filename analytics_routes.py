from flask import Blueprint, render_template
from sqlalchemy.orm import joinedload
from analytics_module import AnalyticsSession, AttackLog, AttackType
from collections import Counter
from datetime import datetime
from decorators import login_required

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
@login_required
def analytics():
    with AnalyticsSession() as db:
        logs = (
            db.query(AttackLog)
            .options(joinedload(AttackLog.attack_type))
            .order_by(AttackLog.timestamp.desc())
            .all()
        )

        ai_count_today = 0
        hourly_counter = Counter()
        dangerous_queries = []

        for log in logs:
            try:
                ts = datetime.strptime(log.timestamp, "%Y-%m-%d %H:%M:%S")

                hour = ts.strftime("%H:00")
                hourly_counter[hour] += 1

                if (
                        log.reason.upper().startswith("AI")
                        and ts.date() == datetime.today().date()
                ):
                    ai_count_today += 1
                    dangerous_queries.append(
                        {
                            "timestamp": ts,
                            "reason": log.reason,
                            "query": log.query,
                            "attack_type": getattr(log.attack_type, "code", "-"),
                            "score": log.score,
                        }
                    )
            except Exception:
                continue

        top_queries = sorted(
            dangerous_queries,
            key=lambda x: x["timestamp"],
            reverse=True,
        )[:5]

        for q in top_queries:
            q["timestamp"] = q["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            q["score"] = f"{q['score']:.2f}" if q["score"] is not None else "-"

    return render_template(
        "analytics.html",
        ai_today=ai_count_today,
        hourly_data=sorted(hourly_counter.items()),
        top_queries=top_queries,
    )
