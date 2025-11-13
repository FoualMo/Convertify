from flask import Blueprint, request, send_file, jsonify
from flask_login import login_required
from services.compressor import FileCompressor
from services.file_utils import save_file

compress_bp = Blueprint("compress", __name__, url_prefix="/convertify/api")




# appliquer automatiquement à toutes les routes du blueprint
@compress_bp.before_request
def check_user_active():
    from flask_login import current_user

    # si non connecté → laisse l'autre décorateur gérer
    if not current_user.is_authenticated:
        return

    # si désactivé → bloque tout
    if not current_user.is_active:
        return {"error": "Compte désactivé"}, 403









@compress_bp.route("/compress", methods=["POST"])
def compress_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Aucun fichier envoyé"}), 400

        file = request.files["file"]
        rate = request.form.get("rate", 70)

        try:
            rate = int(rate)
        except:
            rate = 70

        input_path = save_file(file)
        output_path = FileCompressor.compress_file(input_path, rate)

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_path.split("/")[-1]
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
