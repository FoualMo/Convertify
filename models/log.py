from datetime import datetime
from . import db

class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Log {self.id}>"
