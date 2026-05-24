# Anik Tech School Website

A Flask-based university website with admin panel, student portal, and email notifications.

## Project Structure

```
anik_tech_school/
├── app.py                        ← Main Flask app (routes, models, email)
├── requirements.txt              ← Python dependencies
├── instance/
│   └── anik_tech.db              ← SQLite database (auto-created on first run)
├── templates/
│   ├── base.html                 ← Public layout (navbar + footer)
│   ├── index.html                ← Home page
│   ├── programs.html             ← Programs page
│   ├── admissions.html           ← Admissions page
│   ├── about.html                ← About page
│   ├── contact.html              ← Contact page
│   ├── admin/
│   │   ├── base_admin.html       ← Admin sidebar layout
│   │   ├── login.html            ← Admin login
│   │   ├── dashboard.html        ← Admin dashboard
│   │   ├── students.html         ← Student list
│   │   ├── add_student.html      ← Add student form
│   │   ├── manage_grades.html    ← Grade entry + history
│   │   └── manage_courses.html   ← Course enrollment
│   ├── portal/
│   │   ├── base_portal.html      ← Student portal layout
│   │   ├── login.html            ← Student login
│   │   ├── dashboard.html        ← Student overview
│   │   ├── courses.html          ← Enrolled courses
│   │   └── grades.html           ← Results + GPA
│   └── emails/
│       ├── welcome.html          ← Welcome email (sent on student creation)
│       └── grades.html           ← Results notification email
└── static/
    └── css/
        └── style.css             ← All styles
```

## How to Run

### Step 1 — Install dependencies
```
pip install -r requirements.txt
```

### Step 2 — Configure Gmail (for email notifications)
Open `app.py` and update these two lines:
```python
app.config['MAIL_USERNAME'] = 'your-gmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-gmail-app-password'
```

> **Important:** Use a Gmail App Password, NOT your account password.
> Generate one at: https://myaccount.google.com/apppasswords
> (Requires 2-Step Verification to be enabled)

### Step 3 — Run the app
```
python app.py
```

### Step 4 — Open in browser
```
http://127.0.0.1:5000
```

## Default Admin Credentials
- **URL:** http://127.0.0.1:5000/admin/login
- **Username:** `admin`
- **Password:** `Admin@1234`

> Change this immediately after first login by updating `create_default_admin()` in `app.py`.

## Pages & URLs

| URL                         | Description                     |
|-----------------------------|---------------------------------|
| `/`                         | Home page                       |
| `/programs`                 | Programs listing                |
| `/admissions`               | Admissions info                 |
| `/about`                    | About page                      |
| `/contact`                  | Contact page                    |
| `/admin/login`              | Admin login                     |
| `/admin`                    | Admin dashboard                 |
| `/admin/students`           | View all students               |
| `/admin/students/add`       | Add new student                 |
| `/admin/students/<id>/grades`   | Manage student grades       |
| `/admin/students/<id>/courses`  | Manage student courses      |
| `/portal/login`             | Student portal login            |
| `/portal`                   | Student dashboard               |
| `/portal/courses`           | View enrolled courses           |
| `/portal/grades`            | View grades + GPA               |

## Email Notifications

Two automatic emails are sent:
1. **Welcome email** — when admin adds a new student (includes matric number and portal link)
2. **Grades notification** — when admin publishes a grade (includes result table and portal link)

## Grading Scale

| Score   | Grade | Grade Point |
|---------|-------|-------------|
| 70–100  | A     | 5.0         |
| 60–69   | B     | 4.0         |
| 50–59   | C     | 3.0         |
| 45–49   | D     | 2.0         |
| 40–44   | E     | 1.0         |
| 0–39    | F     | 0.0         |
