# models.py: เก็บโมเดลที่เกี่ยวข้องกับฐานข้อมูล
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


# สร้างตัวแปร db เพื่อใช้ในการสร้างฐานข้อมูล
db = SQLAlchemy()


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
    create_date = db.Column(db.DateTime, default=datetime.utcnow)  # วันที่และเวลา สร้างอัตโนมัติ
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
    bound = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<DeviceName {self.name}>"
    
class SerialNumberHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device_name.id'), nullable=False)
    old_serial_number = db.Column(db.String(100), nullable=True)
    new_serial_number = db.Column(db.String(100), nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    remark = db.Column(db.String(100), nullable=True)

    device = db.relationship('DeviceName', backref=db.backref('serial_number_histories', lazy=True))
    user = db.relationship('User', backref=db.backref('serial_number_changes', lazy=True))

    def __repr__(self):
        return f"<SerialNumberHistory DeviceID: {self.device_id}, Changed At: {self.changed_at}>"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey('work.number'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='comments')
    work = db.relationship('Work', backref='comments')