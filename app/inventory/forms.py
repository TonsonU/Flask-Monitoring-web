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

class EditSerialNumberForm(FlaskForm):
    serial_number = StringField('Serial Number', validators=[DataRequired(), Length(max=100)])
    remark = StringField('Remark', validators=[Length(max=100)])
    submit = SubmitField('Save')

class EditForceDataForm(FlaskForm):
    plus_before = StringField('Plus Before', validators=[DataRequired(), Length(max=100)])
    minus_before = StringField('Minus Before', validators=[DataRequired(), Length(max=100)])
    plus_after = StringField('Plus After', validators=[Optional(), Length(max=100)])
    minus_after = StringField('Minus After', validators=[Optional(), Length(max=100)])
    remark = TextAreaField('Remark', validators=[Optional()])
    submit = SubmitField('Save')

class EditMacAddressForm(FlaskForm):
    mac_address = StringField('MAC Address', validators=[DataRequired(), Length(max=100)])
    remark = StringField('Remark', validators=[Length(max=100)])
    submit = SubmitField('Save')

class EditModuleForm(FlaskForm):
    red_module = StringField('Red Module', validators=[Optional()])
    white_module = StringField('White Module', validators=[Optional()])
    yellow_module = StringField('Yellow Module', validators=[Optional()])
    remark = TextAreaField('Remark', validators=[Optional()])
    submit = SubmitField('Save')