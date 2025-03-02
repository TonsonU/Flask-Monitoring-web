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
from app.models import DeviceName, DeviceType, Location, Line, SerialNumberHistory, ForceDataHistory, MacAddressHistory, ModuleHistory, db, Work
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
    """API: นับจำนวนงานซ่อมที่เสียบ่อยที่สุดตามอุปกรณ์ และแสดงชื่ออุปกรณ์"""
    
    device_counts = (
        db.session.query(DeviceType.name, db.func.count(Work.device_type_id))
        .join(DeviceType, DeviceType.id == Work.device_type_id)  # ✅ JOIN DeviceType
        .group_by(DeviceType.name)
        .order_by(db.func.count(Work.device_type_id).desc())
        .limit(10)  # ดึงแค่ 10 อันดับแรก
        .all()
    )

    print("🔍 DEBUG: Equipment Failure Data:", device_counts)  # ✅ Debug API

    data = {
        "labels": [device_name for device_name, count in device_counts],  # ✅ ใช้ชื่ออุปกรณ์แทน ID
        "values": [count for device_name, count in device_counts],
    }
    return jsonify(data)




@dashboard_bp.route("/api/pending_tasks_location", methods=["GET"])
def pending_tasks_location():
    """API: นับจำนวนงานที่ค้างอยู่ในแต่ละสถานที่ พร้อมดึงชื่อสถานที่"""
    
    location_counts = (
        db.session.query(Location.name, db.func.count(Work.location_id))
        .join(Location, Location.id == Work.location_id)  # ✅ JOIN Location
        .filter(Work.status == "Open")  # ✅ กรองเฉพาะงานที่ยังไม่เสร็จ
        .group_by(Location.name)
        .order_by(db.func.count(Work.location_id).desc())
        .limit(15)  # ✅ ดึงแค่ 15 อันดับแรก
        .all()
    )

    print("🔍 DEBUG: Pending Tasks by Location Data:", location_counts)  # ✅ Debug API

    data = {
        "labels": [location_name for location_name, count in location_counts],  # ✅ ใช้ชื่อสถานที่แทน ID
        "values": [count for location_name, count in location_counts],
    }
    return jsonify(data)

@dashboard_bp.route("/api/cm_by_line", methods=["GET"])
def cm_by_line():
    """API: นับจำนวนงาน CM แยกตาม Line"""
    line_counts = db.session.query(
        Line.name, db.func.count(Work.line_id)
    ).join(Work, Line.id == Work.line_id)  # JOIN ตาราง Work กับ Line
    line_counts = line_counts.group_by(Line.name).order_by(db.func.count(Work.line_id).desc()).all()

    # JSON Response
    data = {
        "labels": [line_name for line_name, count in line_counts],
        "values": [count for line_name, count in line_counts]
    }
    return jsonify(data)
