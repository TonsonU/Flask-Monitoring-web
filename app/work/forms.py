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

# Comment Form
class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
    pdf_url = StringField('PDF Link', validators=[Optional(),])
    image = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Post Comment')

# Create Form
class CreateForm(FlaskForm):
    create_date = StringField("Create Date", validators=[DataRequired()], render_kw={"placeholder": "Select Date and Time"})             # วันที่และเวลา
    work_order = StringField("Work Order", validators=[DataRequired()])               # Work Order
    line_name = QuerySelectField(
        "Line Name",
        query_factory=lambda: Line.query.all(),  # ดึงข้อมูลจากตาราง Line
        get_label="name",  # ชื่อฟิลด์ที่จะแสดงใน dropdown
        allow_blank=True,
        blank_text="Select Line",
        validators=[DataRequired()]
    )
    location_name = QuerySelectField(
        "Location Name",
        query_factory=lambda: Location.query.all(),  # ดึงข้อมูลจากตาราง Location
        get_label="name",
        allow_blank=True,
        blank_text="Select Location",
        validators=[DataRequired()]
    )
    device_type_name = QuerySelectField(
        "Device Type",
        query_factory=lambda: DeviceType.query.all(),  # ดึงข้อมูลจากตาราง DeviceType
        get_label="name",
        allow_blank=True,
        blank_text="Select Device Type",
        validators=[DataRequired()]
    )
    device_name = QuerySelectField(
        "Device Name",
        query_factory=lambda: DeviceName.query.all(),  # ดึงข้อมูลจากตาราง DeviceName
        get_label="name",
        allow_blank=True,
        blank_text="Select Device Name",
        validators=[DataRequired()]
    )
    description = TextAreaField("Description", validators=[DataRequired()])           # รายละเอียด
    report_by = StringField("Report By", validators=[DataRequired()])                 # ผู้รายงาน
    status = SelectField("Status", choices=[("Open", "Open"), ("Closed", "Closed")], validators=[DataRequired()])  # สถานะ
    link = StringField("Link", validators=[DataRequired(),])                       # URL ของไฟล์
    submit = SubmitField("Submit")

# Edit Form
class EditForm(FlaskForm):
    create_date = StringField("Create Date", validators=[DataRequired()])             # วันที่และเวลา
    work_order = StringField("Work Order", validators=[DataRequired()])               # Work Order
    line_name = QuerySelectField(
        "Line Name",
        query_factory=lambda: Line.query.all(),  # ดึงข้อมูลจาก Line
        get_label="name",
        allow_blank=False,
        blank_text="Select Line",
        validators=[DataRequired()]
    )
    location_name = QuerySelectField(
        "Location Name",
        query_factory=lambda: Location.query.all(),  # ดึงข้อมูลจาก Location
        get_label="name",
        allow_blank=False,
        blank_text="Select Location"
    )
    device_type_name = QuerySelectField(
        "Device Type",
        query_factory=lambda: DeviceType.query.all(),  # ดึงข้อมูลจาก DeviceType
        get_label="name",
        allow_blank=False,
        blank_text="Select Device Type"
    )
    device_name = QuerySelectField(
        "Device Name",
        query_factory=lambda: DeviceName.query.all(),  # ดึงข้อมูลจาก DeviceName
        get_label="name",
        allow_blank=False,
        blank_text="Select Device Name"
    )
    description = TextAreaField("Description", validators=[DataRequired()])           # รายละเอียด
    report_by = StringField("Report By", validators=[DataRequired()])                 # ผู้รายงาน
    status = SelectField("Status", choices=[("Open", "Open"), ("Closed", "Closed")], validators=[DataRequired()])  # สถานะ
    link = StringField("Link", validators=[DataRequired(),])                       # URL ของไฟล์
    submit = SubmitField("Submit")