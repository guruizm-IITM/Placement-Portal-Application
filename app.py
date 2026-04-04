from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Student, Company, Admin
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from utils import role_required

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return (
        Admin.query.get(int(user_id)) or
        Company.query.get(int(user_id)) or
        Student.query.get(int(user_id))
    )

with app.app_context():
    db.create_all()


auth = Blueprint('auth', __name__)

@auth.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(student)
        db.session.commit()
        flash("Student registered successfully")
        return redirect(url_for('auth.login'))
    return render_template('register_student.html')



@auth.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        company = Company(
            name=request.form['name'],
            hr_contact=request.form['hr_contact'],
            website=request.form['website'],
            password=generate_password_hash(request.form['password']),
            approval_status='Pending'
        )
        db.session.add(company)
        db.session.commit()
        flash("Company registered. Wait for admin approval.")
        return redirect(url_for('auth.login'))
    return render_template('register_company.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email']
        password = request.form['password']

        user = (
            Admin.query.filter_by(username=email_or_username).first() or
            Student.query.filter_by(email=email_or_username).first() or
            Company.query.filter_by(name=email_or_username).first()
        )

        if user and check_password_hash(user.password, password):

            #Company approval check
            if isinstance(user, Company) and user.approval_status != 'Approved':
                flash("Company not approved yet")
                return redirect(url_for('auth.login'))

            login_user(user)

            #Role-based redirect
            role = user.get_role()

            if role == "admin":
                return redirect(url_for('admin.dashboard'))
            elif role == "company":
                return redirect(url_for('company.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))

        flash("Invalid credentials")

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.get_role() != role:
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator


admin = Blueprint('admin', __name__)

@admin.route('/admin/dashboard')
@login_required
@role_required('admin')
def dashboard():
    return "Admin Dashboard"

with app.app_context():
    db.create_all()

    if not Admin.query.first():
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)