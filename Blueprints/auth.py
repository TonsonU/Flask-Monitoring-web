from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role')

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
        user_found = True  # Default value, assume user exists

        if request.method == 'POST':
            username = request.form['username']
            new_password = request.form['new_password']

            # ค้นหาผู้ใช้ในฐานข้อมูล
            user = User.query.filter_by(username=username).first()

            if user:
                # อัปเดตรหัสผ่านใหม่
                hashed_password = generate_password_hash(new_password)
                user.password = hashed_password
                db.session.commit()

                flash("Password updated successfully.", "success")
                return redirect(url_for('login'))
            else:
                # ถ้าไม่พบผู้ใช้ให้แสดงข้อความ
                user_found = False
                #flash("User not found. Please register.", "danger")

        return render_template('forgot_password.html', user_found=user_found)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))
