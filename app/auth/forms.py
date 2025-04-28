####################################################
# Flask Monitoring Web
#
# 
# Project : Python, Flask, MySQLite, Bootstrap
# Author  : Thanapoom Sukarin, Tonson Ubonsri
# Modifier: 
# Version : 
# Date    : Dec 01, 2024
#
####################################################

# forms.py: เก็บฟอร์มทั้งหมดที่ใช้ในแอป
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField, FileField,IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, URL, EqualTo
from flask_wtf.file import FileAllowed  # เพิ่มการนำเข้า FileAllowed
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import User
from sqlalchemy import func
from datetime import datetime
import re

# Register Form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    # --- แก้ไข: ใช้ EqualTo validator สำหรับ confirm_password ---
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.') # ใช้ EqualTo ดีกว่า
    ])
    # --- สิ้นสุดการแก้ไข ---

    # --- แก้ไข: เพิ่ม field 'role' ---
    role = SelectField('Role', choices=[('user', 'Technician'), ('admin', 'Engineer')], validators=[DataRequired()]) # ใช้ DataRequired ถ้าบังคับเลือก
    # --- สิ้นสุดการแก้ไข ---

    submit = SubmitField('Register')

    # --- แก้ไข: ลบ validate_password ออก (ใช้ EqualTo แทนแล้ว) ---
    # def validate_password(self, password):
    #     if self.password.data != self.confirm_password.data:
    #         raise ValidationError('Passwords must match.')
    # --- สิ้นสุดการแก้ไข ---


# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ForgotPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    # --- แนะนำ: เพิ่มความยาวขั้นต่ำของรหัสผ่านเป็น 6 หรือ 8 ตัวอักษร ---
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Update Password')

    # --- แก้ไข Custom Validator สำหรับ Username ---
    def validate_username(self, username):
        """
        ตรวจสอบว่า username ที่กรอกมีอยู่ในฐานข้อมูลหรือไม่
        โดยไม่คำนึงถึงตัวพิมพ์ใหญ่/เล็ก และตัดช่องว่างหน้า/หลังออก
        """
        # 1. ดึงข้อมูลที่ผู้ใช้กรอก และตัดช่องว่างหน้า/หลังออก
        input_username = username.data.strip()

        # --- เพิ่ม print statement สำหรับ Debug (เอาออกได้เมื่อแก้ไขเสร็จ) ---
        print(f"Attempting to validate username: '{input_username}'")
        # --- สิ้นสุด print statement ---

        if not input_username: # ตรวจสอบเผื่อผู้ใช้กรอกแต่ช่องว่าง
             raise ValidationError('Please enter a username.')

        # 2. ค้นหาในฐานข้อมูลโดยแปลงเป็นตัวพิมพ์เล็กทั้งสองฝั่ง (Case-Insensitive)
        user = User.query.filter(func.lower(User.username) == func.lower(input_username)).first()

        # --- เพิ่ม print statement สำหรับ Debug (เอาออกได้เมื่อแก้ไขเสร็จ) ---
        if user:
            print(f"Found user in DB: ID={user.id}, Username='{user.username}'")
        else:
            print(f"User '{input_username}' not found in DB (case-insensitive search).")
        # --- สิ้นสุด print statement ---


        if not user:
            # ใช้ข้อความเดิม หรือปรับให้ชัดเจนขึ้น
            raise ValidationError('ไม่มี username นี้อยู่ในระบบ กรุณาตรวจสอบ username หรือลงทะเบียนใหม่')
            # raise ValidationError('Username not found. Please check the username or register.')
    # --- สิ้นสุด Custom Validator ---