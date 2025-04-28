####################################################
# Flask Monitoring Web
#
# 
# Project : Python, Flask, MySQLite, Bootstrap
# Author  : Tonson Ubonsri
# Modifier: 
# Version : 
# Date    : Dec 01, 2024
#
####################################################

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm, ForgotPasswordForm
from app.extensions import db
from app.models import User
from . import auth_bp
from sqlalchemy import func



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # สมมติว่ามี main blueprint

    # --- แก้ไข: สร้าง form instance ---
    form = RegisterForm()
    # --- สิ้นสุดการแก้ไข ---

    # --- แก้ไข: ใช้ form.validate_on_submit() ---
    if form.validate_on_submit():
        # ดึงข้อมูลจาก form object และ strip() username
        username = form.username.data.strip()
        password = form.password.data
        # --- แก้ไข: ดึง role จาก form (ถ้ามี field นี้ใน RegisterForm) ---
        # role = request.form.get('role') # ลบออก
        role = form.role.data if hasattr(form, 'role') else 'User' # ดึงจาก form ถ้ามี, หรือกำหนด default
        # --- สิ้นสุดการแก้ไข ---


        # --- แก้ไข: ตรวจสอบ username ซ้ำ (ใช้ func.lower) ---
        # if User.query.filter_by(username=username).first():
        if User.query.filter(func.lower(User.username) == func.lower(username)).first():
            flash("Username already exists.", "danger")
            # Render หน้าเดิมพร้อม form และ error
            return render_template('auth/register.html', title='Register', form=form)
        # --- สิ้นสุดการแก้ไข ---

        # --- สร้าง User ---
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration: {e}', 'danger')
            print(f"Error during registration: {e}")

    # --- แก้ไข: ส่ง form ไป render เสมอ และใช้ path เต็ม ---
    return render_template('register.html', title='Register', form=form)
    # --- สิ้นสุดการแก้ไข ---

# app/auth/routes.py
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        # --- ใส่ Logic การอัปเดตรหัสผ่านจริงที่นี่ ---
        try:
            # ดึง username จาก form ที่ validate ผ่านแล้ว
            input_username = form.username.data.strip()
            # ค้นหา user อีกครั้ง (ควรจะเจอแน่นอน)
            user = User.query.filter(func.lower(User.username) == func.lower(input_username)).first()

            if user:
                # Hash รหัสผ่านใหม่
                hashed_password = generate_password_hash(form.new_password.data)
                user.password = hashed_password
                db.session.commit()
                flash('Password updated successfully! Please login.', 'success')
                return redirect(url_for('auth.login')) # Redirect หลังสำเร็จ
            else:
                # กรณีที่ไม่ควรเกิดขึ้น ถ้า validate ผ่านแล้ว
                flash('An unexpected error occurred finding the user after validation.', 'danger')

        except Exception as e:
            db.session.rollback() # Rollback ถ้ามีปัญหา
            flash(f'An error occurred: {e}', 'danger')
            print(f"Error during password update: {e}") # Log error

        # ถ้ามี error หรือหา user ไม่เจอ (กรณีแปลก) จะ render template ใหม่
        # (แต่ปกติควรจะ redirect ไปแล้ว)

    # --- ลบ elif request.method == 'POST': ออก ---
    # elif request.method == 'POST':
    #     # ... โค้ดส่วนนี้ไม่ควรมีแล้ว ...
    #     pass

    # --- Debug: พิมพ์ errors ก่อน render ---
    print("Form errors before rendering:", form.errors)
    # --------------------------------------

    # ส่ง form ไป render (จะไม่มี user_found แล้ว)
    return render_template('forgot_password.html', title='Forgot Password', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # สมมติว่ามี main blueprint

    form = LoginForm()
    # --- แก้ไข: ใช้ form.validate_on_submit() ---
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        # --- แก้ไข: ค้นหา user (ใช้ func.lower) ---
        # user = User.query.filter_by(username=username).first()
        user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
        # --- สิ้นสุดการแก้ไข ---

        if user and check_password_hash(user.password, password):
            login_user(user)
            # --- แก้ไข: จัดการ next parameter สำหรับ redirect หลัง login ---
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index')) # Redirect ไป next หรือ main.index
            # --- สิ้นสุดการแก้ไข ---
        else:
            flash("Invalid username or password.", "danger")
    # --- สิ้นสุดการแก้ไข ---

    # --- แก้ไข: ใช้ path เต็ม ---
    return render_template('login.html', title='Login', form=form)
    # --- สิ้นสุดการแก้ไข ---

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))