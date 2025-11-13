import os
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/converted"


def ensure_dirs():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def save_file(file):
    """Sauvegarde un fichier uploadé et retourne son chemin."""
    ensure_dirs()
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]
    unique = uuid.uuid4().hex
    filepath = os.path.join(UPLOAD_FOLDER, f"{unique}{ext}")

    file.save(filepath)
    return filepath


def generate_output_path(input_path, new_ext=None):
    """Crée un chemin de fichier de sortie propre."""
    ensure_dirs()
    base = os.path.splitext(os.path.basename(input_path))[0]
    if new_ext:
        return os.path.join(OUTPUT_FOLDER, f"{base}-converted{new_ext}")
    return os.path.join(OUTPUT_FOLDER, f"{base}-converted")


def cleanup_old_files(hours=24):
    """Supprime les fichiers plus vieux que X heures."""
    import time
    now = time.time()

    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            if os.path.isfile(path):
                age = (now - os.path.getmtime(path)) / 3600
                if age > hours:
                    os.remove(path)
