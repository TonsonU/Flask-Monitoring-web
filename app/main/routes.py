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

from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Work

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    works = Work.query.all()
    return render_template("main/index.html", works=works)
