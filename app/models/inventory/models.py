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


# สร้างตัวแปร db เพื่อใช้ในการสร้างฐานข้อมูล
db = SQLAlchemy()

def now_utc():
    return datetime.now(timezone.utc)

class Line(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Line {self.name}>"

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'), nullable=False)
    line = db.relationship('Line', backref=db.backref('locations', lazy=True))

    def __repr__(self):
        return f"<Location {self.name}>"

class DeviceType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'), nullable=False)
    line = db.relationship('Line', backref=db.backref('device_types', lazy=True))

    def __repr__(self):
        return f"<DeviceType {self.name}>"

class DeviceName(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_type.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    device_type = db.relationship('DeviceType', backref=db.backref('device_names', lazy=True))
    location = db.relationship('Location', backref=db.backref('device_names', lazy=True))
    bound = db.Column(db.String(100), nullable=True)
    inandout = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    mac_address = db.Column(db.String(17), nullable=True)
    channel = db.Column(db.String(50), nullable=True)
    device_role = db.Column(db.String(50), nullable=True)
    force_data = db.Column(db.String(50), nullable=True)
    vac_white = db.Column(db.String(50), nullable=True)
    current_white = db.Column(db.String(50), nullable=True)
    vac_red = db.Column(db.String(50), nullable=True)
    current_red = db.Column(db.String(50), nullable=True)
    vac_yellow = db.Column(db.String(50), nullable=True)
    current_yellow = db.Column(db.String(50), nullable=True)
    f1_f2 = db.Column(db.String(50), nullable=True)
    red_module = db.Column(db.String(50), nullable=True)
    white_module = db.Column(db.String(50), nullable=True)
    yellow_module = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<DeviceName {self.name}>'
    
class SerialNumberHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device_name.id'), nullable=False)
    old_serial_number = db.Column(db.String(100), nullable=True)
    new_serial_number = db.Column(db.String(100), nullable=True)
    changed_at = db.Column(db.DateTime, default=now_utc, nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    remark = db.Column(db.String(100), nullable=True)

    device = db.relationship('DeviceName', backref=db.backref('serial_number_histories', lazy=True))
    user = db.relationship('User', backref=db.backref('serial_number_changes', lazy=True))

    def __repr__(self):
        return f"<SerialNumberHistory DeviceID: {self.device_id}, Changed At: {self.changed_at}>"

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


class MacAddressHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device_name.id'), nullable=False)
    old_mac_address = db.Column(db.String(17), nullable=True)
    new_mac_address = db.Column(db.String(17), nullable=True)
    changed_at = db.Column(db.DateTime, default=now_utc, nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    remark = db.Column(db.String(100), nullable=True)

    device = db.relationship('DeviceName', backref=db.backref('mac_address_histories', lazy=True))
    user = db.relationship('User', backref=db.backref('mac_address_changes', lazy=True))

    def __repr__(self):
        return f"<MacAddressHistory DeviceID: {self.device_id}, Changed At: {self.changed_at}>"
    
class ModuleHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device_name.id'), nullable=False)
    old_red_module = db.Column(db.String(100), nullable=True)
    new_red_module = db.Column(db.String(100), nullable=True)
    old_white_module = db.Column(db.String(100), nullable=True)
    new_white_module = db.Column(db.String(100), nullable=True)
    old_yellow_module = db.Column(db.String(100), nullable=True)
    new_yellow_module = db.Column(db.String(100), nullable=True)
    changed_at = db.Column(db.DateTime, default=now_utc, nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    remark = db.Column(db.String(255), nullable=True)

    device = db.relationship('DeviceName', backref=db.backref('module_histories', lazy=True))
    user = db.relationship('User', backref=db.backref('module_changes', lazy=True))

    def __repr__(self):
        return f"<ModuleHistory DeviceID: {self.device_id}, Changed At: {self.changed_at}>"


        