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