from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Student, Company, Admin, PlacementDrive, Application, Placement
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
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    return render_template(
        'admin/dashboard.html',
        students=total_students,
        companies=total_companies,
        drives=total_drives,
        applications=total_applications
    )

with app.app_context():
    db.create_all()

    if not Admin.query.first():
        admin = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()

@admin.route('/admin/company/<int:id>/approve')
@login_required
@role_required('admin')
def approve_company(id):
    company = Company.query.get_or_404(id)
    company.approval_status = 'Approved'
    db.session.commit()
    return redirect(url_for('admin.view_companies'))

@admin.route('/admin/company/<int:id>/reject')
@login_required
@role_required('admin')
def reject_company(id):
    company = Company.query.get_or_404(id)
    company.approval_status = 'Rejected'
    db.session.commit()
    return redirect(url_for('admin.view_companies'))

@admin.route('/admin/companies')
@login_required
@role_required('admin')
def view_companies():
    companies = Company.query.all()
    return render_template('admin/companies.html', companies=companies)

@admin.route('/admin/students')
@login_required
@role_required('admin')
def view_students():
    students = Student.query.all()
    return render_template('admin/students.html', students=students)

@admin.route('/admin/drive/<int:id>/approve')
@login_required
@role_required('admin')
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Approved'
    db.session.commit()
    return redirect(url_for('admin.view_drives'))

@admin.route('/admin/drive/<int:id>/reject')
@login_required
@role_required('admin')
def reject_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('admin.view_drives'))

@admin.route('/admin/drives')
@login_required
@role_required('admin')
def view_drives():
    drives = PlacementDrive.query.all()
    return render_template('admin/drives.html', drives=drives)

@admin.route('/admin/applications')
@login_required
@role_required('admin')
def view_applications():
    applications = Application.query.all()
    return render_template('admin/applications.html', applications=applications)

@admin.route('/admin/search/students')
@login_required
@role_required('admin')
def search_students():
    query = request.args.get('q')
    students = Student.query.filter(
        Student.name.contains(query) |
        Student.email.contains(query)
    ).all()

    return render_template('admin/students.html', students=students)

@admin.route('/admin/search/companies')
@login_required
@role_required('admin')
def search_companies():
    query = request.args.get('q')
    companies = Company.query.filter(
        Company.name.contains(query)
    ).all()

    return render_template('admin/companies.html', companies=companies)

@admin.route('/admin/student/<int:id>/blacklist')
@login_required
@role_required('admin')
def blacklist_student(id):
    student = Student.query.get_or_404(id)
    student.is_blacklisted = True
    db.session.commit()
    return redirect(url_for('admin.view_students'))

@admin.route('/admin/company/<int:id>/blacklist')
@login_required
@role_required('admin')
def blacklist_company(id):
    company = Company.query.get_or_404(id)
    company.approval_status = 'Blacklisted'
    db.session.commit()
    return redirect(url_for('admin.view_companies'))

@admin.route('/admin/chart-data')
@login_required
@role_required('admin')
def admin_chart_data():

    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    total_placements = Placement.query.count()

    return {
        "labels": ["Drives", "Applications", "Placements"],
        "values": [total_drives, total_applications, total_placements]
    }


company = Blueprint('company', __name__)

@company.route('/company/dashboard')
@login_required
@role_required('company')
def dashboard():

    if current_user.approval_status != 'Approved':
        return "Access Denied. Await admin approval."

    drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()

    return render_template('company/dashboard.html', drives=drives)

@company.route('/company/drive/create', methods=['GET', 'POST'])
@login_required
@role_required('company')
def create_drive():

    if current_user.approval_status != 'Approved':
        return "Not authorized"

    if request.method == 'POST':
        drive = PlacementDrive(
            job_title=request.form['title'],
            job_description=request.form['description'],
            eligibility=request.form['eligibility'],
            application_deadline=request.form['deadline'],
            company_id=current_user.id
        )

        db.session.add(drive)
        db.session.commit()

        return redirect(url_for('company.dashboard'))

    return render_template('company/create_drive.html')


@company.route('/company/drive/<int:id>/close')
@login_required
@role_required('company')
def close_drive(id):
    drive = PlacementDrive.query.get_or_404(id)

    if drive.company_id != current_user.id:
        return "Unauthorized"

    drive.status = 'Closed'
    db.session.commit()

    return redirect(url_for('company.dashboard'))


@company.route('/company/drive/<int:id>/applications')
@login_required
@role_required('company')
def view_applications(id):
    drive = PlacementDrive.query.get_or_404(id)

    if drive.company_id != current_user.id:
        return "Unauthorized"

    applications = Application.query.filter_by(drive_id=id).all()

    return render_template(
        'company/applications.html',
        applications=applications,
        drive=drive
    )


VALID_STATUSES = {
    "Applied",
    "Shortlisted",
    "Interview",
    "Selected",
    "Rejected",
    "Placed"
}

STATUS_TRANSITIONS = {
    "Applied": ["Shortlisted", "Rejected"],
    "Shortlisted": ["Interview", "Rejected"],
    "Interview": ["Selected", "Rejected"],
    "Selected": ["Placed"],
    "Placed": [],
    "Rejected": []
}

@company.route('/company/application/<int:id>/update/<status>')
@login_required
@role_required('company')
def update_application_status(id, status):

    application = Application.query.get_or_404(id)

    if application.drive.company_id != current_user.id:
        return "Unauthorized"

    current_status = application.status

    if status not in VALID_STATUSES:
        return "Invalid status"
    

@company.route('/company/chart-data')
@login_required
@role_required('company')
def company_chart_data():

    drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()

    labels = []
    values = []

    for drive in drives:
        labels.append(drive.job_title)
        values.append(len(drive.applications))

    return {
        "labels": labels,
        "values": values
    }

student = Blueprint('student', __name__)

@student.route('/student/dashboard')
@login_required
@role_required('student')
def dashboard():

    drives = PlacementDrive.query.filter_by(status='Approved').all()

    applications = Application.query.filter_by(student_id=current_user.id).all()

    return render_template(
        'student/dashboard.html',
        drives=drives,
        applications=applications
    )


@student.route('/student/search')
@login_required
@role_required('student')
def search_drives():
    query = request.args.get('q')

    drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'Approved',
        PlacementDrive.job_title.contains(query)
    ).all()

    return render_template('student/dashboard.html', drives=drives)


@student.route('/student/apply/<int:drive_id>')
@login_required
@role_required('student')
def apply_job(drive_id):

    # Prevent blacklisted students
    if current_user.is_blacklisted:
        return "You are not allowed to apply"

    application = Application(
        student_id=current_user.id,
        drive_id=drive_id
    )

    try:
        db.session.add(application)
        db.session.commit()
    except:
        return "Already applied"

    return redirect(url_for('student.dashboard'))


@student.route('/student/apply/<int:drive_id>')
@login_required
@role_required('student')
def apply_job(drive_id):

    # Prevent blacklisted students
    if current_user.is_blacklisted:
        return "You are not allowed to apply"

    application = Application(
        student_id=current_user.id,
        drive_id=drive_id
    )

    try:
        db.session.add(application)
        db.session.commit()
    except:
        return "Already applied"

    return redirect(url_for('student.dashboard'))

@student.route('/student/profile', methods=['GET', 'POST'])
@login_required
@role_required('student')
def profile():

    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.skills = request.form['skills']

        db.session.commit()
        return redirect(url_for('student.dashboard'))

    return render_template('student/profile.html')

@student.route('/student/chart-data')
@login_required
@role_required('student')
def student_chart_data():

    applications = Application.query.filter_by(student_id=current_user.id).all()

    status_count = {}

    for app in applications:
        status_count[app.status] = status_count.get(app.status, 0) + 1

    return {
        "labels": list(status_count.keys()),
        "values": list(status_count.values())
    }


if __name__ == "__main__":
    app.run(debug=True)