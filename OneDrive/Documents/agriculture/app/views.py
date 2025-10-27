from datetime import datetime, timedelta

from flask import Blueprint, jsonify, render_template, request, current_app

from .models import SensorReading, get_recent_readings, get_aggregates
from . import db
from .ollama_service import analyze_conditions


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    latest = SensorReading.query.order_by(SensorReading.created_at.desc()).first()
    aggregates = get_aggregates(hours=24)
    readings = get_recent_readings(limit=60)

    def to_soil_percent(value: float | None) -> float | None:
        if value is None:
            return None
        # Heuristic mapping for raw analog (0-1023). Mock uses ~300-700 range.
        min_v, max_v = 300.0, 700.0
        pct = (value - min_v) / (max_v - min_v) * 100.0
        if pct < 0:
            pct = 0.0
        if pct > 100:
            pct = 100.0
        return pct

    chart = {
        "temp": [r.temperature_c for r in readings if r.temperature_c is not None],
        "hum": [r.humidity for r in readings if r.humidity is not None],
        "soil": [to_soil_percent(r.soil_moisture) for r in readings if r.soil_moisture is not None],
    }

    latest_soil_pct = to_soil_percent(latest.soil_moisture) if latest else None

    return render_template(
        "dashboard.html",
        latest=latest,
        aggregates=aggregates,
        chart=chart,
        latest_soil_pct=latest_soil_pct,
    )


@bp.route("/history")
def history():
    limit = int(request.args.get("limit", 100))
    readings = get_recent_readings(limit=limit)
    return render_template("history.html", readings=readings)


# REST API
@bp.route("/api/readings")
def api_readings():
    limit = int(request.args.get("limit", 100))
    readings = [r.to_dict() for r in get_recent_readings(limit=limit)]
    return jsonify({"readings": readings})


@bp.route("/api/aggregates")
def api_aggregates():
    hours = int(request.args.get("hours", 24))
    return jsonify(get_aggregates(hours=hours))


@bp.route("/analysis", methods=["GET", "POST"])
def analysis():
    result = None
    if request.method == "POST":
        hours = int(request.form.get("hours", 24))
        agg = get_aggregates(hours=hours)
        result = analyze_conditions(agg)
    else:
        agg = get_aggregates(hours=24)

    def to_soil_percent(value):
        if value is None:
            return None
        min_v, max_v = 300.0, 700.0
        pct = (value - min_v) / (max_v - min_v) * 100.0
        if pct < 0:
            pct = 0.0
        if pct > 100:
            pct = 100.0
        return pct

    def fmt_time(value):
        try:
            from datetime import datetime
            if not value:
                return None
            s = str(value).replace("Z", "")
            dt = datetime.fromisoformat(s)
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return value

    summary = {
        "avg_temperature_c": round(agg.get("avg_temperature_c"), 1) if agg.get("avg_temperature_c") is not None else None,
        "avg_humidity": round(agg.get("avg_humidity"), 1) if agg.get("avg_humidity") is not None else None,
        "avg_soil_pct": (lambda v: round(v, 1) if v is not None else None)(to_soil_percent(agg.get("avg_soil_moisture"))),
        "count": agg.get("count"),
        "since": agg.get("since"),
        "last": agg.get("last_reading"),
        "since_fmt": fmt_time(agg.get("since")),
        "last_fmt": fmt_time(agg.get("last_reading")),
    }

    return render_template("analysis.html", aggregates=agg, summary=summary, result=result)


