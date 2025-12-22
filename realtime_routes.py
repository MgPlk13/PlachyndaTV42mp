import json
import random
import threading
import time
import requests
from flask import Blueprint, Response, jsonify
from analytics_module import AnalyticsSession, AttackLog
from datetime import datetime
from train_from_db import train_from_db

realtime_bp = Blueprint("realtime", __name__)

allowed_count = 0
blocked_count = 0
_sim_running = False
_sim_thread = None

from queries_generator import generate_safe_queries, generate_malicious_queries

SAFE_QUERIES = generate_safe_queries(500)
MALICIOUS_QUERIES = generate_malicious_queries(500)

BASE_URL = "http://127.0.0.1:5000"


def log_attack_to_db(query: str, status: str, reason: str = "", score: float = 0.0):
    with AnalyticsSession() as session:
        log = AttackLog(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            reason=reason or ("malicious" if status == "blocked" else "safe"),
            query=query,
            score=score,
            status=status,
        )
        session.add(log)
        session.commit()


def _simulate_worker():
    global allowed_count, blocked_count, _sim_running

    while _sim_running:
        sql = random.choice(SAFE_QUERIES + MALICIOUS_QUERIES)
        try:
            r = requests.post(
                f"{BASE_URL}/check_query",
                json={"query": sql},
                timeout=2,
            )
            result = r.json().get("result", "")

            if result.startswith("✅"):
                allowed_count += 1
                log_attack_to_db(sql, "allowed", reason="safe")
            else:
                blocked_count += 1
                log_attack_to_db(sql, "blocked", reason="error_from_db")

        except Exception as e:
            blocked_count += 1
            log_attack_to_db(sql, "blocked", reason=str(e))

        time.sleep(0.7)


@realtime_bp.route("/dos_stream")
def dos_stream():
    def event_stream():
        while True:
            data = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "allowed": allowed_count,
                "blocked": blocked_count,
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)

    return Response(event_stream(), mimetype="text/event-stream")


@realtime_bp.route("/simulate/start", methods=["POST"])
def start_simulation():
    global allowed_count, blocked_count, _sim_running, _sim_thread

    if _sim_running:
        return jsonify({"status": "already_running"}), 409

    allowed_count = 0
    blocked_count = 0
    _sim_running = True

    _sim_thread = threading.Thread(target=_simulate_worker, daemon=True)
    _sim_thread.start()

    return jsonify({"status": "started"})


@realtime_bp.route("/simulate/stop", methods=["POST"])
def stop_simulation():
    global _sim_running
    _sim_running = False
    return jsonify({"status": "stopped"})


@realtime_bp.route("/train_model", methods=["POST"])
def train_model_route():
    result = train_from_db()
    return jsonify(result)
