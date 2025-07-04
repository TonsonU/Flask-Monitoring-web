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

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'), nullable=False)
    line = db.relationship('Line', backref=db.backref('locations', lazy=True))

    def __repr__(self):
        return f"<Location {self.name}>"