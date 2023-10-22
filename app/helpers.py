from functools import wraps
from flask import request, redirect, url_for, flash, session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('user_routes.signin'))
        return f(*args, **kwargs)
    return decorated_function
