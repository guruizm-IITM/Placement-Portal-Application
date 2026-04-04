# Placement Portal – MAD-1 Project

A role-based placement management web application built using Flask, SQLite, Jinja2, and Bootstrap.  
This project is developed as part of the MAD-1 course requirements.

## 🚀 Objective
To build a simple and functional placement portal that supports:
- Admin management
- Company registration & drive creation
- Student applications & tracking

The system demonstrates role-based access, CRUD workflows, and backend-driven logic using Flask.

## 🧰 Tech Stack
- Backend: Flask
- Database: SQLite
- ORM: SQLAlchemy
- Frontend: HTML, CSS, Bootstrap, Jinja2
- Authentication: Flask-Login

## 👥 User Roles
### Admin
- Approve/reject companies
- Approve placement drives
- View all users and applications

### Company
- Register and get approval
- Create placement drives
- View applicants and update status

### Student
- Register/login
- View approved drives
- Apply to drives
- Track application status

## 📁 Project Structure (planned)

## Project Structure

```
Placement_Portal_App/
│
├── app.py
├── config.py
├── models.py
├── routes/
│   ├── auth.py
│   ├── admin.py
│   ├── company.py
│   └── student.py
│
├── templates/
├── static/


## ⚙️ Current Status
Initial setup phase:
- Repository initialization
- Documentation drafting
- Architecture planning

## 📌 Next Steps
- Define database schema
- Implement authentication
- Build role dashboards
- Add application workflow

## 🎓 Academic Note
This is a coursework project focused on backend logic, system design, and role-based workflows rather than production deployment.

---
More details and setup instructions will be added as development progresses.
