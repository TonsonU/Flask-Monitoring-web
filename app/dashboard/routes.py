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
    total_cm = Work.query.count()  # นับจำนวนงานทั้งหมด
    open_cm = Work.query.filter_by(status="Open").count()  # งานที่กำลังดำเนินการ
    close_cm = Work.query.filter_by(status="Close").count()  # งานที่เสร็จแล้ว

    return render_template("dashboard/dashboard.html", 
                           total_cm=total_cm,
                           open_cm=open_cm,
                           close_cm=close_cm)

@dashboard_bp.route("/api/overview_data")
def overview_data():
    """ API ส่งข้อมูลจำนวนงานซ่อม CM """
    data = {
        "total_cm": Work.query.count(),
        "open_cm": Work.query.filter_by(status="Open").count(),
        "close_cm": Work.query.filter_by(status="Close").count(),
    }
    return jsonify(data)


@dashboard_bp.route("/api/equipment_failure", methods=["GET"])
def equipment_failure():
    """API: นับจำนวนงานซ่อมที่เสียบ่อยที่สุดตามอุปกรณ์"""
    device_counts = db.session.query(
        Work.device_type_id, db.func.count(Work.device_type_id)
    ).group_by(Work.device_type_id).order_by(db.func.count(Work.device_type_id).desc()).limit(10).all()

    print("🔍 DEBUG: Equipment Failure Data:", device_counts)  # ✅ Debug API

    data = {
        "labels": [f"อุปกรณ์ {device_id}" for device_id, count in device_counts],
        "values": [count for device_id, count in device_counts],
    }
    return jsonify(data)



@dashboard_bp.route("/api/pending_tasks_location")
def pending_tasks_location():
    """API: นับจำนวนงานที่ค้างอยู่ในแต่ละสถานที่"""
    location_counts = db.session.query(
        Work.location_id, db.func.count(Work.location_id)
    ).filter(Work.status == "Open").group_by(Work.location_id).order_by(db.func.count(Work.location_id).desc()).limit(15).all()

    data = {
        "labels": [f"สถานที่ {location_id}" for location_id, count in location_counts],
        "values": [count for location_id, count in location_counts],
    }
    return jsonify(data)

