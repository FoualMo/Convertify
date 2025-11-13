import os
import zipfile
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename
from .file_utils import OUTPUT_FOLDER


class FileCompressor:
    IMAGE_EXT = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"]
    TEXT_EXT = [".txt", ".md", ".csv", ".json", ".docx"]

    @staticmethod
    def compress_pdf(input_path, output_path):
        """Compression PDF simple (réécriture, pas Ghostscript)."""
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)

            with open(output_path, "wb") as f:
                writer.write(f)

            return True
        except Exception as e:
            print("Erreur PDF :", e)
            return False

    @staticmethod
    def compress_image(input_path, output_path, quality=70):
        try:
            with Image.open(input_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(output_path, "JPEG", optimize=True, quality=quality)
            return True
        except Exception as e:
            print("Erreur image :", e)
            return False

    @staticmethod
    def compress_zip(input_path, output_path, rate=70):
        level = max(1, min(9, int(rate / 10)))
        try:
            with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=level) as z:
                z.write(input_path, arcname=os.path.basename(input_path))
            return True
        except Exception as e:
            print("Erreur ZIP :", e)
            return False

    @staticmethod
    def compress_file(input_path, rate=70):
        """Détecte le type + compresse."""
        filename = secure_filename(os.path.basename(input_path))
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # --- Sélection du type de compression ---
        if ext == ".pdf":
            output_path = os.path.join(OUTPUT_FOLDER, f"{name}-compressed.pdf")
            FileCompressor.compress_pdf(input_path, output_path)

        elif ext in FileCompressor.IMAGE_EXT:
            output_path = os.path.join(OUTPUT_FOLDER, f"{name}-compressed.jpg")
            FileCompressor.compress_image(input_path, output_path, quality=rate)

        elif ext in FileCompressor.TEXT_EXT or ext not in FileCompressor.IMAGE_EXT:
            output_path = os.path.join(OUTPUT_FOLDER, f"{name}-compressed.zip")
            FileCompressor.compress_zip(input_path, output_path, rate)

        return output_path
