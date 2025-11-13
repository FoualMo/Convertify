import os
from PIL import Image
from PyPDF2 import PdfReader
import markdown
import html2text
from .file_utils import save_file, generate_output_path


class FileConverter:

    def convert_file(self, file, target_format):
        input_path = save_file(file)
        target_format = target_format.lower()

        # Détermine le bon chemin de sortie
        output_path = generate_output_path(input_path, f".{target_format}")

        # --- PDF → Images ---
        if target_format in ["png", "jpg"]:
            return self.pdf_to_images(input_path, target_format)

        # --- Image → JPEG/PNG ---
        if target_format in ["png", "jpg", "jpeg"]:
            return self.convert_image(input_path, output_path, target_format)

        # --- DOCX/TXT/MD/HTML → TXT ---
        if target_format == "txt":
            return self.convert_to_text(input_path, output_path)

        # --- fallback: copie brute ---
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())

        return output_path

    # -----------------------------
    #   CONVERSIONS IMAGES
    # -----------------------------
    def convert_image(self, input_path, output_path, fmt):
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(output_path, fmt.upper())
        return output_path

    # -----------------------------
    #   PDF → Images
    # -----------------------------
    def pdf_to_images(self, input_path, fmt):
        reader = PdfReader(input_path)
        base = os.path.splitext(os.path.basename(input_path))[0]
        folder = f"static/converted/{base}_pages"
        os.makedirs(folder, exist_ok=True)

        paths = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            out = os.path.join(folder, f"page_{i+1}.{fmt}")
            img = Image.new("RGB", (800, 1200), "white")
            return out  # simplifié (placeholder)

        return paths

    # -----------------------------
    #   TEXT
    # -----------------------------
    def convert_to_text(self, input_path, output_path):
        ext = os.path.splitext(input_path)[1].lower()

        try:
            if ext == ".md":
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(markdown.markdown(open(input_path).read()))

            elif ext == ".html":
                txt = html2text.html2text(open(input_path).read())
                open(output_path, "w", encoding="utf-8").write(txt)

            else:
                with open(input_path, "r", encoding="utf-8", errors="ignore") as src:
                    with open(output_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())

        except Exception:
            # fallback
            with open(output_path, "wb") as dst, open(input_path, "rb") as src:
                dst.write(src.read())

        return output_path
