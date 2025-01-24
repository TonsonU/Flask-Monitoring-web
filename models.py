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


# สร้างตัวแปร db เพื่อใช้ในการสร้างฐานข้อมูล
db = SQLAlchemy()

def now_utc():
    return datetime.now(timezone.utc)

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

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

    # สร้างความสัมพันธ์
    line = db.relationship('Line', backref='works')
    location = db.relationship('Location', backref='works')
    device_type = db.relationship('DeviceType', backref='works')
    device_name = db.relationship('DeviceName', backref='works')

    def __repr__(self):
        return f"<Work {self.number}>"


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

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey('work.number'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=now_utc, nullable=False)
    pdf_url = db.Column(db.String(255), nullable=True)  # URL ของ PDF (สามารถเว้นว่างได้)
    image_url = db.Column(db.String(255), nullable=True)  # URL ของรูปภาพ (สามารถเว้นว่างได้)
    user = db.relationship('User', backref='comments')
    work = db.relationship('Work', backref='comments')

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

class KnowledgeBase(db.Model):
    number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_date = db.Column(db.DateTime, default=now_utc)
    device_type = db.Column(db.String(100))
    topic = db.Column(db.String(100))
    description = db.Column(db.String(100))
    create_by = db.Column(db.String(100))

    def __repr__(self):
        return f"<KnowledgeBase {self.number}>"
        