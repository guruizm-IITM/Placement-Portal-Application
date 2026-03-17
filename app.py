from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from models import db, User
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
    return render_template("base.html")


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

    return render_template("admin/dashboard.html")


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

    return render_template("company/dashboard.html")


#LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)