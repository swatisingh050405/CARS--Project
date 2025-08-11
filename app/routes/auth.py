from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.forms import LoginForm, SignupForm
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.signup'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('signup.html', form=form)
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html', form=form)
        user = User(name=form.name.data, email=form.email.data,
                    password_hash=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard.dashboard'))
    return render_template('signup.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# ✅ Reset Password route (NEW)
@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Password match check
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.reset_password'))

        # User check
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with this email', 'danger')
            return redirect(url_for('auth.reset_password'))

        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash('Password updated successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset.html')