from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models ici pour que SQLAlchemy les détecte
from .user import User
from .log import Log
