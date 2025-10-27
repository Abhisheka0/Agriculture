# Flask Arduino Sensor Dashboard with Ollama AI

## Features
- Background serial reader (Arduino Uno) with JSON or CSV line support
- Mock mode when serial unavailable (set SERIAL_ENABLED=false)
- SQLite storage via SQLAlchemy
- REST API: `/api/readings`, `/api/aggregates?hours=24`
- Simple Jinja2 UI: dashboard, history, AI analysis
- Ollama integration for recommendations (fallback heuristic if unavailable)

## Setup
1. Create venv and install deps
```powershell
py -3 -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure environment (optional)
```powershell
$env:FLASK_ENV="development"
$env:SERIAL_PORT="COM3"
$env:SERIAL_BAUDRATE="9600"
$env:SERIAL_ENABLED="true"  # set to false to use mock data
$env:OLLAMA_HOST="http://localhost:11434"
$env:OLLAMA_MODEL="llama3.1:8b"
```

3. Initialize database
```powershell
python - << 'PY'
from app import create_app, db
app = create_app('development')
with app.app_context():
    db.create_all()
print('DB initialized')
PY
```

4. Run the app
```powershell
python run.py
```

Open `http://localhost:5000`.

## Arduino Serial Format
Send one line per reading as JSON:
```json
{"temperature_c": 24.5, "humidity": 55.2, "soil_moisture": 620}
```
Or CSV: `24.5,55.2,620`.

## Notes
- If Ollama is running locally with the model available, the Analysis page will use it. Otherwise, a heuristic recommendation is shown.
- Data is read continuously; the dashboard shows latest and 24h averages.


