import json
import random
import threading
import time
from datetime import datetime
from typing import Optional

import serial  # type: ignore
from flask import Flask

from .models import insert_reading
from . import db


class SerialReaderThread(threading.Thread):
    daemon = True

    def __init__(self, app: Flask):
        super().__init__(name="SerialReaderThread")
        self._stop_event = threading.Event()
        self._serial = None
        self._app = app

    def stop(self):
        self._stop_event.set()
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass

    def run(self):
        with self._app.app_context():
            port = self._app.config.get("SERIAL_PORT")
            baud = self._app.config.get("SERIAL_BAUDRATE")
            enabled = self._app.config.get("SERIAL_ENABLED", True)

            use_mock = False
            if enabled:
                try:
                    self._serial = serial.Serial(port, baudrate=baud, timeout=2)
                except Exception:
                    use_mock = True
            else:
                use_mock = True

            if use_mock:
                self._run_mock_loop()
            else:
                self._run_serial_loop()

    def _run_serial_loop(self):
        while not self._stop_event.is_set():
            try:
                line = self._serial.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                # Expect JSON line like: {"temperature_c": 24.5, "humidity": 55.2, "soil_moisture": 620}
                payload = self._parse_line(line)
                if payload is None:
                    continue
                insert_reading(payload.get("temperature_c"), payload.get("humidity"), payload.get("soil_moisture"))
                db.session.remove()
            except Exception:
                time.sleep(1)

    def _parse_line(self, line: str) -> Optional[dict]:
        try:
            data = json.loads(line)
            return {
                "temperature_c": self._to_float(data.get("temperature_c")),
                "humidity": self._to_float(data.get("humidity")),
                "soil_moisture": self._to_float(data.get("soil_moisture")),
            }
        except Exception:
            # Try CSV: temp,humidity,soil
            try:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    return {
                        "temperature_c": self._to_float(parts[0]),
                        "humidity": self._to_float(parts[1]),
                        "soil_moisture": self._to_float(parts[2]),
                    }
            except Exception:
                return None
        return None

    def _to_float(self, value) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except Exception:
            return None

    def _run_mock_loop(self):
        rng = random.Random(42)
        while not self._stop_event.is_set():
            temp = 20.0 + rng.random() * 10.0
            hum = 40.0 + rng.random() * 30.0
            soil = 300 + rng.random() * 400
            insert_reading(temp, hum, soil)
            db.session.remove()
            time.sleep(2)


