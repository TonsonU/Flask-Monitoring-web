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
# models.py: เก็บโมเดลที่เกี่ยวข้องกับฐานข้อมูล
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from app.extensions import db

def now_utc():
    return datetime.now(timezone.utc)

class ForceDataHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    device_id = db.Column(db.Integer, db.ForeignKey('device_name.id'), nullable=False)  # Foreign Key เชื่อมกับ DeviceName
    plus_before = db.Column(db.String(100), nullable=False)  # ค่าก่อนการเปลี่ยนแปลง (บวก)
    minus_before = db.Column(db.String(100), nullable=False)  # ค่าก่อนการเปลี่ยนแปลง (ลบ)
    plus_after = db.Column(db.String(100), nullable=True)  # ค่าหลังการเปลี่ยนแปลง (บวก)
    minus_after = db.Column(db.String(100), nullable=True)  # ค่าหลังการเปลี่ยนแปลง (ลบ)
    changed_at = db.Column(db.DateTime, default=now_utc, nullable=False)  # เวลาที่เปลี่ยนแปลง
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign Key เชื่อมกับ User
    remark = db.Column(db.String(255), nullable=True)  # คำอธิบายเพิ่มเติม

    # ความสัมพันธ์กับ DeviceName และ User
    device = db.relationship('DeviceName', backref='force_data_histories', lazy=True)
    user = db.relationship('User', backref='force_data_changes', lazy=True)

    def __repr__(self):
        return f"<ForceDataHistory DeviceID: {self.device_id}, Changed At: {self.changed_at}>"