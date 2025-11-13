class BaseConfig:
    SECRET_KEY = "change-me"
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB max
    UPLOAD_FOLDER = "static/uploads"
    CONVERTED_FOLDER = "static/converted"
    ALLOWED_EXTENSIONS = ["pdf", "docx", "jpg", "png", "txt", "md", "html"]

    ENABLE_SCHEDULER = True
    CLEAN_INTERVAL_MINUTES = 30  # nettoyage toutes les 30 min
    FILE_EXPIRATION_MINUTES = 60  # supprimer fichiers vieux de 1h
