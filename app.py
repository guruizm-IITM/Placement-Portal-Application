from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Student, Company, Admin, PlacementDrive, Application, Placement
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):

    if '-' not in user_id:
        return None   # prevents crash

    role, id = user_id.split('-')
    id = int(id)

    if role == 'admin':
        return Admin.query.get(id)
    elif role == 'company':
        return Company.query.get(id)
    elif role == 'student':
        return Student.query.get(id)

    return None

@app.route('/')
def home():

    if current_user.is_authenticated:
        role = current_user.get_role()

        if role == "admin":
            return redirect(url_for('admin.admin_dashboard'))
        elif role == "company":
            return redirect(url_for('company.company_dashboard'))
        else:
            return redirect(url_for('student.student_dashboard'))

    return redirect(url_for('auth.login'))

auth = Blueprint('auth', __name__)

@auth.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )
        try:
            db.session.add(student)
            db.session.commit()
            flash("Student registered successfully")
        except IntegrityError:
            db.session.rollback()
            flash("Email already registered. Please login.")
            return redirect(url_for('auth.login'))
    return render_template('auth/register_student.html')



@auth.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        company = Company(
            name=request.form['name'],
            email=request.form['email'],
            hr_contact=request.form['hr_contact'],
            website=request.form['website'],
            password=generate_password_hash(request.form['password']),
            approval_status='Pending'
        )
        try:
            db.session.add(company)
            db.session.commit()
            flash("Company registered. Wait for approval.")
        except IntegrityError:
            db.session.rollback()
            flash("Company already registered.")
            return redirect(url_for('auth.login'))
    return render_template('auth/register_company.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email']
        password = request.form['password']

        user = (
            Admin.query.filter_by(username=email_or_username).first() or
            Student.query.filter_by(email=email_or_username).first() or
            Company.query.filter_by(email=email_or_username).first()
        )

        if user and check_password_hash(user.password, password):

            #Company approval check
            if isinstance(user, Company) and user.approval_status != 'Approved':
                flash("Company not approved yet")
                return redirect(url_for('auth.login'))
            # Student blacklist check
            if isinstance(user, Student) and user.is_blacklisted:
                flash("Access denied. Please contact admin.")
                return redirect(url_for('auth.login'))

            # Company blacklist check
            if isinstance(user, Company) and user.approval_status == "Blacklisted":
                flash("Access denied. Please contact admin.")
                return redirect(url_for('auth.login'))

            login_user(user)

            #Role-based redirect
            role = user.get_role()

            if role == "admin":
                return redirect(url_for('admin.admin_dashboard'))
            elif role == "company":
                return redirect(url_for('company.company_dashboard'))
            else:
                return redirect(url_for('student.student_dashboard'))

        flash("Invalid credentials")

    return render_template('auth/login.html')


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
def admin_dashboard():
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
        admin_user = Admin(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin_user)
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

@admin.route('/admin/drive/<int:id>/applications')
@login_required
@role_required('admin')
def admin_view_drive_applications(id):

    drive = PlacementDrive.query.get_or_404(id)
    applications = Application.query.filter_by(drive_id=id).all()

    return render_template(
        'admin/drive_applications.html',
        drive=drive,
        applications=applications
    )

@admin.route('/admin/search/students')
@login_required
@role_required('admin')
def search_students():
    query = request.args.get('q')

    if not query:
        return redirect(url_for('admin.view_students'))

    students = Student.query.filter(
        (Student.name.contains(query)) |
        (Student.email.contains(query)) |
        (Student.id == int(query) if query.isdigit() else False)
    ).all()

    return render_template('admin/students.html', students=students)

@admin.route('/admin/search/companies')
@login_required
@role_required('admin')
def search_companies():
    query = request.args.get('q')

    if not query:
        return redirect(url_for('admin.view_companies'))

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

@admin.route('/admin/placements')
@login_required
@role_required('admin')
def view_placements():

    placements = Placement.query.all()

    return render_template(
        'admin/placements.html',
        placements=placements
    )

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
def company_dashboard():

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
            application_deadline=datetime.strptime(request.form['deadline'], "%Y-%m-%d"),
            company_id=current_user.id,
            status='Pending'
        )

        db.session.add(drive)
        db.session.commit()

        return redirect(url_for('company.company_dashboard'))

    return render_template('company/create_drive.html')


@company.route('/company/drive/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('company')
def edit_drive(id):

    drive = PlacementDrive.query.get_or_404(id)

    # Ownership check
    if drive.company_id != current_user.id:
        return "Unauthorized"

    if request.method == 'POST':
        drive.job_title = request.form['title']
        drive.job_description = request.form['description']
        drive.eligibility = request.form['eligibility']
        drive.application_deadline = datetime.strptime(request.form['deadline'], "%Y-%m-%d")

        db.session.commit()

        return redirect(url_for('company.company_dashboard'))

    return render_template('company/edit_drive.html', drive=drive)


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

@company.route('/company/student/<int:id>')
@login_required
@role_required('company')
def view_student_profile(id):
    student = Student.query.get_or_404(id)
    return render_template('company/student_profile.html', student=student)


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

    if status not in STATUS_TRANSITIONS[current_status]:
        return "Invalid transition"

    application.status = status

    if status == "Placed":
        placement = Placement(
            student_id=application.student_id,
            drive_id=application.drive_id
        )
        db.session.add(placement)

    db.session.commit()

    return redirect(url_for('company.view_applications', id=application.drive_id))
    

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

@company.route('/company/drive/<int:id>/delete')
@login_required
@role_required('company')
def delete_drive(id):
    drive = PlacementDrive.query.get_or_404(id)

    if drive.company_id != current_user.id:
        return "Unauthorized"

    db.session.delete(drive)
    db.session.commit()

    return redirect(url_for('company.dashboard'))

@company.route('/company/profile', methods=['GET', 'POST'])
@login_required
@role_required('company')
def company_profile():

    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.email = request.form['email']
        current_user.hr_contact = request.form['hr_contact']
        current_user.website = request.form['website']

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Email already exists"

        flash("Profile updated successfully")
        return redirect(url_for('company.dashboard'))

    return render_template('company/profile.html')

student = Blueprint('student', __name__)

@student.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():

    drives = PlacementDrive.query.filter_by(status='Approved').all()

    applications = Application.query.filter_by(student_id=current_user.id).all()

    placements = Placement.query.filter_by(student_id=current_user.id).all()

    return render_template(
        'student/dashboard.html',
        drives=drives,
        applications=applications,
        placements=placements
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
    except IntegrityError:
        db.session.rollback()
        return "Already applied"

    return redirect(url_for('student.student_dashboard'))


@student.route('/student/profile', methods=['GET', 'POST'])
@login_required
@role_required('student')
def profile():

    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.skills = request.form['skills']
        current_user.resume = request.form['resume']

        db.session.commit()
        return redirect(url_for('student.student_dashboard'))

    return render_template('student/profile.html')

@student.route('/student/chart-data')
@login_required
@role_required('student')
def student_chart_data():

    applications = Application.query.filter_by(student_id=current_user.id).all()

    all_statuses = ["Applied", "Shortlisted", "Interview", "Selected", "Placed", "Rejected"]

    status_count = {status: 0 for status in all_statuses}

    for app in applications:
        status_count[app.status] += 1

    return {
        "labels": list(status_count.keys()),
        "values": list(status_count.values())
    }

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(company)
app.register_blueprint(student)

if __name__ == "__main__":
    app.run(debug=True)