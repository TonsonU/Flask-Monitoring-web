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

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField, FileField,IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, Optional, URL
from flask_wtf.file import FileAllowed  # เพิ่มการนำเข้า FileAllowed
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Line, Location, DeviceType, DeviceName
from datetime import datetime
import re

class KnowledgeBaseForm(FlaskForm):
    create_date = StringField('Create Date', validators=[DataRequired()])
    device_type = StringField('Device Type', validators=[DataRequired()])
    topic = StringField('Topic')
    description = StringField('Description')
    create_by = StringField('Create By', validators=[DataRequired()])
    
    submit = SubmitField('Create')

class EditKnowledgeBaseForm(FlaskForm):
    create_date = StringField('Create Date', validators=[DataRequired()])
    device_type = StringField('Device Type', validators=[DataRequired()])
    topic = StringField('Topic')
    description = StringField('Description')
    create_by = StringField('Create By', validators=[DataRequired()])
    
    submit = SubmitField('Save Changes')