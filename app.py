
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from authorize import role_required
from models import *
from datetime import datetime as dt

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'university.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'beyond_course_scope'
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    default_route_function = 'student_view_all'
    default_student_route_function = 'student_view'

    if request.method == 'GET':
        if current_user.is_authenticated:
            if current_user.role in ['MANAGER', 'ADMIN']:
                return redirect(url_for(default_route_function))
            elif current_user.role == 'STUDENT':
                return redirect(
                    url_for(default_student_route_function, student_id=0)
                )
        else:
            redirect_route = request.args.get('next')
            return render_template(
                'login.html',
                redirect_route=redirect_route
            )

    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        redirect_route = request.form.get('redirect_route')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            if current_user.role in ['MANAGER', 'ADMIN']:
                return redirect(
                    redirect_route if redirect_route
                    else url_for(default_route_function)
                )

            elif current_user.role == 'STUDENT':
                return redirect(
                    redirect_route if redirect_route
                    else url_for(default_student_route_function, student_id=0)
                )

        else:
            flash(
                'Your login information was not correct. Please try again.',
                'error'
            )

        return redirect(url_for('login'))

    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


# Training route: MANAGER and ADMIN only
@app.route('/training')
@login_required
@role_required(['MANAGER', 'ADMIN'])
def training():
    return render_template('training.html')


@app.route('/student/view')
@login_required
@role_required(['ADMIN', 'MANAGER'])
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


@app.route('/student/view/<int:student_id>')
@login_required
@role_required(['ADMIN', 'MANAGER', 'STUDENT'])
def student_view(student_id):

    if current_user.role in ['MANAGER', 'ADMIN']:
        student = Student.query.filter_by(
            student_id=student_id
        ).first()

        majors = Major.query.order_by(Major.major).all()

        if student:
            return render_template(
                'student_entry.html',
                student=student,
                majors=majors,
                action='read'
            )

        flash(
            'Student attempting to be viewed could not be found!',
            'error'
        )
        return redirect(url_for('student_view_all'))

    elif current_user.role == 'STUDENT':
        student = Student.query.filter_by(
            email=current_user.email
        ).first()

        majors = Major.query.order_by(Major.major).all()

        if student:
            return render_template(
                'student_entry.html',
                student=student,
                majors=majors,
                action='read'
            )

        flash(
            'Your record could not be located. Please contact advising.',
            'error'
        )
        return redirect(url_for('error'))

    else:
        flash(
            'Invalid request. Please contact support if this problem persists.',
            'error'
        )
        return render_template('error.html')


@app.route('/student/create', methods=['GET', 'POST'])
@login_required
@role_required(['ADMIN', 'MANAGER'])
def student_create():

    if request.method == 'GET':
        majors = Major.query.order_by(Major.major).all()

        return render_template(
            'student_entry.html',
            majors=majors,
            action='create'
        )

    elif request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        major_id = request.form['major_id']
        birth_date = request.form['birth_date']
        is_honors = 'is_honors' in request.form

        student = Student(
            first_name=first_name,
            last_name=last_name,
            email=email,
            major_id=major_id,
            birth_date=dt.strptime(birth_date, '%Y-%m-%d'),
            is_honors=is_honors
        )

        db.session.add(student)
        db.session.commit()

        flash(
            f'{first_name} {last_name} was successfully added!',
            'success'
        )

        return redirect(url_for('student_view_all'))

    flash(
        'Invalid request. Please contact support if this problem persists.',
        'error'
    )
    return redirect(url_for('student_view_all'))


@app.route('/student/update/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required(['ADMIN', 'MANAGER'])
def student_edit(student_id):

    if request.method == 'GET':
        student = Student.query.filter_by(
            student_id=student_id
        ).first()

        majors = Major.query.order_by(Major.major).all()

        if student:
            return render_template(
                'student_entry.html',
                student=student,
                majors=majors,
                action='update'
            )

        flash(
            'Student attempting to be edited could not be found!',
            'error'
        )

    elif request.method == 'POST':
        student = Student.query.filter_by(
            student_id=student_id
        ).first()

        if student:
            student.first_name = request.form['first_name']
            student.last_name = request.form['last_name']
            student.email = request.form['email']
            student.major_id = request.form['major_id']
            student.birthdate = dt.strptime(
                request.form['birth_date'],
                '%Y-%m-%d'
            )
            student.num_credits_completed = request.form[
                'num_credits_completed'
            ]
            student.gpa = request.form['gpa']
            student.is_honors = 'is_honors' in request.form

            db.session.commit()

            flash(
                f'{student.first_name} {student.last_name} was successfully updated!',
                'success'
            )
        else:
            flash(
                'Student attempting to be edited could not be found!',
                'error'
            )

        return redirect(url_for('student_view_all'))

    flash(
        'Invalid request. Please contact support if this problem persists.',
        'error'
    )
    return redirect(url_for('student_view_all'))


@app.route('/student/delete/<int:student_id>')
@login_required
@role_required(['ADMIN'])
def student_delete(student_id):
    student = Student.query.filter_by(
        student_id=student_id
    ).first()

    if student:
        db.session.delete(student)
        db.session.commit()

        flash(
            f'{student} was successfully deleted!',
            'success'
        )
    else:
        flash(
            'Delete failed! Student could not be found.',
            'error'
        )

    return redirect(url_for('student_view_all'))


@app.route('/error')
def error():
    return render_template('error.html')


@app.errorhandler(404)
def page_not_found(e):
    flash(
        'Sorry! You are trying to access a page that does not exist. '
        'Please contact support if this problem persists.',
        'error'
    )

    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=5001)
