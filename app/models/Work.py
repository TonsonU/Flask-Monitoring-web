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

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from app.extensions import db

def now_utc():
    return datetime.now(timezone.utc)


# Model สำหรับ Work
class Work(db.Model):
    number = db.Column(db.Integer, primary_key=True, autoincrement=True)  # เลข 6 หลัก รันอัตโนมัติ
    create_date = db.Column(db.DateTime, default=now_utc)  # วันที่และเวลา สร้างอัตโนมัติ
    work_order = db.Column(db.String(50), nullable=False)          # Work Order
    # ForeignKey เชื่อมกับตารางอื่นๆ
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_type.id'), nullable=True)
    device_name_id = db.Column(db.Integer, db.ForeignKey('device_name.id'), nullable=True)
    description = db.Column(db.Text, nullable=False)               # รายละเอียด
    report_by = db.Column(db.String(50), nullable=False)           # ผู้รายงาน
    status = db.Column(db.String(20), nullable=False, default="open")  # สถานะ (ค่าเริ่มต้น: open)
    #action = db.Column(db.Text, nullable=True)                     # รายละเอียดของการดำเนินการ
    link = db.Column(db.String(255), nullable=True)           # URL ของไฟล์
    cause_id = db.Column(db.Integer, db.ForeignKey('cause.id'), nullable=True)  # ForeignKey เชื่อมกับ Cause
    point_casedetail_id = db.Column(db.Integer, db.ForeignKey('point_case_detail.id'), nullable=True)  # ForeignKey เชื่อมกับ PointCaseDetail


    # สร้างความสัมพันธ์
    line = db.relationship('Line', backref='works')
    location = db.relationship('Location', backref='works')
    device_type = db.relationship('DeviceType', backref='works')
    device_name = db.relationship('DeviceName', backref='works')
    cause = db.relationship('Cause', backref='works')
    point_casedetail = db.relationship('PointCaseDetail', backref='works')


    def __repr__(self):
        return f"<Work {self.number}>"