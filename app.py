
import os
from datetime import datetime as dt
from email.utils import parseaddr

from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student, Major


# ==========================================
# FLASK APPLICATION SETUP
# ==========================================

app = Flask(__name__)

os.makedirs(app.instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(app.instance_path, 'university.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'development-only-secret'
)

db.init_app(app)


# ==========================================
# MODULE 08: EXISTING WEBSITE
# ==========================================

@app.route('/')
def hello_world():
    return redirect(url_for('student_view_all'))


@app.route('/hello')
def hello_page():
    return render_template('hello.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/about-css')
def about_css():
    return render_template('about-css.html')


@app.route('/favorite-course')
def favorite_course():
    subject = request.args.get('subject', '')
    course_number = request.args.get('course_number', '')

    return render_template(
        'favorite-course.html',
        subject=subject,
        course_number=course_number
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        email = request.form.get('email', '')
        message = request.form.get('message', '')

        return render_template(
            'contact.html',
            submitted=True,
            first_name=first_name,
            last_name=last_name,
            email=email,
            message=message
        )

    return render_template('contact.html', submitted=False)


# ==========================================
# MODULE 09: EMAIL VALIDATION
# ==========================================

def valid_email(value):
    if not value or len(value) > 100:
        return False

    parsed_email = parseaddr(value)[1]

    return (
        parsed_email == value
        and value.count('@') == 1
        and '.' in value.split('@')[1]
        and ' ' not in value
    )


# ==========================================
# READ: VIEW ALL STUDENTS
# ==========================================

@app.route('/student/view', methods=['GET'])
def student_view_all():
    students = (
        Student.query
        .outerjoin(Major, Student.major_id == Major.major_id)
        .add_entity(Major)
        .order_by(Student.last_name, Student.first_name)
        .all()
    )

    return render_template(
        'student_view_all.html',
        students=students
    )


# ==========================================
# READ: VIEW ONE STUDENT
# ==========================================

@app.route('/student/view/<int:student_id>', methods=['GET'])
def student_view(student_id):

    student = Student.query.filter_by(
        student_id=student_id
    ).first()

    if student is None:
        flash('Student could not be found.', 'error')
        return redirect(url_for('student_view_all'))

    majors = Major.query.order_by(Major.major).all()

    return render_template(
        'student_entry.html',
        student=student,
        majors=majors,
        action='read'
    )


# ==========================================
# CREATE: ADD STUDENT
# ==========================================

@app.route('/student/create', methods=['GET', 'POST'])
def student_create():

    if request.method == 'GET':
        majors = Major.query.order_by(Major.major).all()

        return render_template(
            'student_entry.html',
            majors=majors,
            action='create'
        )

    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    major_id = request.form.get('major_id', '')
    birth_date = request.form.get('birth_date', '')
    is_honors = 'is_honors' in request.form

    if not first_name or not last_name:
        flash('First and last names are required.', 'error')
        return redirect(url_for('student_create'))

    if not valid_email(email):
        flash(
            'A valid email address of 100 characters or fewer is required.',
            'error'
        )
        return redirect(url_for('student_create'))

    try:
        student = Student(
            first_name=first_name,
            last_name=last_name,
            email=email,
            major_id=int(major_id),
            birth_date=dt.strptime(birth_date, '%Y-%m-%d'),
            is_honors=is_honors
        )
    except (ValueError, TypeError):
        flash('Please enter valid student information.', 'error')
        return redirect(url_for('student_create'))

    db.session.add(student)
    db.session.commit()

    flash(
        f'{first_name} {last_name} was successfully added!',
        'success'
    )

    return redirect(url_for('student_view_all'))


# ==========================================
# UPDATE: EDIT STUDENT
# ==========================================

@app.route('/student/update/<int:student_id>', methods=['GET', 'POST'])
def student_edit(student_id):

    student = Student.query.filter_by(
        student_id=student_id
    ).first()

    if student is None:
        flash('Student could not be found.', 'error')
        return redirect(url_for('student_view_all'))

    if request.method == 'GET':
        majors = Major.query.order_by(Major.major).all()

        return render_template(
            'student_entry.html',
            student=student,
            majors=majors,
            action='update'
        )

    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()

    if not first_name or not last_name:
        flash('First and last names are required.', 'error')
        return redirect(url_for('student_edit', student_id=student_id))

    if not valid_email(email):
        flash(
            'A valid email address of 100 characters or fewer is required.',
            'error'
        )
        return redirect(url_for('student_edit', student_id=student_id))

    try:
        major_id = int(request.form['major_id'])
        birth_date = dt.strptime(
            request.form['birth_date'],
            '%Y-%m-%d'
        )
        credits = int(request.form['num_credits_completed'])
        gpa = float(request.form['gpa'])

        if credits < 0 or not 0 <= gpa <= 4:
            raise ValueError

    except (ValueError, TypeError, KeyError):
        flash('Please enter valid student information.', 'error')
        return redirect(url_for('student_edit', student_id=student_id))

    student.first_name = first_name
    student.last_name = last_name
    student.email = email
    student.major_id = major_id
    student.birth_date = birth_date
    student.num_credits_completed = credits
    student.gpa = gpa
    student.is_honors = 'is_honors' in request.form

    db.session.commit()

    flash(
        f'{student.first_name} {student.last_name} was successfully updated!',
        'success'
    )

    return redirect(url_for('student_view_all'))


# ==========================================
# DELETE: REMOVE STUDENT
# ==========================================

@app.route('/student/delete/<int:student_id>', methods=['POST'])
def student_delete(student_id):

    student = Student.query.filter_by(
        student_id=student_id
    ).first()

    if student is None:
        flash('Delete failed! Student could not be found.', 'error')
        return redirect(url_for('student_view_all'))

    full_name = f'{student.first_name} {student.last_name}'

    db.session.delete(student)
    db.session.commit()

    flash(
        f'{full_name} was successfully deleted!',
        'success'
    )

    return redirect(url_for('student_view_all'))


# ==========================================
# START FLASK APPLICATION
# ==========================================

if __name__ == '__main__':
    app.run(port=5001, debug=True)
