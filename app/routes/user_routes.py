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