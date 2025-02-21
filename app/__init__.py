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

from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate, bootstrap
from app.models import User
from app.auth import auth_bp
from app.main import main_bp
from app.work import work_bp
from app.inventory import inventory_bp
from app.knowledge_base import knowledge_bp
from app.clear_tables import clear_tables_bp
from app.filters import datetime_bangkok

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Flask Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ✅ ลงทะเบียน filter
    app.jinja_env.filters['datetime_bangkok'] = datetime_bangkok

    # ลงทะเบียน Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(work_bp, url_prefix='/work')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge_base')
    app.register_blueprint(clear_tables_bp, url_prefix='/clear_tables')
    app.add_template_filter(datetime_bangkok, 'datetime_bangkok')

    return app
