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