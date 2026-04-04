from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    def get_role(self):
        return "admin"

class Company(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(150))
    website = db.Column(db.String(200))
    password = db.Column(db.String(200), nullable=False)

    approval_status = db.Column(db.String(50), default='Pending')  

    placement_drives = db.relationship('PlacementDrive', backref='company', lazy=True)
    def get_role(self):
        return "company"

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    resume = db.Column(db.String(200))
    skills = db.Column(db.Text)

    is_blacklisted = db.Column(db.Boolean, default=False)

    applications = db.relationship('Application', backref='student', lazy=True)
    def get_role(self):
        return "student"

class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    eligibility = db.Column(db.Text)

    application_deadline = db.Column(db.DateTime)

    status = db.Column(db.String(50), default='Pending')

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    applications = db.relationship('Application', backref='drive', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    application_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    status = db.Column(db.String(50), default='Applied')
    # Applied / Shortlisted / Selected / Rejected

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),)


class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)

    offer_letter = db.Column(db.String(200))
    joining_date = db.Column(db.DateTime)
    student = db.relationship('Student')
    drive = db.relationship('PlacementDrive')