
from app import app, db
from models import Major, User, Student
from werkzeug.security import generate_password_hash
from datetime import datetime as dt

with app.app_context():
    db.drop_all()
    db.create_all()

    # Initial loading of majors
    majors = [
        'Accounting',
        'Finance',
        'Information Systems',
        'International Business',
        'Management',
        'Operations Management & Business Analytics',
        'Supply Chain Management'
    ]

    for each_major in majors:
        print(f'{each_major} inserted into major')
        a_major = Major(major=each_major)
        db.session.add(a_major)
        db.session.commit()

    # Initial loading of users
    users = [
        {
            'username': 'student',
            'email': 'student@umd.edu',
            'first_name': 'Imma',
            'last_name': 'Student',
            'password': generate_password_hash('studentpw', method='pbkdf2:sha256'),
            'role': 'STUDENT'
        },
        {
            'username': 'manager',
            'email': 'manager@umd.edu',
            'first_name': 'Joe',
            'last_name': 'King',
            'password': generate_password_hash('managerpw', method='pbkdf2:sha256'),
            'role': 'MANAGER'
        },
        {
            'username': 'admin',
            'email': 'admin@umd.edu',
            'first_name': 'Crystal',
            'last_name': 'Ball',
            'password': generate_password_hash('adminpw', method='pbkdf2:sha256'),
            'role': 'ADMIN'
        },
        {
            'username': 'jhung',
            'email': 'jhung@terpmail.umd.edu',
            'first_name': 'Joey',
            'last_name': 'Hung',
            'password': generate_password_hash('jhung', method='pbkdf2:sha256'),
            'role': 'STUDENT'
        }
    ]

    for each_user in users:
        print(f'{each_user["username"]} inserted into user')
        a_user = User(
            username=each_user["username"],
            email=each_user["email"],
            first_name=each_user["first_name"],
            last_name=each_user["last_name"],
            password=each_user["password"],
            role=each_user["role"]
        )
        db.session.add(a_user)
        db.session.commit()

    # Initial loading of students
    students = [
        {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'student@umd.edu',
            'major_id': 3,
            'birth_date': dt.strptime('2007-08-01', '%Y-%m-%d'),
            'is_honors': 1
        },
        {
            'first_name': 'Joey',
            'last_name': 'Hung',
            'email': 'jhung@terpmail.umd.edu',
            'major_id': 1,
            'birth_date': dt.strptime('2003-01-01', '%Y-%m-%d'),
            'is_honors': 0
        }
    ]

    for each_student in students:
        print(f'{each_student["first_name"]} {each_student["last_name"]} inserted into student')
        a_student = Student(
            first_name=each_student["first_name"],
            last_name=each_student["last_name"],
            email=each_student["email"],
            major_id=each_student["major_id"],
            birth_date=each_student["birth_date"],
            is_honors=each_student["is_honors"]
        )
        db.session.add(a_student)
        db.session.commit()
