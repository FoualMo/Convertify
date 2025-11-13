from datetime import date, timedelta
import secrets
import time
import psutil
import platform
from flask import Blueprint, Response, flash, redirect, render_template, jsonify, abort, request, url_for
from flask_login import login_required, current_user
from functools import wraps

from sqlalchemy import func

from models.db import db
from models.user import APIKey, RequestLog, User
from utils.decorators import require_admin

# =========================
# Blueprint admin
# =========================
admin = Blueprint("admin", __name__, url_prefix="/admin")

# =========================
# Monitoring page HTML
# =========================
@admin.route("/monitoring")
@login_required
#@require_admin
def monitoring():
    return render_template("monitoring.html")

# =========================
# Cleaner page HTML
# =========================
@admin.route("/cleaner_status")
@login_required
@require_admin
def cleaner_status():
    return render_template("admin/cleaner_status.html")

# =========================
# Metrics API pour JS
# =========================
@admin.route("/metrics")
@login_required
#@require_admin
def metrics():
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        uptime_seconds = int(time.time() - psutil.boot_time())

        # Si tu veux suivre le nombre de requêtes, tu peux le mettre ici
        requests_count = 0

        data = {
            "timestamp": time.time(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_usage_percent": disk_percent,
                "platform": platform.system(),
                "platform_version": platform.version()
            },
            "requests": requests_count,
            "uptime_seconds": uptime_seconds
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# Dashboard Pro
# =========================
@admin.route("/pro_dashboard", methods=["GET", "POST"])
@login_required
@require_admin
def pro_dashboard():
    # POST → création nouvelle clé
    if request.method == "POST":
        email = request.form.get("email")
        daily_limit = int(request.form.get("daily_limit", 100))
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Utilisateur non trouvé", "danger")
            return redirect(url_for("admin.pro_dashboard"))
        # Générer clé aléatoire
        api_key = secrets.token_hex(16)
        key = APIKey(user_id=user.id, api_key=api_key, daily_limit=daily_limit)
        db.session.add(key)
        db.session.commit()
        flash(f"Clé API créée pour {email}", "success")
        return redirect(url_for("admin.pro_dashboard"))

    # GET → afficher le dashboard
    search_email = request.args.get("search_email", "")
    status_filter = request.args.get("status_filter", "")

    keys_query = APIKey.query.join(User).add_columns(User.email).order_by(APIKey.created_at.desc())
    if search_email:
        keys_query = keys_query.filter(User.email.ilike(f"%{search_email}%"))
    if status_filter == "active":
        keys_query = keys_query.filter(APIKey.revoked == False)
    elif status_filter == "revoked":
        keys_query = keys_query.filter(APIKey.revoked == True)

    keys = []
    for key_obj, email in keys_query.all():
        keys.append({
            "id": key_obj.id,
            "email": email,
            "api_key": key_obj.api_key,
            "created_at_fmt": key_obj.created_at.strftime("%Y-%m-%d %H:%M"),
            "daily_limit": key_obj.daily_limit,
            "revoked": key_obj.revoked,
            "today_usage": key_obj.today_usage
        })

    users = [u.email for u in User.query.order_by(User.email).all()]

    return render_template("pro_dashboard.html", keys=keys, users=users)

# =========================
# Révoquer une clé
# =========================
@admin.route("/pro_revoke/<key>", methods=["POST"])
@login_required
@require_admin
def pro_revoke(key):
    api_key = APIKey.query.filter_by(api_key=key).first_or_404()
    api_key.revoked = True
    db.session.commit()
    flash("Clé révoquée", "success")
    return redirect(url_for("admin.pro_dashboard"))

# =========================
# Modifier le quota journalier
# =========================
@admin.route("/update_quota/<key>", methods=["POST"])
@login_required
@require_admin
def update_quota(key):
    daily_limit = int(request.form.get("daily_limit", 100))
    api_key = APIKey.query.filter_by(api_key=key).first_or_404()
    api_key.daily_limit = daily_limit
    db.session.commit()
    flash("Quota mis à jour", "success")
    return redirect(url_for("admin.pro_dashboard"))

@admin.route("/export_keys_csv")
@require_admin
def export_keys_csv():
    from models import APIKey  # ou depuis ton fichier models
    keys = APIKey.query.all()

    def generate():
        yield "ID,Email,API Key,Created At,Daily Limit,Revoked\n"
        for key in keys:
            yield f"{key.id},{key.user.email},{key.api_key},{key.created_at},{key.daily_limit},{key.revoked}\n"

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=api_keys.csv"})


# =========================
# Dashboard principal
# =========================

@admin.route("/", methods=["GET"])
@require_admin
def dashboard():
    # GET : afficher le dashboard
    users = [u.email for u in User.query.all()]
    keys = APIKey.query.all()
    return render_template("pro_dashboard.html", users=users, keys=keys)

@admin.route("/createkey", methods=["POST"])
@login_required
@require_admin
def create_key():
    email = request.form.get("email")
    daily_limit = int(request.form.get("daily_limit", 100))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Utilisateur non trouvé", "danger")
        return redirect(url_for("admin.dashboard"))

    # Générer clé aléatoire
    api_key = secrets.token_hex(16)
    key = APIKey(user_id=user.id, api_key=api_key, daily_limit=daily_limit)
    db.session.add(key)
    db.session.commit()

    flash(f"Nouvelle clé API générée pour {email}", "success")
    return redirect(url_for("admin.dashboard"))


# -----------------------------------
# ✅ LISTE DES UTILISATEURS
# -----------------------------------
@admin.route("/users")
@login_required
@require_admin
def users():
    # ✅ Paramètres GET
    search_email = request.args.get("search_email", "").strip()
    role_filter = request.args.get("role_filter", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 10

    # ✅ Base Query
    query = User.query

    # Filtrer par email
    if search_email:
        query = query.filter(User.email.ilike(f"%{search_email}%"))

    # Filtrer par rôle (admin / user)
    if role_filter == "admin":
        query = query.filter(User.is_admin.is_(True))
    elif role_filter == "user":
        query = query.filter(User.is_admin.is_(False))

    # ✅ Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    return render_template(
        "admin/users.html",
        users=users,
        pagination=pagination,
        search_email=search_email,
        role_filter=role_filter
    )

# -----------------------------------
# ✅ MODIFIER RÔLE USER
# -----------------------------------
@admin.route("/users/<int:user_id>/role", methods=["POST"])
@login_required
@require_admin
def update_role(user_id):

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin

    db.session.commit()
    flash("Rôle mis à jour ✅", "success")

    return redirect(url_for("admin.users"))

# -----------------------------------
# affichage profil d'un user coté admin
# -----------------------------------
@admin.route("/users/<int:user_id>", methods=["GET"])
@login_required
@require_admin
def user_profil(user_id):
    user = User.query.get_or_404(user_id)
    keys = APIKey.query.filter_by(user_id=user.id).all()

    total_calls = sum(k.today_usage + getattr(k, "total_usage", 0) for k in keys)
    today_calls = sum(k.today_usage for k in keys)

    recent_logs = RequestLog.query.filter_by(user_id=user.id).order_by(RequestLog.date.desc()).limit(10).all()

    # Affichage debug
    print(f"Affichage du profil utilisateur : {user.last_login_at} (ID: {user.id})")

    return render_template(
        "admin/user_profil.html",
        user=user,
        keys=keys,
        total_calls=total_calls,
        today_calls=today_calls,
        recent_logs=recent_logs
    )
# -----------------------------------
# ✅ SUPPRIMER USER
# -----------------------------------
@admin.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@require_admin
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash("Utilisateur supprimé ✅", "success")

    return redirect(url_for("admin.users"))

@admin.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@require_admin
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)

    # ✅ Inversion active/inactive
    user.is_active = not user.is_active

    db.session.commit()

    if user.is_active:
        flash("Utilisateur réactivé ✅", "success")
    else:
        flash("Utilisateur désactivé ✅", "warning")

    return redirect(url_for("admin.users"))


@admin.route("/users_data")
@login_required
@require_admin
def users_data():
    search_email = request.args.get("search_email", "").strip()
    role_filter = request.args.get("role_filter", "").strip()

    query = User.query

    if search_email:
        query = query.filter(User.email.ilike(f"%{search_email}%"))

    if role_filter:
        if role_filter == "admin":
            query = query.filter(User.is_admin.is_(True))
        elif role_filter == "user":
            query = query.filter(User.is_admin.is_(False))

    users = query.order_by(User.id.asc()).all()

    data = [
        {
            "id": u.id,
            "email": u.email,
            "role": "admin" if u.is_admin else "user",
            "is_active": u.is_active
        }
        for u in users
    ]

    return jsonify(data)


@admin.route("/requests_stats")
@login_required
@require_admin
def get_request_stats():
    start_date = date.today() - timedelta(days=6)

    results = (
        RequestLog.query
        .filter(
            RequestLog.date >= start_date,
            RequestLog.endpoint.like("/api/%")
        )
        .with_entities(RequestLog.date, func.count(RequestLog.id))
        .group_by(RequestLog.date)
        .order_by(RequestLog.date)
        .all()
    )

    dates = [start_date + timedelta(days=i) for i in range(7)]
    counts = [next((r[1] for r in results if r[0] == d), 0) for d in dates]

    return jsonify({
        "dates": [d.strftime("%d/%m") for d in dates],
        "counts": counts
    })
