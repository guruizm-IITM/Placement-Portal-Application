# 🎓 Placement Portal Management System

A comprehensive web-based placement management system developed using Flask. This application streamlines the recruitment process by connecting students, companies, and the institute’s placement cell through a centralized platform.

---

## 📌 Project Overview

The **Placement Portal Management System** enables seamless coordination between students, recruiters, and administrators. It allows companies to post job opportunities, students to apply for them, and administrators to oversee and manage the entire placement lifecycle.

This project was developed as part of the **Modern Application Development (MAD-1)** coursework at IIT Madras.

---

## 🚀 Features

### 🔐 Authentication & Role-Based Access Control
- Secure login system using Flask-Login.
- Separate dashboards for Admin, Company, and Student.
- Password hashing using Werkzeug.
- Role-based access control and session management.

### 👨‍💼 Admin Functionalities
- View dashboard statistics:
  - Total Students
  - Total Companies
  - Total Placement Drives
  - Total Applications
  - Total Placements
- Approve or reject company registrations.
- Approve or reject placement drives.
- View all placement drives and applications.
- View historical placement data.
- Search students and companies.
- Blacklist or deactivate students and companies.

### 🏢 Company Functionalities
- Register and create a company profile.
- Access dashboard only after admin approval.
- Create, edit, delete, and close placement drives.
- View student applications and profiles.
- Update application statuses:
  - Applied
  - Shortlisted
  - Interview
  - Selected
  - Rejected
  - Placed
- Visualize application trends using charts.
- Edit company profile.

### 🎓 Student Functionalities
- Self-registration and login.
- Update profile and resume details.
- View approved placement drives.
- Apply for jobs and track application status.
- View placement history.
- Visualize analytics using charts.
- Edit student profile.

### 📊 Data Visualization
- Interactive charts using **Chart.js**:
  - Admin: System-wide analytics.
  - Company: Applications per job posting.
  - Student: Application status distribution.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Flask | Backend web framework |
| SQLAlchemy | Object Relational Mapper (ORM) |
| Flask-Login | Authentication and session management |
| Jinja2 | Template engine |
| SQLite | Lightweight database |
| Chart.js | Data visualization |
| HTML5 | Frontend structure |
| CSS3 | Styling and layout |
| Werkzeug | Password hashing and security |

---

## 📂 Project Structure

```
placement_portal_app/
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── instance/
│ └── placement.db
│
├── templates/
│ ├── base.html
│ │
│ ├── auth/
│ │ ├── login.html
│ │ ├── register_student.html
│ │ └── register_company.html
│ │
│ ├── admin/
│ │ ├── dashboard.html
│ │ ├── companies.html
│ │ ├── students.html
│ │ ├── drives.html
│ │ ├── drive_applications.html
│ │ └── placements.html
│ │
│ ├── company/
│ │ ├── dashboard.html
│ │ ├── create_drive.html
│ │ ├── edit_drive.html
│ │ ├── applications.html
│ │ └── profile.html
│ │
│ └── student/
│ ├── dashboard.html
│ └── profile.html

```
---

## 🗄️ Database Schema

### Entities
- **Admin**
- **Company**
- **Student**
- **PlacementDrive**
- **Application**
- **Placement**

### Relationships
- Company → PlacementDrive (One-to-Many)
- Student → Application (One-to-Many)
- PlacementDrive → Application (One-to-Many)
- Student → Placement (One-to-Many)
- PlacementDrive → Placement (One-to-Many)

You can generate the ER diagram using **dbdiagram.io**.

---

### 📊 Core Functionalities Implemented
✔ Authentication and Authorization
✔ Role-Based Access Control
✔ Company Approval Workflow
✔ Placement Drive Management
✔ Job Application Tracking
✔ Placement History Management
✔ Data Visualization with Charts
✔ Duplicate Application Prevention
✔ Search and Blacklisting Features
✔ Profile Management for Students and Companies