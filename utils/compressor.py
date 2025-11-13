import os
import zipfile
from PIL import Image
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter


class FileCompressor:
    SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]
    SUPPORTED_TEXT_FORMATS = [".txt", ".docx", ".md", ".csv", ".json"]
    OUTPUT_FOLDER = os.path.abspath("static/converted")

    @staticmethod
    def compress_pdf(input_path, output_path):
        """Compression simple PDF (structure réécrite, pas d'optimisation des images)."""
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            return True
        except Exception as e:
            print(f"[⚠] Erreur compression PDF : {e}")
            return False

    @staticmethod
    def compress_image(input_path, output_path, quality=70):
        """Compression d'images via Pillow."""
        try:
            with Image.open(input_path) as img:

                # Convertir si nécessaire (PNG → JPG pour meilleure compression)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                img.save(output_path, "JPEG", optimize=True, quality=quality)

            return True

        except Exception as e:
            print(f"[⚠] Erreur compression image : {e}")
            return False

    @staticmethod
    def compress_other(input_path, output_path, compression_rate=70):
        """
        Compression ZIP pour fichiers non-supportés.
        compression_rate 0–100 → converti en niveau ZIP 1–9
        """
        compresslevel = max(1, min(9, int(compression_rate / 10)))

        try:
            with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=compresslevel) as zipf:
                zipf.write(input_path, arcname=os.path.basename(input_path))

            return True
        except Exception as e:
            print(f"[⚠] Erreur compression fichier : {e}")
            return False

    @staticmethod
    def compress_file(input_path, compression_rate=70):
        """Détecte le type de fichier et appelle la bonne fonction."""
        filename = secure_filename(os.path.basename(input_path))
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        os.makedirs(FileCompressor.OUTPUT_FOLDER, exist_ok=True)

        # Le chemin final (définitif)
        if ext == ".pdf":
            output_path = os.path.join(FileCompressor.OUTPUT_FOLDER, f"{name}-compressed.pdf")

        elif ext in FileCompressor.SUPPORTED_IMAGE_FORMATS:
            output_path = os.path.join(FileCompressor.OUTPUT_FOLDER, f"{name}-compressed.jpg")

        else:
            output_path = os.path.join(FileCompressor.OUTPUT_FOLDER, f"{name}-compressed.zip")

        # Appel du bon compresseur
        if ext == ".pdf":
            FileCompressor.compress_pdf(input_path, output_path)

        elif ext in FileCompressor.SUPPORTED_IMAGE_FORMATS:
            FileCompressor.compress_image(input_path, output_path, quality=compression_rate)

        else:
            FileCompressor.compress_other(input_path, output_path, compression_rate=compression_rate)

        return output_path
