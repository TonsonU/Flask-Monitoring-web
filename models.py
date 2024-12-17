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

# Work Model
class Work(db.Model):
    number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    work_order = db.Column(db.String(50), nullable=False)
    equipment = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(50), nullable=False)
    report_by = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")
    action = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Work {self.number}>"
