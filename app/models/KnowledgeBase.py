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

class KnowledgeBase(db.Model):
    number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_date = db.Column(db.DateTime, default=now_utc)
    device_type = db.Column(db.String(100))
    topic = db.Column(db.String(100))
    description = db.Column(db.String(100))
    create_by = db.Column(db.String(100))

    def __repr__(self):
        return f"<KnowledgeBase {self.number}>"
        