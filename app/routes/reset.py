from flask import render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from app import app, db
from app.models import User

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check passwords match
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('reset_password'))

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with this email', 'error')
            return redirect(url_for('reset_password'))

        # Update password (hashed)
        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash('Password updated successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')
