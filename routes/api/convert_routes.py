from flask import Blueprint, request, send_file, jsonify
from flask_login import login_required, current_user
from services.converter import FileConverter
from models.user import APIKey, RequestLog, db
import os
import time

convert_bp = Blueprint("convert", __name__, url_prefix="/convertify/api")

# Formats autorisés
ALLOWED_FORMATS = ["pdf", "png", "txt", "jpg", "docx"]

# -------------------------
# Vérification compte actif
# -------------------------
@convert_bp.before_request
def check_user_active():
    if not current_user.is_authenticated:
        return
    if not current_user.is_active:
        return jsonify({"error": "Compte désactivé"}), 403

# -------------------------
# Endpoint de conversion
# -------------------------
@convert_bp.route("/convert", methods=["POST"])
@login_required
def convert_file():

    try:
        # Vérification présence fichier
        if "file" not in request.files:
            return jsonify({"error": "Aucun fichier envoyé"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Fichier invalide"}), 400

        # Vérification format cible
        target_format = request.form.get("format", "").lower().strip()
        if target_format not in ALLOWED_FORMATS:
            return jsonify({"error": "Format cible invalide ou non supporté"}), 400

        # Vérifier quota quotidien
        api_keys = APIKey.query.filter_by(user_id=current_user.id, revoked=False).all()
        if not api_keys:
            return jsonify({"error": "Aucune clé API active trouvée"}), 403

        total_today_usage = sum(k.today_usage for k in api_keys)
        total_daily_limit = sum(k.daily_limit for k in api_keys)

        if total_today_usage >= total_daily_limit:
            return jsonify({"error": "Quota journalier dépassé"}), 429

        # Conversion
        start_time = time.time()
        converter = FileConverter()
        output_path = converter.convert_file(file, target_format)
        duration_ms = (time.time() - start_time) * 1000

        # Mettre à jour utilisation today_usage
        for k in api_keys:
            k.today_usage += 1
        db.session.commit()

        # Log de la requête
        log = RequestLog(
            user_id=current_user.id,
            endpoint=request.path,
            method=request.method,
            status_code=200,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            response_time_ms=duration_ms
        )
        db.session.add(log)
        db.session.commit()

        # Envoi fichier
        response = send_file(
            output_path,
            as_attachment=True,
            download_name=os.path.basename(output_path)
        )

        # Supprimer fichier temporaire après envoi
        @response.call_on_close
        def cleanup_temp():
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception as e:
                print(f"Erreur suppression fichier temporaire : {e}")

        return response

    except Exception as e:
        return jsonify({"error": f"Erreur interne : {str(e)}"}), 500
