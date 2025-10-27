from datetime import datetime, timedelta
from typing import Optional

from . import db


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)
    temperature_c = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    soil_moisture = db.Column(db.Float, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() + "Z",
            "temperature_c": self.temperature_c,
            "humidity": self.humidity,
            "soil_moisture": self.soil_moisture,
        }


def insert_reading(temperature_c: Optional[float], humidity: Optional[float], soil_moisture: Optional[float]) -> SensorReading:
    reading = SensorReading(
        temperature_c=temperature_c,
        humidity=humidity,
        soil_moisture=soil_moisture,
    )
    db.session.add(reading)
    db.session.commit()
    return reading


def get_recent_readings(limit: int = 100):
    return (
        SensorReading.query.order_by(SensorReading.created_at.desc())
        .limit(limit)
        .all()
    )


def get_time_window(start: datetime, end: datetime):
    return (
        SensorReading.query.filter(SensorReading.created_at >= start, SensorReading.created_at <= end)
        .order_by(SensorReading.created_at.asc())
        .all()
    )


def get_aggregates(hours: int = 24) -> dict:
    from sqlalchemy import func
    since = datetime.utcnow() - timedelta(hours=hours)
    # Aggregate averages for last N hours
    q = db.session.query(
        func.avg(SensorReading.temperature_c),
        func.avg(SensorReading.humidity),
        func.avg(SensorReading.soil_moisture),
        func.min(SensorReading.created_at),
        func.max(SensorReading.created_at),
        func.count(SensorReading.id),
    ).filter(SensorReading.created_at >= since)

    avg_temp, avg_hum, avg_soil, min_time, max_time, count = q.one()
    return {
        "since": since.isoformat() + "Z",
        "count": int(count or 0),
        "avg_temperature_c": float(avg_temp) if avg_temp is not None else None,
        "avg_humidity": float(avg_hum) if avg_hum is not None else None,
        "avg_soil_moisture": float(avg_soil) if avg_soil is not None else None,
        "first_reading": min_time.isoformat() + "Z" if min_time else None,
        "last_reading": max_time.isoformat() + "Z" if max_time else None,
    }


