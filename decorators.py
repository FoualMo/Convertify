from functools import wraps
from flask import abort, jsonify
from flask_login import current_user

def require_active_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_active:
            return jsonify({"error": "Compte désactivé"}), 403
        
        return f(*args, **kwargs)
    return wrapper

# =========================
# Décorateur pour protéger les routes admin
# =========================
def require_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Accès refusé
        return func(*args, **kwargs)
    return wrapper