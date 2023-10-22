from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    Migrate(app, db)
