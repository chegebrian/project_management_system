# 🏢 Property Management System

A **Flask-based Property Management System** designed to help landlords
and property managers manage properties, rental units, tenants, and
payments efficiently.

---

# 📌 Project Overview

Managing rental properties manually can be inefficient and prone to
errors. This system digitizes property management by allowing
administrators to:

- Manage multiple properties
- Track units within properties
- Register and manage tenants
- Record and monitor rent payments
- Authenticate users securely

The application is built using **Flask**, **SQLAlchemy**, and
**Flask-Login**, following a modular architecture.

---

# 🚀 Features

## 👤 User Authentication

- User registration
- Secure login/logout
- Session management with Flask-Login
- Password hashing

## 🏠 Property Management

- Create new properties
- Update property details
- View all properties

## 🏢 Unit Management

- Add rental units under properties
- Track unit availability
- Assign units to tenants

## 🧑‍💼 Tenant Management

- Register tenants
- Link tenants to rental units
- View tenant information

## 💰 Payment Tracking

- Record rent payments
- Track payment history
- Associate payments with tenants

---

# 🛠️ Technologies Used

Technology Purpose

---

Python Programming language
Flask Web framework
SQLAlchemy ORM for database
Flask-Login Authentication
Flask-WTF Form handling
SQLite Database
Jinja2 HTML templating

---

# 📂 Project Structure

    property-management-system/
    │
    ├── app.py
    ├── config.py
    ├── forms.py
    ├── models.py
    ├── Pipfile
    ├── database.db
    │
    ├── templates/
    │   ├── base.html
    │   ├── login.html
    │   ├── register.html
    │   └── dashboard.html
    │
    │
    └── venv/

---

# 🗄️ Database Models

## User

Represents system users.

Fields: - id - username - email - password_hash

## Property

Fields: - id - name - location - description

Relationship: - One property has many units

## Unit

Fields: - id - property_id - unit_number - rent_amount - status

Relationship: - Belongs to a property

## Tenant

Fields: - id - name - phone - email - unit_id

Relationship: - Tenant occupies a unit

## Payment

Fields: - id - tenant_id - amount - payment_date

Relationship: - Payment belongs to tenant

---

# ⚙️ Installation Guide

## 1️⃣ Clone Repository

    git clone https://github.com/yourusername/property-management-system.git
    cd property-management-system

## 2️⃣ Create Virtual Environment

    python3 -m venv venv

Activate environment

Linux / Mac

    source venv/bin/activate

Windows

    venv\Scripts\activate

## 3️⃣ Install Dependencies

    pip install flask flask-login flask-wtf sqlalchemy

## 4️⃣ Run Application

    flask run

or

    python app.py

Open browser:

    http://127.0.0.1:5000

---

# 📊 Example Workflow

1.  User registers
2.  User logs in
3.  Create property
4.  Add units
5.  Register tenants
6.  Record rent payments

---

# 🔐 Authentication

Routes that require login are protected using:

    @login_required

---

# 📡 Routes

Route Description

---

/register Register new user
/login Login
/logout Logout
/properties View properties
/units Manage units
/tenants Manage tenants
/payments Track payments

---

# 📸 Screenshots

Add screenshots of:

- Login page
- Dashboard
- Property management page
- Tenant records

Example:

    ![Dashboard](screenshots/dashboard.png)

---

# 🌍 Deployment

You can deploy this project using:

- Render
- Railway
- Heroku
- DigitalOcean

Example Render steps:

1.  Push project to GitHub
2.  Connect GitHub to Render
3.  Select **Web Service**
4.  Add environment variables
5.  Deploy

---

# 🧪 Future Improvements

- Role-based authentication (Admin / Manager)
- REST API
- M-Pesa payment integration
- Email notifications
- Analytics dashboard

---

# 🤝 Contributing

Steps:

    Fork repository
    Create feature branch
    git checkout -b feature-name

    Commit changes
    git commit -m "Add feature"

    Push branch
    git push origin feature-name

Open a Pull Request.

---

# 📜 License

MIT License

---
