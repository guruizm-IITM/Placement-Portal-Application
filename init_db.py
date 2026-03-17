from app import app
from models import db, User, Drive, Application
from sqlalchemy import inspect

with app.app_context():
    db.create_all()

    inspector = inspect(db.engine)
    print("Tables created:", inspector.get_table_names())