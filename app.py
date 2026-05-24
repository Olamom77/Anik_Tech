from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)

# ── Config ──────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = 'change-this-to-a-random-secret-key-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///anik_tech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail (Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-gmail@gmail.com'        # ← replace
app.config['MAIL_PASSWORD'] = 'your-gmail-app-password'    # ← replace (use App Password, not account password)
app.config['MAIL_DEFAULT_SENDER'] = ('Anik Tech School', 'your-gmail@gmail.com')

db = SQLAlchemy(app)
mail = Mail(app)


# ── Models ───────────────────────────────────────────────────────────────
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    matric_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    program = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), nullable=False, default='100L')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_courses(self):
        return Course.query.filter_by(student_id=self.id).all()

    def get_grades(self):
        return Grade.query.filter_by(student_id=self.id).all()


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_code = db.Column(db.String(20), nullable=False)
    course_title = db.Column(db.String(120), nullable=False)
    credit_units = db.Column(db.Integer, nullable=False, default=3)
    semester = db.Column(db.String(30), nullable=False)


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_code = db.Column(db.String(20), nullable=False)
    course_title = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    grade_point = db.Column(db.Float, nullable=False)
    credit_units = db.Column(db.Integer, nullable=False, default=3)
    semester = db.Column(db.String(30), nullable=False)


# ── Auth Decorators ───────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_id'):
            flash('Please log in as admin.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('student_id'):
            flash('Please log in to your student portal.', 'warning')
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated


# ── Email Helpers ─────────────────────────────────────────────────────────
def send_welcome_email(student):
    try:
        msg = Message(
            subject='Welcome to Anik Tech School!',
            recipients=[student.email]
        )
        msg.html = render_template('emails/welcome.html', student=student)
        mail.send(msg)
    except Exception as e:
        app.logger.error(f'Email error: {e}')


def send_grade_notification(student, semester):
    try:
        grades = Grade.query.filter_by(student_id=student.id, semester=semester).all()
        msg = Message(
            subject=f'Your {semester} Results – Anik Tech School',
            recipients=[student.email]
        )
        msg.html = render_template('emails/grades.html', student=student, grades=grades, semester=semester)
        mail.send(msg)
    except Exception as e:
        app.logger.error(f'Email error: {e}')


# ── Public Pages ──────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/programs')
def programs():
    return render_template('programs.html')

@app.route('/admissions')
def admissions():
    return render_template('admissions.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# ── Admin Auth ────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_id'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Welcome back, ' + admin.username + '!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))


# ── Admin Dashboard ───────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    total_students = Student.query.count()
    total_courses = Course.query.count()
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_courses=total_courses,
                           recent_students=recent_students)


@app.route('/admin/students')
@admin_required
def admin_students():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students.html', students=students)


@app.route('/admin/students/add', methods=['GET', 'POST'])
@admin_required
def admin_add_student():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        matric = request.form.get('matric_number', '').strip().upper()
        program = request.form.get('program', '').strip()
        level = request.form.get('level', '100L')
        password = request.form.get('password', '')

        if Student.query.filter_by(email=email).first():
            flash('A student with that email already exists.', 'danger')
        elif Student.query.filter_by(matric_number=matric).first():
            flash('That matric number is already registered.', 'danger')
        else:
            student = Student(full_name=full_name, email=email,
                              matric_number=matric, program=program, level=level)
            student.set_password(password)
            db.session.add(student)
            db.session.commit()
            send_welcome_email(student)
            flash(f'Student {full_name} added and welcome email sent.', 'success')
            return redirect(url_for('admin_students'))
    return render_template('admin/add_student.html')


@app.route('/admin/students/<int:student_id>/grades', methods=['GET', 'POST'])
@admin_required
def admin_manage_grades(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        course_code = request.form.get('course_code', '').strip().upper()
        course_title = request.form.get('course_title', '').strip()
        score = float(request.form.get('score', 0))
        credit_units = int(request.form.get('credit_units', 3))
        semester = request.form.get('semester', '').strip()

        # Auto-calculate grade and grade point
        if score >= 70:
            g, gp = 'A', 5.0
        elif score >= 60:
            g, gp = 'B', 4.0
        elif score >= 50:
            g, gp = 'C', 3.0
        elif score >= 45:
            g, gp = 'D', 2.0
        elif score >= 40:
            g, gp = 'E', 1.0
        else:
            g, gp = 'F', 0.0

        grade = Grade(student_id=student.id, course_code=course_code,
                      course_title=course_title, score=score, grade=g,
                      grade_point=gp, credit_units=credit_units, semester=semester)
        db.session.add(grade)
        db.session.commit()

        send_grade_notification(student, semester)
        flash('Grade added and student notified by email.', 'success')

    grades = Grade.query.filter_by(student_id=student.id).all()
    return render_template('admin/manage_grades.html', student=student, grades=grades)


@app.route('/admin/students/<int:student_id>/courses', methods=['GET', 'POST'])
@admin_required
def admin_manage_courses(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        course_code = request.form.get('course_code', '').strip().upper()
        course_title = request.form.get('course_title', '').strip()
        credit_units = int(request.form.get('credit_units', 3))
        semester = request.form.get('semester', '').strip()
        course = Course(student_id=student.id, course_code=course_code,
                        course_title=course_title, credit_units=credit_units,
                        semester=semester)
        db.session.add(course)
        db.session.commit()
        flash('Course added.', 'success')

    courses = Course.query.filter_by(student_id=student.id).all()
    return render_template('admin/manage_courses.html', student=student, courses=courses)


# ── Student Portal ────────────────────────────────────────────────────────
@app.route('/portal/login', methods=['GET', 'POST'])
def student_login():
    if session.get('student_id'):
        return redirect(url_for('student_dashboard'))
    if request.method == 'POST':
        matric = request.form.get('matric_number', '').strip().upper()
        password = request.form.get('password', '')
        student = Student.query.filter_by(matric_number=matric).first()
        if student and student.check_password(password):
            session['student_id'] = student.id
            session['student_name'] = student.full_name
            flash('Welcome back, ' + student.full_name.split()[0] + '!', 'success')
            return redirect(url_for('student_dashboard'))
        flash('Invalid matric number or password.', 'danger')
    return render_template('portal/login.html')


@app.route('/portal/logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('student_login'))


@app.route('/portal')
@student_required
def student_dashboard():
    student = Student.query.get(session['student_id'])
    courses = Course.query.filter_by(student_id=student.id).all()
    grades = Grade.query.filter_by(student_id=student.id).all()
    return render_template('portal/dashboard.html', student=student,
                           courses=courses, grades=grades)


@app.route('/portal/courses')
@student_required
def student_courses():
    student = Student.query.get(session['student_id'])
    courses = Course.query.filter_by(student_id=student.id).all()
    # Group by semester
    by_semester = {}
    for c in courses:
        by_semester.setdefault(c.semester, []).append(c)
    return render_template('portal/courses.html', student=student, by_semester=by_semester)


@app.route('/portal/grades')
@student_required
def student_grades():
    student = Student.query.get(session['student_id'])
    grades = Grade.query.filter_by(student_id=student.id).all()
    by_semester = {}
    for g in grades:
        by_semester.setdefault(g.semester, []).append(g)
    # Compute GPA per semester and overall
    def compute_gpa(grade_list):
        total_points = sum(g.grade_point * g.credit_units for g in grade_list)
        total_units = sum(g.credit_units for g in grade_list)
        return round(total_points / total_units, 2) if total_units else 0.0
    semester_gpas = {sem: compute_gpa(gs) for sem, gs in by_semester.items()}
    overall_gpa = compute_gpa(grades)
    return render_template('portal/grades.html', student=student,
                           by_semester=by_semester, semester_gpas=semester_gpas,
                           overall_gpa=overall_gpa)


# ── DB Init ───────────────────────────────────────────────────────────────
def create_default_admin():
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', email='admin@aniktech.edu.ng')
        admin.set_password('Admin@1234')   # Change this after first login!
        db.session.add(admin)
        db.session.commit()
        print('✓ Default admin created — username: admin | password: Admin@1234')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()
    app.run(debug=True)

@app.route('/setup-admin-12345')
def setup_admin():
    if Admin.query.first():
        return "Admin already exists"
    admin = Admin(username="admin", email="admin@anik.tech")
    admin.set_password("Olamom77")
    db.session.add(admin)
    db.session.commit()
    return "Admin created successfully"
