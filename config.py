import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
    DEBUG = False
    DATABASE = "db.sqlite3"
    API_QUOTA = 100
    METRICS_REFRESH_INTERVAL = 30  # en secondes
