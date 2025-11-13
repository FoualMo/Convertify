from datetime import date, datetime
import logging
import time
from flask import Flask, request, g
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash

from config.site_config import SiteConfig
from models.db import db  # ✅ import unique et cohérent
from models.user import User, APIKey, RequestLog


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'un_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # -------------------
    # Context global (site info)
    # -------------------
    @app.context_processor
    def inject_site_settings():
        return {"site": SiteConfig}

    # -------------------
    # Gestion login
    # -------------------
    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -------------------
    # Enregistrement des Blueprints
    # -------------------
    from routes.api.auth import auth_bp
    from routes.api.convert_routes import convert_bp
    from routes.api.compress_bp import compress_bp
    from routes.main_pages import main
    from routes.admin.dashboard import admin

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(convert_bp)
    app.register_blueprint(compress_bp)
    app.register_blueprint(main)
    app.register_blueprint(admin)

    # -------------------
    # Log automatique des requêtes
    # -------------------
    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        if current_user.is_authenticated and request.path.startswith("/api/"):
            if request.path in [r.rule for r in app.url_map.iter_rules()]:
                log = RequestLog(
                    user_id=current_user.id,
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string,
                    date=date.today(),
                    time=datetime.utcnow(),
                    response_time_ms=(time.time() - g.start_time) * 1000
                )
                db.session.add(log)
                db.session.commit()
        return response

    return app


app = create_app()
with app.app_context():
        db.create_all()

        # Création admin si absent
        if not User.query.filter_by(email="admin@example.com").first():
            admin = User(
                email="admin@example.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin ajouté", flush=True)
# -------------------------------------------------
# Lancement direct (et création de la base si besoin)
# -------------------------------------------------
# -------------------
# Lancement app
# -------------------
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()

        # Création admin si absent
        if not User.query.filter_by(email="admin@example.com").first():
            admin = User(
                email="admin@example.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin ajouté", flush=True)

    app.run(debug=True)

