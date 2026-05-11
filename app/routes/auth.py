"""
Authentication routes: register, login, logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new user account."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password:
            return render_template('register.html', error='Please fill in all required fields.')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            return render_template('register.html', error='Username or email is already taken.')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Account created. You are now signed in.', 'scan_success')
        return redirect(url_for('scan.new_scan'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate user and create login session."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            return render_template('login.html', error='Please enter your username/email and password.')

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if not user or not user.check_password(password):
            return render_template('login.html', error='Invalid credentials. Please try again.')

        login_user(user)
        flash('Signed in successfully.', 'scan_success')
        return redirect(url_for('scan.new_scan'))

    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout current user."""
    if current_user.is_authenticated:
        logout_user()
        flash('You have been signed out.', 'scan_success')
    return redirect(url_for('auth.login'))
