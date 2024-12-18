# app.py: เป็นไฟล์หลักที่รวมทุกอย่าง
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
from models import db,User
from routes import init_app
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

# กำหนดการตั้งค่าฐานข้อมูล
db.init_app(app)
# เชื่อมต่อ db และ Migrate
migrate = Migrate(app, db)

# ตั้งค่า Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # กำหนดชื่อ route สำหรับหน้า login

# ฟังก์ชัน user_loader ที่ใช้ในการโหลดผู้ใช้จากฐานข้อมูล
@login_manager.user_loader
def load_user(user_id):      # โหลดผู้ใช้จากฐานข้อมูลตาม user_id
    return User.query.get(int(user_id))

# เริ่มใช้งาน Flask-Bootstrap
Bootstrap(app)

# Initialize routes
init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
