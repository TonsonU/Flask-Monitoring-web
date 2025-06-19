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
from app.extensions import db
from app.models import Work
from . import main_bp

@main_bp.route('/')
@login_required
def index():
    #works = Work.query.all()
    works = Work.query.order_by(
        db.case(
            (Work.status == 'Open', 0),
            (Work.status == 'Closed', 1),
            else_=2
        ),
        Work.create_date.desc()
    ).all()
    return render_template("index.html", works=works)
