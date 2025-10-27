from app import create_app, db
from config import DevConfig

app = create_app("development")


@app.shell_context_processor
def make_shell_context():
    from app.models import SensorReading
    return {"db": db, "SensorReading": SensorReading}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


