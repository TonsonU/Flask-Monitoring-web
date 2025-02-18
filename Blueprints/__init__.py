from .auth import auth_bp
from .main import main_bp
from .work import work_bp
from .inventory import inventory_bp
from .knowledge_base import knowledge_bp
from.clear_tables import clear_tables_bp

def init_app(app):
    """ลงทะเบียน Blueprints ทั้งหมดในแอป"""
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(work_bp, url_prefix='/work')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(knowledge_bp, url_prefix='/knowledge_base')
    app.register_blueprint(clear_tables_bp, url_prefix='/clear_tables')
