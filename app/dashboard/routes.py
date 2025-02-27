# app/dashboard/routes.py
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

from flask import Blueprint, render_template,request, url_for, flash, redirect, jsonify, current_app
from flask_login import login_required,current_user
from app.models import DeviceName, DeviceType, SerialNumberHistory, ForceDataHistory, MacAddressHistory, ModuleHistory, db, Work
from sqlalchemy import or_
from app.extensions import db
from . import dashboard_bp


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """ แสดงหน้า Dashboard """
    return render_template('dashboard.html') # แก้ไขตรงนี้

@dashboard_bp.route('/api/work_data')
def work_data():
    """ ดึงข้อมูล Work และสามารถกรองตามวันที่ """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Work.query
    if start_date and end_date:
        query = query.filter(Work.create_date.between(start_date, end_date))
    
    works = query.all()

    data = {
        "labels": [],
        "values": []
    }

    work_status_count = {}
    for work in works:
        status = work.status
        if status not in work_status_count:
            work_status_count[status] = 0
        work_status_count[status] += 1

    data["labels"] = list(work_status_count.keys())
    data["values"] = list(work_status_count.values())

    return jsonify(data)
