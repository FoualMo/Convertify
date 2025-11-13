from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, date
from .db import db

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# ----------------------------------------------------
# 👤 Modèle Utilisateur avec logs
# ----------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -----------------------------
    # Suivi des connexions
    # -----------------------------
    last_login_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    login_count = db.Column(db.Integer, default=0)

    # relations
    api_keys = db.relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    request_logs = db.relationship("RequestLog", back_populates="user")

    # -----------------------------
    # Gestion du mot de passe
    # -----------------------------
    @property
    def password(self):
        raise AttributeError("Le mot de passe n'est pas lisible.")

    @password.setter
    def password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)
        print(f"[✅] Mot de passe défini pour {self.email}")

    def check_password(self, raw_password):
        result = check_password_hash(self.password_hash, raw_password)
        print(f"[🔐] Vérification mot de passe pour {self.email} → {'OK' if result else 'ECHEC'}")
        return result

    # -----------------------------
    # Méthode pour enregistrer la connexion
    # -----------------------------
    def register_login(self, ip_address=None):
        from models.db import db

        old_date = self.last_login_at
        self.last_login_at = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address
        self.login_count = (self.login_count or 0) + 1
        db.session.commit()
        db.session.refresh(self)

        # prints simples avec flush=True
        print(f"[👤 LOGIN] Utilisateur connecté : {self.email}", flush=True)
        print(f"    Ancienne connexion : {old_date}", flush=True)
        print(f"    Nouvelle connexion : {self.last_login_at}", flush=True)
        print(f"    IP : {self.last_login_ip}", flush=True)
        print(f"    Nombre total de connexions : {self.login_count}", flush=True)



    # -----------------------------
    # Sérialisation
    # -----------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "login_count": self.login_count
        }

    def __repr__(self):
        return f"<User {self.email} - Admin: {self.is_admin} - Active: {self.last_login_at}>"


# ----------------------------------------------------
# 🔑 Modèle Clé API
# ----------------------------------------------------
class APIKey(db.Model):
    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    daily_limit = db.Column(db.Integer, default=100)
    revoked = db.Column(db.Boolean, default=False)
    today_usage = db.Column(db.Integer, default=0)

    last_used_at = db.Column(db.DateTime, nullable=True)
    total_usage = db.Column(db.Integer, default=0)

    user = db.relationship("User", back_populates="api_keys")

    def increment_usage(self):
        """Incrémente le compteur d'utilisation."""
        self.today_usage += 1
        self.total_usage += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()

        print(f"[🔑] Clé utilisée par {self.user.email}")
        print(f"    API Key : {self.api_key}")
        print(f"    Utilisations aujourd'hui : {self.today_usage}")
        print(f"    Total cumulé : {self.total_usage}")

    @property
    def is_active(self):
        return not self.revoked

    def __repr__(self):
        return f"<APIKey {self.api_key} for {self.user.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_email": self.user.email,
            "api_key": self.api_key,
            "created_at": self.created_at.isoformat(),
            "daily_limit": self.daily_limit,
            "revoked": self.revoked,
            "today_usage": self.today_usage,
            "total_usage": self.total_usage,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }


# ----------------------------------------------------
# 📊 Modèle Journal des Requêtes
# ----------------------------------------------------
class RequestLog(db.Model):
    __tablename__ = "request_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=True)

    date = db.Column(db.Date, default=date.today)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    response_time_ms = db.Column(db.Float, nullable=True)

    user = db.relationship("User", back_populates="request_logs")

    def __repr__(self):
        return f"<RequestLog {self.endpoint} [{self.method}] - user {self.user_id}>"

    @property
    def timestamp(self):
        return f"{self.date} {self.time.strftime('%H:%M:%S')}"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "date": self.date.isoformat(),
            "time": self.time.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "response_time_ms": self.response_time_ms
        }

    def log_to_console(self):
        logger.info(f"[📄 LOG] {self.method} {self.endpoint} (user={self.user_id}) → {self.status_code}")
        logger.info(f"    IP : {self.ip_address} | UA : {self.user_agent}")
        logger.info(f"    Date : {self.date} {self.time.strftime('%H:%M:%S')} ({self.response_time_ms} ms)")
