# 📘 EdTech Assignment Tracker

A full-stack assignment management system built for Pannini Educational Ventures Pvt. Ltd. internship project.

## 🔧 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap, JavaScript

## 🎯 Features

### 👨‍🏫 Teacher Role
- Signup/Login
- Create assignments
- View submissions

### 👨‍🎓 Student Role
- Signup/Login
- View available assignments
- Submit assignments
- View own submissions

## 📁 Folder Structure

```
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   └── schemas.py
├── frontend/
    ├──index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard_teacher.html
│   ├── dashboard_student.html
│   └── my_submissions.html
└── README.md
├──screenshots/
```

## 🔐 Authentication

- JWT-based auth using `Authorization: Bearer <token>`
- Role-based access control for routes

## 🚀 How to Run Locally

1. **Clone repo** and install dependencies:
   ```bash
   pip install fastapi uvicorn python-multipart python-jose sqlalchemy passlib
   ```

2. **Start server**
   ```bash
   uvicorn main:app --reload
   ```

3. **Open frontend files directly in browser** (HTML)

## ⚙️ API Endpoints

| Method | Endpoint               | Description                     |
|--------|------------------------|---------------------------------|
| POST   | `/signup`              | Register a new user             |
| POST   | `/login`               | Login and get access token      |
| POST   | `/assignments`         | Create assignment (teacher)     |
| GET    | `/assignments`         | List assignments (student)      |
| POST   | `/submit`              | Submit assignment (student)     |
| GET    | `/submissions/{id}`    | View all submissions (teacher)  |
| GET    | `/my-submissions`      | Student's submitted assignments |


## 👨‍🎓 Created by
**Sharath M Talawar**  
GitHub: [https://github.com/sharath816](https://github.com/sharath816)
