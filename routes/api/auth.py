from datetime import date, datetime
from venv import logger
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User, APIKey, RequestLog
from models.db import db

auth_bp = Blueprint('auth_bp', __name__, url_prefix="/api")


# -------------------
# Auth Blueprint “pro” avec prints
# -------------------
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from models.db import db
from models.user import User
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email déjà utilisé"}), 400

    user = User(
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    print(f"[✅ REGISTER] Nouvel utilisateur : {email}", flush=True)
    return jsonify({"message": "Utilisateur créé"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    user = user.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Identifiants invalides"}), 401
    # Update connexion
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.remote_addr
    user.login_count = (user.login_count or 0) + 1
    login_user(user)

    db.session.commit()

    # Print debug
    print(f"[👤 LOGIN] Utilisateur connecté : {user.email}", flush=True)
    print(f"    Dernière connexion : {user.last_login_at}", flush=True)
    print(f"    IP : {user.last_login_ip}", flush=True)
    print(f"    Nombre total de connexions : {user.login_count}", flush=True)

    return jsonify({"message": "Connecté", "user": user.to_dict()}), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout_post():
    email = current_user.email
    logout_user()
    print(f"[🚪 LOGOUT] Utilisateur déconnecté : {email}", flush=True)
    return jsonify({"message": "Déconnecté"}), 200

@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout_postt():
    email = current_user.email
    logout_user()
    print(f"[🚪 LOGOUT] Utilisateur déconnecté : {email}", flush=True)
    return redirect(url_for('main.index'))

@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({"user": current_user.to_dict()}), 200
