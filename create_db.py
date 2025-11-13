from datetime import datetime
from app import create_app
from models.db import db
from werkzeug.security import generate_password_hash
from models.user import User

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tables créées !")

    # Ajouter un admin de test
    if not User.query.filter_by(email="admin@example.com").first():
        admin = User(
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
            last_login_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin ajouté !")

