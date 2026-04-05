# 💰 Finance Dashboard System

A full-stack **Finance Dashboard Web Application** built using Flask that supports user management, financial tracking, role-based access control, and analytical insights.

---

## 🚀 Features

* 👥 User & Role Management
* 💰 Financial Records Management
* 📊 Dashboard Summary & Insights
* 🔐 Role-Based Access Control
* 🔔 Flash Messages (auto fade + dismiss)
* 📱 Fully Responsive UI

---

## 🧩 Core Functionalities

### 1️⃣ User and Role Management

The system provides a structured way to manage users and their access levels.

#### ✅ Backend Capabilities:

* Create and manage users
* Assign roles to users
* Manage user status (Active / Inactive)
* Restrict actions based on roles

#### 🎭 Roles Implemented:

* **Viewer** → Can only view dashboard data
* **Analyst** → Can view records and insights
* **Admin** → Full access (users + records management)

---

### 2️⃣ Financial Records Management

Handles all financial transactions and entries.

#### 📌 Record Fields:

* Amount
* Type (Income / Expense)
* Category
* Date
* Notes / Description

#### ⚙️ Supported Operations:

* Create records
* View records
* Update records
* Delete records
* Filter records (by date, category, type)

---

### 3️⃣ Dashboard Summary

Provides aggregated insights for better decision-making.

#### 📊 Includes:

* Total Income
* Total Expenses
* Net Balance
* Category-wise totals
* Recent transactions
* Monthly / Weekly trends

---

### 4️⃣ Access Control Logic

Implements strict backend-level permission control.

#### 🔐 Rules:

* **Viewer** → Cannot create/update/delete
* **Analyst** → Read-only access to records & insights
* **Admin** → Full control over system

All routes and actions are protected based on role validation.

---

## 🖼️ Screenshots

### 🏠 Home Page

![Home Page](static/1) Home Page.png)

---

### 📝 Register Page

![Register Page](static/2) Register Page.png)

---

### 🔐 Login Page

![Login Page](static/screenshots/login.png)

---

### 👤 User Page

![User Page](static/screenshots/user.png)

---

### 🧑‍💼 Admin Panel

![Admin Panel](static/screenshots/admin_panel.png)

---

### 📊 Analyst Panel

![Analyst Page](static/screenshots/analyst.png)

---

### 📈 Dashboard & Insights

![Dashboard](static/screenshots/dashboard.png)

---

### 🔍 Search & Filter

![Search](static/screenshots/search.png)

---

### 👥 User Management

![User Management](static/screenshots/user_management.png)

---

### 💰 Record Management

![Record Management](static/screenshots/records.png)


---

## ⚙️ Installation

### 1. Clone repository

```bash
git clone https://github.com/your-username/finance-dashboard.git
cd finance-dashboard
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

---

## 🧠 Tech Stack

* **Backend:** Flask, SQLAlchemy
* **Frontend:** HTML, CSS, Bootstrap Icons
* **Database:** SQLite
* **Templates:** Jinja2

---

## 📂 Project Structure

```
project/
│
├── static/
│   ├── favicon.png
│   ├── screenshots/
│       ├── admin_panel.png
│       ├── register.png
│       ├── flash.png
│
├── templates/
├── app.py
├── models.py
├── requirements.txt
└── README.md
```

---

## 📌 Notes

* Ensure roles (Viewer, Analyst, Admin) exist in DB
* Flash messages support categories:

  * success
  * error
  * warning
  * info

---

## ✨ Future Improvements

* 📊 Advanced analytics charts
* 📁 Export reports (PDF/Excel)
* 🌐 Deployment (Render / AWS)
* 🔐 Enhanced authentication

---

## 👨‍💻 Author

Built with 💙 as a real-world backend-focused project.
