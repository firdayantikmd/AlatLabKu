from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User, UserRole
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

from helpers import login_required

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/hello', methods=['GET'])
def hello():
    return "Hello!!"

@user_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Choose another one.')
            return redirect(url_for('user_routes.signup'))

        # Store user details in database
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            role='Mahasiswa'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please login.')
        return redirect(url_for('user_routes.signin'))

    return render_template('signup.html')

@user_routes.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Incorrect email or password. Please try again.')
            return redirect(url_for('user_routes.signin'))

        session['username'] = user.username

        flash('Login successful!')
        return redirect(url_for('base_routes.home'))

    return render_template('signin.html')

@user_routes.route('/signout', methods=['GET'])
def signout():
    # Remove the user data from the session if it's there
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('user_routes.signin'))

@user_routes.route('/userlist', methods=['GET'])
@login_required
def get_userlist():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    search_term = request.args.get('search', '')
    query = User.query

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            User.username.ilike(search_pattern) | 
            User.full_name.ilike(search_pattern) |
            User.email.ilike(search_pattern) |
            User.student_id.ilike(search_pattern) |
            User.no_hp.ilike(search_pattern)
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    return render_template('userlist.html', users=users, pagination=pagination)

@user_routes.route('/edituser/<int:id>', methods=['GET', 'POST'])
@login_required
def edituser(id):
    # Assuming you have a User model that queries users by id
    user = User.query.get(id)
    
    if not user:
        flash("User not found", "error")
        return redirect(url_for('user_routes.get_userlist'))  # Assuming you have a user list route

    if request.method == 'GET':
        # Render an edit user template with the user's data
        return render_template('edituser.html', user=user)

    elif request.method == 'POST':
        # Fetch data from form (assuming you're using form data to send the updates)
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        student_id = request.form.get('student_id')
        no_hp = request.form.get('no_hp')

        # Update user data
        user.username = username
        user.email = email
        user.full_name = full_name if full_name else user.full_name
        user.student_id = student_id if student_id else user.student_id
        user.no_hp = no_hp if no_hp else user.no_hp

        # Save changes to database
        db.session.commit()

        flash("User updated successfully!", "success")
        return redirect(url_for('user_routes.get_userlist'))

@user_routes.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    
    if not user:
        flash("User not found", "error")
        return redirect(url_for('user_routes.get_userlist'))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully!", "success")
    return redirect(url_for('user_routes.get_userlist'))

@user_routes.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'GET':
        return render_template('adduser.html')

    elif request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        student_id = request.form.get('student_id')
        no_hp = request.form.get('no_hp')
        self_photo = request.form.get('self_photo')  # assuming this is a string path, adjust if using file uploads
        card_photo = request.form.get('card_photo')  # same assumption as self_photo
        major = request.form.get('major')
        role = request.form.get('role', 'Mahasiswa')

        # Check if username, email, or student_id already exists
        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()
        user_by_student_id = User.query.filter_by(student_id=student_id).first()

        if user_by_username:
            flash('Username already exists. Choose another one.')
            return redirect(url_for('user_routes.add_user'))
        if user_by_email:
            flash('Email already exists. Choose another one.')
            return redirect(url_for('user_routes.add_user'))
        if user_by_student_id:
            flash('Student ID already exists. Choose another one.')
            return redirect(url_for('user_routes.add_user'))

        # Store user details in database
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            full_name=full_name,
            student_id=student_id,
            no_hp=no_hp,
            self_photo=self_photo,
            card_photo=card_photo,
            major=major,
            role=role  # you might need to ensure this matches the UserRole enum
        )
        db.session.add(new_user)
        db.session.commit()

        flash('User added successfully!')
        return redirect(url_for('user_routes.get_userlist'))

    return render_template('adduser.html',  users=users, pagination=pagination)
