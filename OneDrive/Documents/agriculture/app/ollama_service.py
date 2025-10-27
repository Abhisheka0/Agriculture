import json
from typing import Dict

import requests
from flask import current_app


def _build_prompt(aggregates: Dict) -> str:
    lines = [
        "You are an agronomy assistant. Analyze environmental sensor data and provide:",
        "1) Brief assessment of crop stress risk",
        "2) Irrigation recommendation (when/how much)",
        "3) Preventive measures",
        "4) Any anomalies to check",
        "Use clear, concise bullet points."
    ]
    lines.append("\nSensor aggregates (last window):")
    for k in ["avg_temperature_c", "avg_humidity", "avg_soil_moisture", "since", "count", "last_reading"]:
        lines.append(f"- {k}: {aggregates.get(k)}")
    return "\n".join(lines)


def analyze_conditions(aggregates: Dict) -> str:
    host = current_app.config.get("OLLAMA_HOST", "http://localhost:11434")
    model = current_app.config.get("OLLAMA_MODEL", "llama3.1:8b")
    prompt = _build_prompt(aggregates)

    try:
        resp = requests.post(
            f"{host}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "No response from model.")
    except Exception as e:
        # Fallback simple heuristic if Ollama is unavailable
        return _heuristic_recommendation(aggregates, error=str(e))


def _heuristic_recommendation(aggregates: Dict, error: str = "") -> str:
    t = aggregates.get("avg_temperature_c")
    h = aggregates.get("avg_humidity")
    s = aggregates.get("avg_soil_moisture")

    notes = []
    stress = []
    irrigation = []

    if t is not None and t > 32:
        stress.append("High temperature may cause heat stress.")
    if h is not None and h < 35:
        stress.append("Low humidity could increase transpiration and stress.")
    if s is not None and s < 400:
        irrigation.append("Soil moisture low: consider watering soon.")
    elif s is not None and s > 700:
        irrigation.append("Soil moisture high: delay irrigation to prevent root issues.")
    else:
        irrigation.append("Maintain regular irrigation schedule.")

    notes.append("Mulch to reduce evaporation.")
    notes.append("Irrigate early morning or late evening.")

    result = ["Heuristic recommendation (Ollama unavailable):"]
    if error:
        result.append(f"- Note: {error}")
    if stress:
        result.append("- Crop stress:")
        result += [f"  - {x}" for x in stress]
    if irrigation:
        result.append("- Irrigation:")
        result += [f"  - {x}" for x in irrigation]
    result.append("- Preventive measures:")
    result += [f"  - {x}" for x in notes]
    return "\n".join(result)


