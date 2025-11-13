from datetime import date, timedelta
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user
from sqlalchemy import func
from models.user import RequestLog, User, APIKey
from models.db import db
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint("main", __name__)

# ===========================
# PAGES CLASSIQUES
# ===========================
@main.route("/")
def index():
    return render_template("index.html")

@main.route("/docs")
def docs():
    return render_template("api_docs.html")

@main.route("/contact")
def contact():
    return render_template("contact.html")

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/terms")
def terms():
    return render_template("terms.html")

@main.route("/privacy")
def privacy():
    return render_template("privacy.html")

@main.route("/compression")
def compression():
    return render_template("compress.html")

@main.route("/convertion")
def convertion():
    return render_template("convert.html")


# ===========================
# LOGIN
# ===========================
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and not user.is_active:
            flash("Votre compte est désactivé. Contactez l’administrateur.", "danger")
            return redirect(url_for("main.login"))
        if not user or not check_password_hash(user.password_hash, password):
            flash("Identifiants invalides", "login_error")
            return redirect(url_for('main.login'))

        login_user(user)
        return redirect(url_for('main.index'))

    # GET
    return render_template('login.html', register_active=False)


# ===========================
# REGISTER
# ===========================
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash("Email déjà utilisé", "register_error")
            return redirect(url_for('main.register'))

        user = User(
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Inscription réussie ! Vous pouvez vous connecter.", "register_success")
        return redirect(url_for('main.login'))

    # GET
    return render_template('login.html', register_active=True)

@main.route("/profil")
@login_required
def profil():
    # Statistiques pour admin uniquement
    stats = None
    users = []
    if current_user.is_admin:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        inactive_users = total_users - active_users
        total_keys = APIKey.query.count()
        requests_today = RequestLog.query.filter(RequestLog.date == date.today()).count()
        requests_7_days = (
            db.session.query(func.count(RequestLog.id))
            .filter(RequestLog.date >= date.today() - timedelta(days=7))
            .scalar()
        )

        # Top 5 endpoints les plus utilisés (uniquement /api/)
        top_endpoints = (
            db.session.query(RequestLog.endpoint, func.count(RequestLog.id))
            .filter(RequestLog.endpoint.like("/api/%"))   # ✅ uniquement les endpoints API
            .group_by(RequestLog.endpoint)
            .order_by(func.count(RequestLog.id).desc())
            .limit(5)
            .all()
        )

        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "total_keys": total_keys,
            "requests_today": requests_today,
            "requests_7_days": requests_7_days,
            "top_endpoints": top_endpoints
        }

        users = User.query.all()

    keys = APIKey.query.filter_by(user_id=current_user.id).all()

    return render_template("profile.html", stats=stats, keys=keys, users=users)