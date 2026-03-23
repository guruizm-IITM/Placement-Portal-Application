from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from models import db, User, Drive, Application
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("home.html")


#REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        # Approval logic
        is_approved = True if role == "student" else False

        user = User(
            name=name,
            email=email,
            password=password,
            role=role,
            is_approved=is_approved
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


#LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            if not user.is_approved:
                flash("Your account is pending approval.")
                return redirect(url_for("login"))

            login_user(user)
            flash("Login successful")

            return redirect(url_for("dashboard"))

        flash("Invalid credentials")

    return render_template("login.html")


#DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))

    elif current_user.role == "student":
        return redirect(url_for("student_dashboard"))

    elif current_user.role == "company":
        return redirect(url_for("company_dashboard"))

    return "Invalid role"

#ADMIN DASHBOARD
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Unauthorized", 403

    total_students = User.query.filter_by(role="student").count()
    total_companies = User.query.filter_by(role="company").count()
    total_drives = Drive.query.count()
    total_applications = Application.query.count()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications
    )


#STUDENT DASHBOARD
@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        return "Unauthorized", 403

    return render_template("student/dashboard.html")


#COMPANY DASHBOARD
@app.route("/company/dashboard")
@login_required
def company_dashboard():
    if current_user.role != "company":
        return "Unauthorized", 403

    drives = Drive.query.filter_by(company_id=current_user.id).all()

    drive_data = []

    for drive in drives:
        applicant_count = Application.query.filter_by(drive_id=drive.id).count()

        drive_data.append({
            "drive": drive,
            "count": applicant_count
        })

    return render_template(
        "company/dashboard.html",
        drive_data=drive_data
    )


#LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("login"))


@app.route("/admin/companies")
@login_required
def view_companies():
    if current_user.role != "admin":
        return "Unauthorized", 403

    companies = User.query.filter_by(role="company", is_approved=False).all()

    return render_template("admin/companies.html", companies=companies)

@app.route("/admin/approve_company/<int:user_id>")
@login_required
def approve_company(user_id):
    if current_user.role != "admin":
        return "Unauthorized", 403

    company = User.query.get(user_id)
    company.is_approved = True
    db.session.commit()

    return redirect(url_for("view_companies"))


@app.route("/admin/delete_company/<int:user_id>")
@login_required
def delete_company(user_id):
    if current_user.role != "admin":
        return "Unauthorized", 403

    company = User.query.get(user_id)
    db.session.delete(company)
    db.session.commit()

    return redirect(url_for("view_companies"))

from datetime import datetime

@app.route("/company/create_drive", methods=["GET", "POST"])
@login_required
def create_drive():
    if current_user.role != "company":
        return "Unauthorized", 403

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        date = request.form["date"]

        drive = Drive(
            title=title,
            description=description,
            date=date,
            company_id=current_user.id,
            is_approved=False
        )

        db.session.add(drive)
        db.session.commit()

        return redirect(url_for("company_dashboard"))

    return render_template("company/create_drive.html")


@app.route("/student/drives")
@login_required
def view_drives():
    if current_user.role != "student":
        return "Unauthorized", 403

    drives = Drive.query.filter_by(is_approved=True).all()

    return render_template("student/drives.html", drives=drives)

@app.route("/student/apply/<int:drive_id>")
@login_required
def apply_drive(drive_id):
    if current_user.role != "student":
        return "Unauthorized", 403

    existing = Application.query.filter_by(
        student_id=current_user.id,
        drive_id=drive_id
    ).first()

    if existing:
        return "Already applied"

    application = Application(
        student_id=current_user.id,
        drive_id=drive_id,
        status="applied",
        applied_at=datetime.utcnow()
    )

    db.session.add(application)
    db.session.commit()

    return redirect(url_for("view_drives"))

@app.route("/admin/drives")
@login_required
def view_drives_admin():
    if current_user.role != "admin":
        return "Unauthorized", 403

    drives = Drive.query.filter_by(is_approved=False).all()

    return render_template("admin/drives.html", drives=drives)


@app.route("/admin/approve_drive/<int:drive_id>")
@login_required
def approve_drive(drive_id):
    if current_user.role != "admin":
        return "Unauthorized", 403

    drive = Drive.query.get(drive_id)
    drive.is_approved = True
    db.session.commit()

    return redirect(url_for("view_drives_admin"))


@app.route("/company/applicants/<int:drive_id>")
@login_required
def view_applicants(drive_id):
    if current_user.role != "company":
        return "Unauthorized", 403

    applications = Application.query.filter_by(drive_id=drive_id).all()

    return render_template("company/applicants.html", applications=applications)


@app.route("/company/update_status/<int:app_id>/<status>")
@login_required
def update_status(app_id, status):
    if current_user.role != "company":
        return "Unauthorized", 403

    application = Application.query.get(app_id)
    application.status = status
    db.session.commit()

    return redirect(request.referrer)


@app.route("/company/drives")
@login_required
def company_drives():
    if current_user.role != "company":
        return "Unauthorized", 403

    drives = Drive.query.filter_by(company_id=current_user.id).all()

    return render_template("company/drives.html", drives=drives)

@app.route("/student/applications")
@login_required
def student_applications():
    if current_user.role != "student":
        return "Unauthorized", 403

    applications = Application.query.filter_by(student_id=current_user.id).all()

    return render_template("student/applications.html", applications=applications)

@app.route("/admin/applications")
@login_required
def admin_applications():
    if current_user.role != "admin":
        return "Unauthorized", 403

    applications = Application.query.all()

    return render_template("admin/applications.html", applications=applications)


if __name__ == "__main__":
    app.run(debug=True)