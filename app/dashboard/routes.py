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
from app.models import DeviceName, DeviceType, Location, Line, SerialNumberHistory, ForceDataHistory, MacAddressHistory, ModuleHistory, db, Work,PointCaseDetail,Cause
from sqlalchemy import or_
from app.extensions import db
from . import dashboard_bp


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """เมื่อเข้า Dashboard ให้ Redirect ไปหน้า Overview"""
    return redirect(url_for('dashboard.overview_page'))

@dashboard_bp.route("/overview")
@login_required
def overview_page():
    """แสดงหน้า Overview"""
    total_cm = Work.query.count()
    open_cm = Work.query.filter_by(status="Open").count()
    close_cm = Work.query.filter_by(status="Closed").count()

    return render_template("dashboard/overview.html",
                           total_cm=total_cm,
                           open_cm=open_cm,
                           close_cm=close_cm)


@dashboard_bp.route("/location")
@login_required
def location_page():
    return render_template("dashboard/location.html")

@dashboard_bp.route("/equipment")
@login_required
def equipment_page():
    return render_template("dashboard/equipment.html")

@dashboard_bp.route("/tracking")
@login_required
def tracking_page():
    return render_template("dashboard/tracking.html")
    

@dashboard_bp.route("/api/overview_data")
def overview_data():
    """ API ส่งข้อมูลจำนวนงานซ่อม CM """
    data = {
        "total_cm": Work.query.count(),
        "open_cm": Work.query.filter_by(status="Open").count(),
        "close_cm": Work.query.filter_by(status="Closed").count(),
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


# Location.html
@dashboard_bp.route("/api/get_lines_locations", methods=["GET"])
def get_lines_locations():
    """ดึงข้อมูล Line ทั้งหมด + Location ตาม Line ID"""
    line_id = request.args.get("line_id")  # รับค่า line_id จาก dropdown

    # 📌 ดึงข้อมูล Line ทั้งหมด
    lines = db.session.query(Line.id, Line.name).all()
    lines_data = [{"id": line.id, "name": line.name} for line in lines]

    # 📌 ถ้ามี line_id ให้ดึง Location ของ Line นั้นเท่านั้น
    locations_data = []
    if line_id:
        locations = (
            db.session.query(Location.id, Location.name, Location.line_id)
            .filter(Location.line_id == line_id)
            .all()
        )
        locations_data = [
            {"id": loc.id, "name": loc.name, "line_id": loc.line_id} for loc in locations
        ]

    return jsonify({"lines": lines_data, "locations": locations_data})

@dashboard_bp.route("/api/get_cm_data", methods=["GET"])
def get_cm_data():
    """ดึงข้อมูล CM ตาม Location ID"""
    location_id = request.args.get("location_id")
    if not location_id:
        return jsonify({"labels": [], "values": []})

    cm_counts = (
        db.session.query(Work.status, db.func.count(Work.id))
        .filter(Work.location_id == location_id)
        .group_by(Work.status)
        .all()
    )

    labels = [status for status, count in cm_counts]
    values = [count for status, count in cm_counts]

    return jsonify({"labels": labels, "values": values})


@dashboard_bp.route("/api/get_work_by_location", methods=["GET"])
def get_work_by_location():
    """ดึงข้อมูล Work ตาม Location ID พร้อมแสดงชื่ออุปกรณ์"""
    location_id = request.args.get("location_id")

    if not location_id:
        print("❌ No location_id provided")
        return jsonify([])  # ถ้าไม่มี location_id ให้คืนค่าว่าง

    works = (
        db.session.query(
            Work.work_order,
            Work.status,
            DeviceType.name.label("device_type_name"),
            DeviceName.name.label("device_name_name"),
            Location.name.label("location_name"),  # ✅ ดึงชื่อ Location
            Work.description,
            Work.report_by
        )
        .join(DeviceType, DeviceType.id == Work.device_type_id, isouter=True)  # ✅ Join กับ DeviceType
        .join(DeviceName, DeviceName.id == Work.device_name_id, isouter=True)  # ✅ Join กับ DeviceName
        .join(Location, Location.id == Work.location_id)  # ✅ JOIN Location
        .filter(Work.location_id == location_id)
        .all()
    )

    print(f"✅ Fetched {len(works)} records for location_id={location_id}")
    for work in works:
        print(f"🔹 {work.work_order} | {work.device_type_name} | {work.device_name_name}")

    data = [
        {
            "work_order": work.work_order,
            "status": work.status,
            "device_type_name": work.device_type_name or "ไม่ระบุ",
            "device_name_name": work.device_name_name or "ไม่ระบุ",
            "location_name": work.location_name,  # ✅ เพิ่มชื่อ Location
            "description": work.description,
            "report_by": work.report_by,
        }
        for work in works
    ]

    return jsonify(data)

@dashboard_bp.route("/api/work_count_by_location", methods=["GET"])
def work_count_by_location():
    """API: ดึงจำนวนงานซ่อมทั้งหมด แยกตาม Location"""

    work_counts = (
        db.session.query(Location.id, Location.name, db.func.count(Work.number))
        .join(Work, Work.location_id == Location.id)  # ✅ Join ตาราง Work กับ Location
        .filter(Work.status == "Open")  # ✅ กรองเฉพาะงานที่ยังไม่เสร็จ
        .group_by(Location.id, Location.name)
        .order_by(db.func.count(Work.number).desc())  # ✅ เรียงจากมากไปน้อย
        .limit(10)
        .all()
    )

    # ✅ ส่งข้อมูลกลับในรูปแบบ JSON
    data = {
        "labels": [location_name for location_id, location_name, count in work_counts],
        "values": [count for location_id, location_name, count in work_counts],
        "location_ids": [location_id for location_id, location_name, count in work_counts],  # ✅ เพิ่ม location_id
    }
    return jsonify(data)


@dashboard_bp.route("/api/work_status_by_location", methods=["GET"])
def work_status_by_location():
    """API: ดึงข้อมูลสถานะงานซ่อมในแต่ละสถานที่ (แสดง Top 10)"""

    # ดึงข้อมูลจำนวนงาน "Open" และ "Close" ของแต่ละ Location
    work_counts = (
        db.session.query(
            Location.name,
            db.func.count(db.case((Work.status == "Open", 1))).label("open_count"),
            db.func.count(db.case((Work.status == "Closed", 1))).label("close_count"),
        )
        .join(Work, Work.location_id == Location.id)
        .group_by(Location.name)
        .order_by(db.func.count(Work.number).desc())  # เรียงจากสถานที่ที่มีงานมากที่สุด
        .limit(10)  # ดึงแค่ 10 อันดับแรก
        .all()
    )

    data = {
        "labels": [row.name for row in work_counts],
        "open_values": [row.open_count for row in work_counts],
        "close_values": [row.close_count for row in work_counts],
    }

    return jsonify(data)


# equipment.html

@dashboard_bp.route("/api/get_equipment_types_grouped", methods=["GET"])
def get_equipment_types_grouped():
    """API: ดึงรายการประเภทอุปกรณ์ทั้งหมด แต่รวมชื่อที่ซ้ำกัน"""

    # 📌 Query ดึงประเภทอุปกรณ์ทั้งหมด + Line ที่เกี่ยวข้อง
    equipment_types = (
        db.session.query(DeviceType.name, Line.name.label("line_name"), db.func.count(Work.number))
        .join(Work, Work.device_type_id == DeviceType.id)
        .join(Line, Work.line_id == Line.id)
        .group_by(DeviceType.name, Line.name)  # ✅ รวมชื่อที่ซ้ำกัน แต่แยกตาม Line
        .order_by(DeviceType.name, db.func.count(Work.number).desc())  # ✅ เรียงตามชื่อ
        .all()
    )
    print("🔍 DEBUG: Equipment Types Grouped Data:", equipment_types)

    # 📌 รวมชื่ออุปกรณ์เดียวกัน แต่แยกตาม Line
    grouped_data = {}
    for device_name, line_name, count in equipment_types:
        if device_name not in grouped_data:
            grouped_data[device_name] = []
        grouped_data[device_name].append({"line": line_name, "count": count})

    return jsonify(grouped_data)

@dashboard_bp.route("/api/work_trend_by_equipment", methods=["GET"])
def work_trend_by_equipment():
    """API: ดึงแนวโน้มจำนวนงานซ่อมของอุปกรณ์แยกตามปี"""

    equipment_name = request.args.get("equipment_name")  # รับค่า Equipment Name จาก Filter
    if not equipment_name:
        return jsonify({"labels": [], "values": []})
    print("🔍 DEBUG: Equipment Name:", equipment_name)

    work_trend = (
        db.session.query(
            db.func.strftime("%Y", Work.create_date).label("year"),  # ดึงปีจาก created_at
            db.func.count(Work.number).label("work_count")
        )
        .join(DeviceType, DeviceType.id == Work.device_type_id)  # ✅ JOIN เพื่อดึงชื่ออุปกรณ์
        .filter(DeviceType.name == equipment_name)  # ✅ กรองตามชื่ออุปกรณ์
        .group_by("year")  # ✅ จัดกลุ่มตามปี
        .order_by("year")  # ✅ เรียงตามปี
        .all()
    )

    data = {
        "labels": [year for year, count in work_trend],  # 📌 ปี
        "values": [count for year, count in work_trend]  # 📌 จำนวนงานซ่อม
    }
    return jsonify(data)

@dashboard_bp.route("/api/work_years_by_equipment", methods=["GET"])
def get_years_by_equipment():
    equipment_name = request.args.get("equipment_name")
    if not equipment_name:
        return jsonify([])

    years = (
        db.session.query(db.func.strftime("%Y", Work.create_date))
        .join(DeviceType, DeviceType.id == Work.device_type_id)
        .filter(DeviceType.name == equipment_name)
        .distinct()
        .order_by(db.func.strftime("%Y", Work.create_date))
        .all()
    )

    return jsonify([year for (year,) in years])


@dashboard_bp.route("/api/work_trend_by_month", methods=["GET"])
def work_trend_by_month():
    equipment_name = request.args.get("equipment_name")
    selected_year = request.args.get("year")

    if not equipment_name or not selected_year:
        return jsonify({"labels": [], "values": []})

    results = (
        db.session.query(
            db.func.strftime("%m", Work.create_date).label("month"),
            db.func.count(Work.number)
        )
        .join(DeviceType, DeviceType.id == Work.device_type_id)
        .filter(DeviceType.name == equipment_name)
        .filter(db.func.strftime("%Y", Work.create_date) == selected_year)
        .group_by("month")
        .order_by("month")
        .all()
    )

    # ให้แน่ใจว่ามีครบทุกเดือน
    month_map = {f"{i:02}": 0 for i in range(1, 13)}
    for month, count in results:
        month_map[month] = count

    return jsonify({
        "labels": [f"{i:02}" for i in range(1, 13)],
        "values": list(month_map.values())
    })



@dashboard_bp.route("/api/breakdown_by_equipment", methods=["GET"])
def breakdown_by_equipment():
    """API: ดึงจำนวนงานซ่อมของ Device Name ตาม Device Type (ไม่แยกตามปี)"""

    equipment_name = request.args.get("device_type_id")
    print("🔍 DEBUG: Device Type ID:", equipment_name)
    
    if not equipment_name:
        return jsonify({"labels": [], "values": []})

    breakdown_data = (
        db.session.query(DeviceName.name, db.func.count(Work.device_name_id))
        .join(Work, Work.device_name_id == DeviceName.id)  # ✅ JOIN Work กับ DeviceName
        .join(DeviceType, DeviceType.id == DeviceName.device_type_id)  # ✅ JOIN DeviceType
        .filter(DeviceType.name == equipment_name)  # ✅ กรองตามประเภทอุปกรณ์
        .group_by(DeviceName.name)  # ✅ รวม Device Name ที่ซ้ำกัน
        .order_by(db.func.count(Work.device_name_id).desc())  # ✅ เรียงจากมากไปน้อย
        .all()
    )
    print("🔍 DEBUG: Breakdown Data:", breakdown_data)


    data = {
        "labels": [device_name for device_name, count in breakdown_data],  # 📌 ชื่ออุปกรณ์
        "values": [count for device_name, count in breakdown_data],  # 📌 จำนวนงานซ่อมของอุปกรณ์
    }

    return jsonify(data)

@dashboard_bp.route("/api/device_location_breakdown", methods=["GET"])
def device_location_breakdown():
    """API: ดึงจำนวนงานซ่อมของ Device Name (ภายใต้ Device Type ที่เลือก) แยกตาม Location"""

    device_type_name = request.args.get("device_name")  # 🔍 จริงๆ คือ DeviceType.name
    print("🔍 DEBUG: Device Type Name:", device_type_name)

    if not device_type_name:
        return jsonify({"labels": [], "values": []})

    # 📌 ดึงจำนวนงานซ่อมโดยรวมของอุปกรณ์ใน DeviceType นั้น แยกตาม Location
    breakdown = (
        db.session.query(Location.name, db.func.count(Work.number))
        .join(Work, Work.location_id == Location.id)
        .join(DeviceName, Work.device_name_id == DeviceName.id)
        .join(DeviceType, DeviceType.id == DeviceName.device_type_id)
        .filter(DeviceType.name == device_type_name)
        .group_by(Location.name)
        .order_by(db.func.count(Work.number).desc())
        .all()
    )

    print("🔍 DEBUG: Breakdown =", breakdown)

    data = {
        "labels": [loc for loc, count in breakdown],
        "values": [count for loc, count in breakdown]
    }
    return jsonify(data)


@dashboard_bp.route("/api/point_case_breakdown", methods=["GET"])
def point_case_breakdown():
    """API: ดึงจำนวนเคสของอุปกรณ์ประเภท 'Point' โดยแยกตาม PointCaseDetail"""

    # 🔍 ดึง DeviceType.id ทั้งหมดที่ชื่อ "Point"
    point_type_ids = [
        dt.id for dt in DeviceType.query.filter(DeviceType.name == "Point").all()
    ]
    print("✅ Point DeviceType IDs:", point_type_ids)

    if not point_type_ids:
        return jsonify({"labels": [], "values": []})

    # 🔧 ดึงจำนวนงานที่เป็น Point Case โดย group ตามชื่อเคส
    results = (
        db.session.query(PointCaseDetail.name, db.func.count(Work.number))
        .join(Work, Work.point_casedetail_id == PointCaseDetail.id)
        .filter(Work.device_type_id.in_(point_type_ids))  # ✅ แทนที่จะใช้แค่ตัวเดียว
        .group_by(PointCaseDetail.name)
        .order_by(db.func.count(Work.number).desc())
        .all()
    )

    print("🔍 DEBUG: Point case:", results)

    data = {
        "labels": [name for name, count in results],
        "values": [count for name, count in results]
    }

    return jsonify(data)

@dashboard_bp.route("/api/cause_case_breakdown", methods=["GET"])
def cause_case_breakdown():
    """API: ดึงจำนวนเคสโดยแยกตาม Cause"""

    results = (
        db.session.query(Cause.name, db.func.count(Work.number))
        .join(Work, Work.cause_id == Cause.id)
        .group_by(Cause.name)
        .order_by(db.func.count(Work.number).desc())
        .all()
    )

    print("🔍 DEBUG: Case:", results)

    data = {
        "labels": [name for name, count in results],
        "values": [count for name, count in results]
    }

    return jsonify(data)
