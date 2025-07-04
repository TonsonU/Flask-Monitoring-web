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
from wtforms.validators import DataRequired, Length, ValidationError, Optional, URL
from flask_wtf.file import FileAllowed  # เพิ่มการนำเข้า FileAllowed
from wtforms_sqlalchemy.fields import QuerySelectField
from models import Line, Location, DeviceType, DeviceName
from datetime import datetime
import re

# Register Form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

    def validate_password(self, password):
        if self.password.data != self.confirm_password.data:
            raise ValidationError('Passwords must match.')

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

