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

# app.py: เป็นไฟล์หลักที่รวมทุกอย่าง

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from config import Config
from models import db, User
from filters import datetime_bangkok
from Blueprints import init_app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ลงทะเบียน filter
    app.add_template_filter(datetime_bangkok, name='datetime_bangkok')

    # ตั้งค่าฐานข้อมูล
    db.init_app(app)
    migrate = Migrate(app, db)

    # ตั้งค่า Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    Bootstrap(app)

    # ลงทะเบียน Blueprints
    init_app(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
