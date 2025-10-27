import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLITE_PATH = os.path.join(BASE_DIR, "sensor_data.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Serial settings
    SERIAL_PORT = os.environ.get("SERIAL_PORT", "COM3")
    SERIAL_BAUDRATE = int(os.environ.get("SERIAL_BAUDRATE", "9600"))
    SERIAL_ENABLED = os.environ.get("SERIAL_ENABLED", "true").lower() == "true"

    # Ollama
    OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")


class DevConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevConfig,
    "production": ProdConfig,
}


