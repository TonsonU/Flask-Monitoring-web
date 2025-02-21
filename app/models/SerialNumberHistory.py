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