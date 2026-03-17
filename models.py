from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)  
    # admin / student / company

    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    company_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(50))

    is_approved = db.Column(db.Boolean, default=False)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'))

    status = db.Column(db.String(20), default="applied")
    applied_at = db.Column(db.DateTime)