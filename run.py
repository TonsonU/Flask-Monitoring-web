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

from app import create_app,db
from flask_wtf.csrf import CSRFProtect

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)

csrf = CSRFProtect(app)

