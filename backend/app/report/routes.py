####################################################
# Flask Monitoring Web
#
# 
# Project : Python, Flask, MySQLite, Bootstrap
# Author  : Thanapoom Sukarin
# Modifier: 
# Version : 
# Date    : Dec 01, 2024
#
####################################################

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, send_file
from flask_login import login_required, current_user
import pytz
from pytz import timezone
from datetime import datetime
from app.extensions import db
from . import report_bp
from werkzeug.utils import secure_filename
import tempfile
import uuid
import os
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Cm


leaders = [
    "Boonlom R",
    "Bhasit  B",
    "Kritsana D",
    "Thanawat K",
    "Tonson U",
    "Thanapoom S",
    "Jirayut J",
    "Amornthep T",
    "Naratip C",
    "Nakarin K",
    "Jittaphon N",
    "Pongsakorn I",
    "Sutee L",
    "Apichai O",
    "Danusit N"
]
apostles = leaders

@report_bp.context_processor
def inject_names():
    return dict(leaders=leaders, apostles=apostles)

@report_bp.route('/main')
@login_required
def main():
    return render_template('report.html') 

@report_bp.route('/point_y1_form')
def point_y1_form():
    return render_template('point_y1_form.html')

@report_bp.route("/generate_point_y1_pdf", methods=["POST"])
def generate_point_y1_pdf():
    context = {}

    # ========== Section 1: ข้อมูลทั่วไป ==========
    text_fields = [
        'leaders', 'date', 'coordinate', 'station', 'location', 'apostles', 'work_description', 'time1', 'time2', 'apostles'
    ]
    for field in text_fields:
        context[field] = request.form.get(field, "")

    # Members (person1, person2, ..., person7)
    for i in range(1, 8):
        context[f"person{i}"] = request.form.get(f"person{i}", "")

    # Work orders (work1, work2, ..., work7)
    for i in range(1, 8):
        context[f"work{i}"] = request.form.get(f"work{i}", "")

    # TPR numbers (tpr1, tpr2, ..., tpr4)
    for i in range(1, 5):
        context[f"tpr{i}"] = request.form.get(f"tpr{i}", "")

    # Checkbox กลุ่มแรก
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    checkbox_fields = [
        'station_in', 'station_out', 'borrow_earthing', 'borrow_voltage', 'borrow_item',
        'return_item', 'track_in', 'track_out'
    ]
    for field in checkbox_fields:
        context[field] = markbox(field)

    # ========== Section 2: ตารางงาน Point Machine (30 งาน) ==========
    special_rows = [3, 4, 7]

    for row in range(1, 31):
        for col in range(1, 5):
            if row == 1:
                # ✅ ข้อ 1: ใช้ input text
                context[f"poi1_{col}_{row}"] = request.form.get(f"poi1_{col}_{row}", "")
            elif row in special_rows:
                # ✅ ข้อ 3, 4, 7: ใช้ checkbox (key มี _1 ต่อท้าย)
                context[f"poi1_{col}_{row}_1"] = markbox(f"poi1_{col}_{row}_1")
            else:
                # ✅ ข้ออื่น: ใช้ checkbox แบบปกติ
                context[f"poi1_{col}_{row}"] = markbox(f"poi1_{col}_{row}")

    # Row พิเศษ: ข้อ 3, 4, 7 ที่มีแถวเสริม
    special_rows = [3, 4, 7]
    for row in special_rows:
        # sub-row 1: ย้ำให้แน่ใจว่าอ่าน markbox อีกครั้ง (สำคัญมาก)
        for col in range(1, 5):
            context[f"poi1_{col}_{row}"] = markbox(f"poi1_{col}_{row}")

        # sub-row 2,3 (และ 4,5 เฉพาะข้อ 7): อ่านเป็น text
        for sub in range(2, 6 if row == 7 else 4):
            for col in range(1, 5):
                context[f"poi1_{col}_{row}_{sub}"] = request.form.get(f"poi1_{col}_{row}_{sub}", "")

    # ✅ เพิ่ม remark แยกต่อข้อ
    for row in range(1, 31):
        context[f"remark1_{row}"] = request.form.get(f"remark1_{row}", "")

    # ========== Section 3: Force & Mark Center Table ==========
    for i in range(1, 5):  # 4 แถว
        context[f"poi_{i}"] = request.form.get(f"poi_{i}", "")
        for j in range(1, 9):  # 8 ช่อง
            context[f"poi2_{i}_{j}"] = request.form.get(f"poi2_{i}_{j}", "")

    # ========== Section 4: Contact Resistance, Voltage, Current Table ==========
    for i in range(1, 5):  # 4 rows
        context[f"poi_{i}"] = request.form.get(f"poi_{i}", "")
        for side in [1, 2]:  # Plus (+) and Minus (-)
            for j in range(1, 13):
                context[f"poi3_{i}_{side}_{j}"] = request.form.get(f"poi3_{i}_{side}_{j}", "")

    # ========== Section 5: Contact Force 1-10 ==========
    for i in range(1, 41):  # i = 1 ถึง 40
        for poi in range(1, 5):  # 4 POs
            context[f"poi4_{poi}_{i}"] = request.form.get(f"poi4_{poi}_{i}", "")

    # ========== Section 6: Other Issues ==========
    for i in range(1, 6):
        context[f"other_issue_{i}"] = request.form.get(f"other_issue_{i}", "")

    # ========== Render Word Template (สร้าง doc ก่อนใช้) ==========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "docx_templates", "Point (Y1).docx")
    doc = DocxTemplate(template_path)

    # ========== Section 7: แนบรูป ==========
    image_keys = ['work_picture_1', 'work_picture_2', 'work_picture_3', 'work_picture_4']  # ตามชื่อใน template.docx

    for key in image_keys:
        file = request.files.get(key)
        if file and file.filename:
            temp_dir = tempfile.mkdtemp()
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, safe_filename)
            file.save(file_path)
            context[key] = InlineImage(doc, file_path, width=Cm(6))
        else:
            context[key] = ""

    # ========== สร้าง Word จาก context ==========
    doc.render(context)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    # ---------- ✨ สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ ✨ ----------
    today_str = datetime.today().strftime("%Y-%m-%d")             # YYYY-MM-DD
    job_name   = context.get("work_description", "Job")
    location   = context.get("location", "Location")
    # ป้องกันอักขระต้องห้ามในชื่อไฟล์ (Windows ฯลฯ)
    job_name = secure_filename(job_name) or "Job"
    location = secure_filename(location) or "Location"

    download_filename = (
        f"KK-{today_str} PM (Y1) Point {job_name} At {location}.docx"
    )

    # ---------- ส่งไฟล์ให้ดาวน์โหลด ----------

    return send_file(temp_path.name, as_attachment=True, download_name=download_filename)

@report_bp.route('/point_m6_form')
def point_m6_form():
    return render_template('point_m6_form.html')

@report_bp.route("/generate_point_m6_pdf", methods=["POST"])
def generate_point_m6_pdf():
    context = {}

    # ========== Section 1: ข้อมูลทั่วไป ==========
    text_fields = [
        'leaders', 'date', 'coordinate', 'station', 'location', 'apostles', 'work_description', 'time1', 'time2', 'apostles'
    ]
    for field in text_fields:
        context[field] = request.form.get(field, "")

    # Members (person1, person2, ..., person7)
    for i in range(1, 8):
        context[f"person{i}"] = request.form.get(f"person{i}", "")

    # Work orders (work1, work2, ..., work7)
    for i in range(1, 8):
        context[f"work{i}"] = request.form.get(f"work{i}", "")

    # TPR numbers (tpr1, tpr2, ..., tpr4)
    for i in range(1, 5):
        context[f"tpr{i}"] = request.form.get(f"tpr{i}", "")

    # Checkbox กลุ่มแรก
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    checkbox_fields = [
        'station_in', 'station_out', 'borrow_earthing', 'borrow_voltage', 'borrow_item',
        'return_item', 'track_in', 'track_out'
    ]
    for field in checkbox_fields:
        context[field] = markbox(field)

    # ========== Section 2: ตารางงาน Point Machine (30 งาน) ==========
    # ปรับให้ข้อ 6 (เดิมข้อ 7) เป็น special row แทน
    special_rows = [3, 4, 6]

    for i in range(1, 5):  # 4 แถว
        context[f"poi_{i}"] = request.form.get(f"poi_{i}", "")

    for row in range(1, 23):
        for col in range(1, 5):
            if row == 1:
                # ✅ ข้อ 1: ใช้ input text
                context[f"poi1_{col}_{row}"] = request.form.get(f"poi1_{col}_{row}", "")
            elif row in special_rows:
                # ✅ ข้อ 3, 4, 6: ใช้ checkbox (key มี _1 ต่อท้าย)
                context[f"poi1_{col}_{row}_1"] = markbox(f"poi1_{col}_{row}_1")
            else:
                # ✅ ข้ออื่น: ใช้ checkbox แบบปกติ
                context[f"poi1_{col}_{row}"] = markbox(f"poi1_{col}_{row}")

    # Row พิเศษ: ข้อ 3, 4, 6 ที่มีแถวเสริม (ข้อ 6 มี 5 แถว)
    special_rows = [3, 4, 6]
    for row in special_rows:
        # sub-row 1: อ่าน markbox ซ้ำ
        for col in range(1, 5):
            context[f"poi1_{col}_{row}"] = markbox(f"poi1_{col}_{row}")

        # sub-row 2–5 (ข้อ 6 เดิมคือข้อ 7 มี 5 แถว)
        for sub in range(2, 6 if row == 6 else 4):
            for col in range(1, 5):
                context[f"poi1_{col}_{row}_{sub}"] = request.form.get(f"poi1_{col}_{row}_{sub}", "")

    # ✅ เพิ่ม remark แยกต่อข้อ (รวม remark1_6, remark1_7)
    for row in range(1, 23):
        context[f"remark1_{row}"] = request.form.get(f"remark1_{row}", "")

    # ========== Section 4: Contact Resistance, Voltage, Current Table ==========
    for i in range(1, 5):  # 4 rows
        context[f"poi_{i}"] = request.form.get(f"poi_{i}", "")
        for side in [1, 2]:  # Plus (+) and Minus (-)
            for j in range(1, 13):
                context[f"poi3_{i}_{side}_{j}"] = request.form.get(f"poi3_{i}_{side}_{j}", "")

    # ========== Section 6: Other Issues ==========
    for i in range(1, 6):
        context[f"other_issue_{i}"] = request.form.get(f"other_issue_{i}", "")

    # ========== Render Word Template (สร้าง doc ก่อนใช้) ==========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "docx_templates", "Point (M6).docx")
    doc = DocxTemplate(template_path)

    # ========== Section 7: แนบรูป ==========
    image_keys = ['work_picture_1', 'work_picture_2', 'work_picture_3', 'work_picture_4']  # ตามชื่อใน template.docx

    for key in image_keys:
        file = request.files.get(key)
        if file and file.filename:
            temp_dir = tempfile.mkdtemp()
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, safe_filename)
            file.save(file_path)
            context[key] = InlineImage(doc, file_path, width=Cm(6))
        else:
            context[key] = ""

    # ========== สร้าง Word จาก context ==========
    doc.render(context)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    # ---------- ✨ สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ ✨ ----------
    today_str = datetime.today().strftime("%Y-%m-%d")             # YYYY-MM-DD
    job_name   = context.get("work_description", "Job")
    location   = context.get("location", "Location")
    # ป้องกันอักขระต้องห้ามในชื่อไฟล์ (Windows ฯลฯ)
    job_name = secure_filename(job_name) or "Job"
    location = secure_filename(location) or "Location"

    download_filename = (
        f"KK-{today_str} PM (M6) Point {job_name} At {location}.docx"
    )

    # ---------- ส่งไฟล์ให้ดาวน์โหลด ----------

    return send_file(temp_path.name, as_attachment=True, download_name=download_filename)

@report_bp.route('/point_m2_form')
def point_m2_form():
    return render_template('point_m2_form.html')

@report_bp.route("/generate_point_m2_pdf", methods=["POST"])
def generate_point_m2_pdf():
    context = {}

    # ========== Section 1: ข้อมูลทั่วไป ==========
    text_fields = [
        'leaders', 'date', 'coordinate', 'station', 'location', 'apostles', 'work_description', 'time1', 'time2', 'apostles'
    ]
    for field in text_fields:
        context[field] = request.form.get(field, "")

    # Members (person1, person2, ..., person7)
    for i in range(1, 8):
        context[f"person{i}"] = request.form.get(f"person{i}", "")

    # Work orders (work1, work2, ..., work7)
    for i in range(1, 8):
        context[f"work{i}"] = request.form.get(f"work{i}", "")

    # TPR numbers (tpr1, tpr2, ..., tpr4)
    for i in range(1, 5):
        context[f"tpr{i}"] = request.form.get(f"tpr{i}", "")

    # Checkbox กลุ่มแรก
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    checkbox_fields = [
        'station_in', 'station_out', 'borrow_earthing', 'borrow_voltage', 'borrow_item',
        'return_item', 'track_in', 'track_out'
    ]
    for field in checkbox_fields:
        context[field] = markbox(field)

    # ========== Section 2: ตารางงาน Point Machine (30 งาน) ==========
    # ปรับให้ข้อ 6 (เดิมข้อ 7) เป็น special row แทน
    special_rows = [3, 4, 6]

    for i in range(1, 5):  # 4 แถว
        context[f"poi_{i}"] = request.form.get(f"poi_{i}", "")

    for row in range(1, 23):
        for col in range(1, 5):
            if row == 1:
                # ✅ ข้อ 1: ใช้ input text
                context[f"poi1_{col}_{row}"] = request.form.get(f"poi1_{col}_{row}", "")
            elif row in special_rows:
                # ✅ ข้อ 3, 4, 6: ใช้ checkbox (key มี _1 ต่อท้าย)
                context[f"poi1_{col}_{row}_1"] = markbox(f"poi1_{col}_{row}_1")
            else:
                # ✅ ข้ออื่น: ใช้ checkbox แบบปกติ
                context[f"poi1_{col}_{row}"] = markbox(f"poi1_{col}_{row}")

    # Row พิเศษ: ข้อ 3, 4, 6 ที่มีแถวเสริม (ข้อ 6 มี 5 แถว)
    special_rows = [3, 4, 6]
    for row in special_rows:
        # sub-row 1: อ่าน markbox ซ้ำ
        for col in range(1, 5):
            context[f"poi1_{col}_{row}"] = markbox(f"poi1_{col}_{row}")

        # sub-row 2–5 (ข้อ 6 เดิมคือข้อ 7 มี 5 แถว)
        for sub in range(2, 6 if row == 6 else 4):
            for col in range(1, 5):
                context[f"poi1_{col}_{row}_{sub}"] = request.form.get(f"poi1_{col}_{row}_{sub}", "")

    # ✅ เพิ่ม remark แยกต่อข้อ (รวม remark1_6, remark1_7)
    for row in range(1, 23):
        context[f"remark1_{row}"] = request.form.get(f"remark1_{row}", "")

    # ========== Section 6: Other Issues ==========
    for i in range(1, 6):
        context[f"other_issue_{i}"] = request.form.get(f"other_issue_{i}", "")

    # ========== Render Word Template (สร้าง doc ก่อนใช้) ==========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "docx_templates", "Point (M2).docx")
    doc = DocxTemplate(template_path)

    # ========== Section 7: แนบรูป ==========
    image_keys = ['work_picture_1', 'work_picture_2', 'work_picture_3', 'work_picture_4']  # ตามชื่อใน template.docx

    for key in image_keys:
        file = request.files.get(key)
        if file and file.filename:
            temp_dir = tempfile.mkdtemp()
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, safe_filename)
            file.save(file_path)
            context[key] = InlineImage(doc, file_path, width=Cm(6))
        else:
            context[key] = ""

    # ========== สร้าง Word จาก context ==========
    doc.render(context)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    # ---------- ✨ สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ ✨ ----------
    today_str = datetime.today().strftime("%Y-%m-%d")             # YYYY-MM-DD
    job_name   = context.get("work_description", "Job")
    location   = context.get("location", "Location")
    # ป้องกันอักขระต้องห้ามในชื่อไฟล์ (Windows ฯลฯ)
    job_name = secure_filename(job_name) or "Job"
    location = secure_filename(location) or "Location"

    download_filename = (
        f"KK-{today_str} PM (M2) Point {job_name} At {location}.docx"
    )

    # ---------- ส่งไฟล์ให้ดาวน์โหลด ----------

    return send_file(temp_path.name, as_attachment=True, download_name=download_filename)

@report_bp.route('/point_m1_form')
def point_m1_form():
    return render_template('point_m1_form.html')

@report_bp.route("/generate_point_m1_pdf", methods=["POST"])
def generate_point_m1_pdf():
    context = {}

    # ========== Section 1: ข้อมูลทั่วไป ==========
    text_fields = [
        'leaders', 'date', 'coordinate', 'station', 'location', 'apostles', 'work_description', 'time1', 'time2', 'apostles'
    ]
    for field in text_fields:
        context[field] = request.form.get(field, "")

    # Members (person1, person2, ..., person7)
    for i in range(1, 8):
        context[f"person{i}"] = request.form.get(f"person{i}", "")

    # Work orders (work1, work2, ..., work7)
    for i in range(1, 8):
        context[f"work{i}"] = request.form.get(f"work{i}", "")

    # TPR numbers (tpr1, tpr2, ..., tpr4)
    for i in range(1, 5):
        context[f"tpr{i}"] = request.form.get(f"tpr{i}", "")

    # Checkbox กลุ่มแรก
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    checkbox_fields = [
        'station_in', 'station_out', 'borrow_earthing', 'borrow_voltage', 'borrow_item',
        'return_item', 'track_in', 'track_out'
    ]
    for field in checkbox_fields:
        context[field] = markbox(field)

    # ========== Section 2: ตารางงาน Point Machine (30 งาน) ==========
    # ปรับให้ข้อ 6 (เดิมข้อ 7) เป็น special row แทน
    special_rows = [3, 4, 6]

    for i in range(1, 5):  # 4 แถว
        context[f"poi_{i}"] = request.form.get(f"poi_{i}", "")

    for row in range(1, 23):
        for col in range(1, 5):
            if row == 1:
                # ✅ ข้อ 1: ใช้ input text
                context[f"poi1_{col}_{row}"] = request.form.get(f"poi1_{col}_{row}", "")
            elif row in special_rows:
                # ✅ ข้อ 3, 4, 6: ใช้ checkbox (key มี _1 ต่อท้าย)
                context[f"poi1_{col}_{row}_1"] = markbox(f"poi1_{col}_{row}_1")
            else:
                # ✅ ข้ออื่น: ใช้ checkbox แบบปกติ
                context[f"poi1_{col}_{row}"] = markbox(f"poi1_{col}_{row}")

    # Row พิเศษ: ข้อ 3, 4, 6 ที่มีแถวเสริม (ข้อ 6 มี 5 แถว)
    special_rows = [3, 4, 6]
    for row in special_rows:
        # sub-row 1: อ่าน markbox ซ้ำ
        for col in range(1, 5):
            context[f"poi1_{col}_{row}"] = markbox(f"poi1_{col}_{row}")

        # sub-row 2–5 (ข้อ 6 เดิมคือข้อ 7 มี 5 แถว)
        for sub in range(2, 6 if row == 6 else 4):
            for col in range(1, 5):
                context[f"poi1_{col}_{row}_{sub}"] = request.form.get(f"poi1_{col}_{row}_{sub}", "")

    # ✅ เพิ่ม remark แยกต่อข้อ (รวม remark1_6, remark1_7)
    for row in range(1, 23):
        context[f"remark1_{row}"] = request.form.get(f"remark1_{row}", "")

    # ========== Section 6: Other Issues ==========
    for i in range(1, 6):
        context[f"other_issue_{i}"] = request.form.get(f"other_issue_{i}", "")

    # ========== Render Word Template (สร้าง doc ก่อนใช้) ==========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "docx_templates", "Point (M1).docx")
    doc = DocxTemplate(template_path)

    # ========== Section 7: แนบรูป ==========
    image_keys = ['work_picture_1', 'work_picture_2', 'work_picture_3', 'work_picture_4']  # ตามชื่อใน template.docx

    for key in image_keys:
        file = request.files.get(key)
        if file and file.filename:
            temp_dir = tempfile.mkdtemp()
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, safe_filename)
            file.save(file_path)
            context[key] = InlineImage(doc, file_path, width=Cm(6))
        else:
            context[key] = ""

    # ========== สร้าง Word จาก context ==========
    doc.render(context)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    # ---------- ✨ สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ ✨ ----------
    today_str = datetime.today().strftime("%Y-%m-%d")             # YYYY-MM-DD
    job_name   = context.get("work_description", "Job")
    location   = context.get("location", "Location")
    # ป้องกันอักขระต้องห้ามในชื่อไฟล์ (Windows ฯลฯ)
    job_name = secure_filename(job_name) or "Job"
    location = secure_filename(location) or "Location"

    download_filename = (
        f"KK-{today_str} PM (M1) Point {job_name} At {location}.docx"
    )

    # ---------- ส่งไฟล์ให้ดาวน์โหลด ----------

    return send_file(temp_path.name, as_attachment=True, download_name=download_filename)

@report_bp.route('/mitrac_y3_form')
def mitrac_y3_form():
    return render_template('mitrac_y3_form.html')

@report_bp.route("/generate_mitrac_y3_pdf", methods=["POST"])
def generate_mitrac_y3_pdf():
    context = {}

    # ========== Section 1: ข้อมูลทั่วไป ==========
    text_fields = [
        'leaders', 'date', 'coordinate', 'station', 'location', 'apostles', 'work_description', 'time1', 'time2', 'apostles'
    ]
    for field in text_fields:
        context[field] = request.form.get(field, "")

    # Members (person1, person2, ..., person7)
    for i in range(1, 8):
        context[f"person{i}"] = request.form.get(f"person{i}", "")

    # Work orders (work1, work2, ..., work7)
    for i in range(1, 8):
        context[f"work{i}"] = request.form.get(f"work{i}", "")

    # TPR numbers (tpr1, tpr2, ..., tpr4)
    for i in range(1, 5):
        context[f"tpr{i}"] = request.form.get(f"tpr{i}", "")

    # Checkbox กลุ่มแรก
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    checkbox_fields = [
        'station_in', 'station_out', 'borrow_earthing', 'borrow_voltage', 'borrow_item',
        'return_item', 'track_in', 'track_out'
    ]
    for field in checkbox_fields:
        context[field] = markbox(field)
    
    # ========== Section 2: Visual Inspection & Cleaning Procedure (Y3) ==========
    num_general_items = 28

    # Loop for items result1-result28 and remark1-remark28
    for i in range(1, num_general_items + 1):
        context[f"result{i}"] = markbox(f"result{i}")
        context[f"remark{i}"] = request.form.get(f"remark{i}", "")

    # Specific handling for item 20's additional checkboxes
    context["type1_20"] = markbox("type1_20")
    context["type2_20"] = markbox("type2_20")

    # ========== Section 3: VCU-Lite Unit Status (ตารางที่ 1) ==========
    indicators = ["POW", "ERR", "TX", "RX", "MVB", "SC", "WA", "RTS"]
    statuses = ["ON", "OFF", "BLINK"]

    for indicator in indicators:
        for status in statuses:
            # สำหรับ checkbox ของสถานะ LED เช่น POW_ON, ERR_OFF
            context[f"{indicator}_{status}"] = markbox(f"{indicator}_{status}")
        # สำหรับช่องข้อความ Remark เช่น POW_remark, ERR_remark
        context[f"{indicator}_remark"] = request.form.get(f"{indicator}_remark", "")
    
    # ========== Section 4: แรงดันไฟฟ้าของ Power Supply (ตารางที่ 2) ==========
    sections = {
    "input": ["result", "remark"],
    "output": ["result", "remark"]
    }

    for section_name, field_types in sections.items():
        for field_type in field_types:
            # สร้างชื่อ field แบบเต็ม เช่น "input_result", "output_remark"
            full_field_name = f"{section_name}_{field_type}"
            context[full_field_name] = request.form.get(full_field_name, "")
    
    # ========== Section 5: บันทึกค่า Contact Impedance Relay (ตารางที่ 3) ==========
    platform_sides = ["NB", "EB"]

    relays = {
        "NB": ["FSR_1", "DCR_1", "NDR_1", "FIR_2", "DOR_2", "RDR_2", "ADCLR_2", "3CTR_1", "4CTR_1", "6CTR_1"],
        "EB": ["FSR_3", "DCR_3", "NDR_3", "FIR_4", "DOR_4", "RDR_4", "ADCLR_4", "3CTR_2", "4CTR_2", "6CTR_2"]
    }

    states = ["en", "de"]

    measurements = [1, 2, 3, 4]

    for platform in platform_sides:
        for relay_name in relays[platform]:
            for state in states:
                for i in measurements:
                    field_name = f"r_{relay_name}_{state}{i}"
                    context[field_name] = request.form.get(field_name, "")
    
    # ========== Section 6: Relay Status (ตารางที่ 4) ==========
    relay_list = [
    "FSR_1", "DCR_1", "NDR_1", "FIR_2", "DOR_2", "RDR_2", "ADCLR_2", "3CTR_1", "4CTR_1", "6CTR_1",
    "FSR_3", "DCR_3", "NDR_3", "FIR_4", "DOR_4", "RDR_4", "ADCLR_4", "3CTR_2", "4CTR_2", "6CTR_2"
]

    for relay in relay_list:
        relay_key = relay

        context[f"led_{relay_key}_on"] = markbox(f"led_{relay_key}_on")
        context[f"led_{relay_key}_off"] = markbox(f"led_{relay_key}_off")
        context[f"led_{relay_key}_blink"] = markbox(f"led_{relay_key}_blink")
        context[f"remark_{relay_key}"] = request.form.get(f"remark_{relay_key}", "")

    # ========== Section 7: Other Issues ==========
    for i in range(1, 6):
        context[f"other_issue_{i}"] = request.form.get(f"other_issue_{i}", "")

    # ========== Render Word Template (สร้าง doc ก่อนใช้) ==========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "docx_templates", "MITRAC (Y3).docx")
    doc = DocxTemplate(template_path)

    # ========== Section 8: แนบรูป ==========
    image_keys = ['work_picture_1', 'work_picture_2', 'work_picture_3', 'work_picture_4']  # ตามชื่อใน template.docx

    for key in image_keys:
        file = request.files.get(key)
        if file and file.filename:
            temp_dir = tempfile.mkdtemp()
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, safe_filename)
            file.save(file_path)
            context[key] = InlineImage(doc, file_path, width=Cm(6))
        else:
            context[key] = ""

    # ========== สร้าง Word จาก context ==========
    doc.render(context)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    # ---------- ✨ สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ ✨ ----------
    today_str = datetime.today().strftime("%Y-%m-%d")             # YYYY-MM-DD
    job_name   = context.get("work_description", "Job")
    location   = context.get("location", "Location")
    # ป้องกันอักขระต้องห้ามในชื่อไฟล์ (Windows ฯลฯ)
    job_name = secure_filename(job_name) or "Job"
    location = secure_filename(location) or "Location"

    download_filename = (
        f"KK-{today_str} PM (Y3) Mitrac {job_name} At {location}.docx"
    )

    # ---------- ส่งไฟล์ให้ดาวน์โหลด ----------

    return send_file(temp_path.name, as_attachment=True, download_name=download_filename)

@report_bp.route('/mitrac_y1_form')
def mitrac_y1_form():
    return render_template('mitrac_y1_form.html')

@report_bp.route("/generate_mitrac_y1_pdf", methods=["POST"])
def generate_mitrac_y1_pdf():
    context = {}

    # ========== Section 1: ข้อมูลทั่วไป ==========
    text_fields = [
        'leaders', 'date', 'coordinate', 'station', 'location', 'apostles', 'work_description', 'time1', 'time2', 'apostles'
    ]
    for field in text_fields:
        context[field] = request.form.get(field, "")

    # Members (person1, person2, ..., person7)
    for i in range(1, 8):
        context[f"person{i}"] = request.form.get(f"person{i}", "")

    # Work orders (work1, work2, ..., work7)
    for i in range(1, 8):
        context[f"work{i}"] = request.form.get(f"work{i}", "")

    # TPR numbers (tpr1, tpr2, ..., tpr4)
    for i in range(1, 5):
        context[f"tpr{i}"] = request.form.get(f"tpr{i}", "")

    # Checkbox กลุ่มแรก
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    checkbox_fields = [
        'station_in', 'station_out', 'borrow_earthing', 'borrow_voltage', 'borrow_item',
        'return_item', 'track_in', 'track_out'
    ]
    for field in checkbox_fields:
        context[field] = markbox(field)
    
    # ========== Section 2: Visual Inspection & Cleaning Procedure (Y3) ==========
    num_general_items = 23

    # Loop for items result1-result28 and remark1-remark28
    for i in range(1, num_general_items + 1):
        context[f"result{i}"] = markbox(f"result{i}")
        context[f"remark{i}"] = request.form.get(f"remark{i}", "")

    # Specific handling for item 15's additional checkboxes
    context["type1_15"] = markbox("type1_15")
    context["type2_15"] = markbox("type2_15")

    # ========== Section 3: VCU-Lite Unit Status (ตารางที่ 1) ==========
    indicators = ["POW", "ERR", "TX", "RX", "MVB", "SC", "WA", "RTS"]
    statuses = ["ON", "OFF", "BLINK"]

    for indicator in indicators:
        for status in statuses:
            # สำหรับ checkbox ของสถานะ LED เช่น POW_ON, ERR_OFF
            context[f"{indicator}_{status}"] = markbox(f"{indicator}_{status}")
        # สำหรับช่องข้อความ Remark เช่น POW_remark, ERR_remark
        context[f"{indicator}_remark"] = request.form.get(f"{indicator}_remark", "")
    
    # ========== Section 4: แรงดันไฟฟ้าของ Power Supply (ตารางที่ 2) ==========
    sections = {
    "input": ["result", "remark"],
    "output": ["result", "remark"]
    }

    for section_name, field_types in sections.items():
        for field_type in field_types:
            # สร้างชื่อ field แบบเต็ม เช่น "input_result", "output_remark"
            full_field_name = f"{section_name}_{field_type}"
            context[full_field_name] = request.form.get(full_field_name, "")
     
    # ========== Section 6: Relay Status (ตารางที่ 4) ==========
    relay_list = [
    "FSR_1", "DCR_1", "NDR_1", "FIR_2", "DOR_2", "RDR_2", "ADCLR_2", "3CTR_1", "4CTR_1", "6CTR_1",
    "FSR_3", "DCR_3", "NDR_3", "FIR_4", "DOR_4", "RDR_4", "ADCLR_4", "3CTR_2", "4CTR_2", "6CTR_2"
]

    for relay in relay_list:
        relay_key = relay

        context[f"led_{relay_key}_on"] = markbox(f"led_{relay_key}_on")
        context[f"led_{relay_key}_off"] = markbox(f"led_{relay_key}_off")
        context[f"led_{relay_key}_blink"] = markbox(f"led_{relay_key}_blink")
        context[f"remark_{relay_key}"] = request.form.get(f"remark_{relay_key}", "")

    # ========== Section 7: Other Issues ==========
    for i in range(1, 6):
        context[f"other_issue_{i}"] = request.form.get(f"other_issue_{i}", "")

    # ========== Render Word Template (สร้าง doc ก่อนใช้) ==========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "docx_templates", "MITRAC (Y1).docx")
    doc = DocxTemplate(template_path)

    # ========== Section 8: แนบรูป ==========
    image_keys = ['work_picture_1', 'work_picture_2', 'work_picture_3', 'work_picture_4']  # ตามชื่อใน template.docx

    for key in image_keys:
        file = request.files.get(key)
        if file and file.filename:
            temp_dir = tempfile.mkdtemp()
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, safe_filename)
            file.save(file_path)
            context[key] = InlineImage(doc, file_path, width=Cm(6))
        else:
            context[key] = ""

    # ========== สร้าง Word จาก context ==========
    doc.render(context)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    # ---------- ✨ สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ ✨ ----------
    today_str = datetime.today().strftime("%Y-%m-%d")             # YYYY-MM-DD
    job_name   = context.get("work_description", "Job")
    location   = context.get("location", "Location")
    # ป้องกันอักขระต้องห้ามในชื่อไฟล์ (Windows ฯลฯ)
    job_name = secure_filename(job_name) or "Job"
    location = secure_filename(location) or "Location"

    download_filename = (
        f"KK-{today_str} PM (Y1) Mitrac {job_name} At {location}.docx"
    )

    # ---------- ส่งไฟล์ให้ดาวน์โหลด ----------

    return send_file(temp_path.name, as_attachment=True, download_name=download_filename)

@report_bp.route('/mitrac_m6_form')
def mitrac_m6_form():
    return render_template('mitrac_m6_form.html')

@report_bp.route("/generate_mitrac_m6_pdf", methods=["POST"])
def generate_mitrac_m6_pdf():
    context = {}

    # ========== Section 1: ข้อมูลทั่วไป ==========
    text_fields = [
        'leaders', 'date', 'coordinate', 'station', 'location', 'apostles', 'work_description', 'time1', 'time2', 'apostles'
    ]
    for field in text_fields:
        context[field] = request.form.get(field, "")

    # Members (person1, person2, ..., person7)
    for i in range(1, 8):
        context[f"person{i}"] = request.form.get(f"person{i}", "")

    # Work orders (work1, work2, ..., work7)
    for i in range(1, 8):
        context[f"work{i}"] = request.form.get(f"work{i}", "")

    # TPR numbers (tpr1, tpr2, ..., tpr4)
    for i in range(1, 5):
        context[f"tpr{i}"] = request.form.get(f"tpr{i}", "")

    # Checkbox กลุ่มแรก
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    checkbox_fields = [
        'station_in', 'station_out', 'borrow_earthing', 'borrow_voltage', 'borrow_item',
        'return_item', 'track_in', 'track_out'
    ]
    for field in checkbox_fields:
        context[field] = markbox(field)

    # ========== Section 2: Visual Inspection & Cleaning Procedure (Y3) ==========
    num_general_items = 22

    # Loop for items result1-result28 and remark1-remark28
    for i in range(1, num_general_items + 1):
        context[f"result{i}"] = markbox(f"result{i}")
        context[f"remark{i}"] = request.form.get(f"remark{i}", "")

    # Specific handling for item 15's additional checkboxes
    context["type1_15"] = markbox("type1_15")
    context["type2_15"] = markbox("type2_15")

    # ========== Section 3: VCU-Lite Unit Status (ตารางที่ 1) ==========
    indicators = ["POW", "ERR", "TX", "RX", "MVB", "SC", "WA", "RTS"]
    statuses = ["ON", "OFF", "BLINK"]

    for indicator in indicators:
        for status in statuses:
            # สำหรับ checkbox ของสถานะ LED เช่น POW_ON, ERR_OFF
            context[f"{indicator}_{status}"] = markbox(f"{indicator}_{status}")
        # สำหรับช่องข้อความ Remark เช่น POW_remark, ERR_remark
        context[f"{indicator}_remark"] = request.form.get(f"{indicator}_remark", "")
    
    # ========== Section 4: แรงดันไฟฟ้าของ Power Supply (ตารางที่ 2) ==========
    sections = {
    "input": ["result", "remark"],
    "output": ["result", "remark"]
    }

    for section_name, field_types in sections.items():
        for field_type in field_types:
            # สร้างชื่อ field แบบเต็ม เช่น "input_result", "output_remark"
            full_field_name = f"{section_name}_{field_type}"
            context[full_field_name] = request.form.get(full_field_name, "")
     
    # ========== Section 6: Other Issues ==========
    for i in range(1, 6):
        context[f"other_issue_{i}"] = request.form.get(f"other_issue_{i}", "")

    # ========== Render Word Template (สร้าง doc ก่อนใช้) ==========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "docx_templates", "MITRAC (M6).docx")
    doc = DocxTemplate(template_path)

    # ========== Section 7: แนบรูป ==========
    image_keys = ['work_picture_1', 'work_picture_2', 'work_picture_3', 'work_picture_4']  # ตามชื่อใน template.docx

    for key in image_keys:
        file = request.files.get(key)
        if file and file.filename:
            temp_dir = tempfile.mkdtemp()
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, safe_filename)
            file.save(file_path)
            context[key] = InlineImage(doc, file_path, width=Cm(6))
        else:
            context[key] = ""

    # ========== สร้าง Word จาก context ==========
    doc.render(context)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    # ---------- ✨ สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ ✨ ----------
    today_str = datetime.today().strftime("%Y-%m-%d")             # YYYY-MM-DD
    job_name   = context.get("work_description", "Job")
    location   = context.get("location", "Location")
    # ป้องกันอักขระต้องห้ามในชื่อไฟล์ (Windows ฯลฯ)
    job_name = secure_filename(job_name) or "Job"
    location = secure_filename(location) or "Location"

    download_filename = (
        f"KK-{today_str} PM (M6) Mitrac {job_name} At {location}.docx"
    )

    # ---------- ส่งไฟล์ให้ดาวน์โหลด ----------

    return send_file(temp_path.name, as_attachment=True, download_name=download_filename)

@report_bp.route('/mitrac_m3_form')
def mitrac_m3_form():
    return render_template('mitrac_m3_form.html')

@report_bp.route("/generate_mitrac_m3_pdf", methods=["POST"])
def generate_mitrac_m3_pdf():
    context = {}

    # ========== Section 1: ข้อมูลทั่วไป ==========
    text_fields = [
        'leaders', 'date', 'coordinate', 'station', 'location', 'apostles', 'work_description', 'time1', 'time2', 'apostles'
    ]
    for field in text_fields:
        context[field] = request.form.get(field, "")

    # Members (person1, person2, ..., person7)
    for i in range(1, 8):
        context[f"person{i}"] = request.form.get(f"person{i}", "")

    # Work orders (work1, work2, ..., work7)
    for i in range(1, 8):
        context[f"work{i}"] = request.form.get(f"work{i}", "")

    # TPR numbers (tpr1, tpr2, ..., tpr4)
    for i in range(1, 5):
        context[f"tpr{i}"] = request.form.get(f"tpr{i}", "")

    # Checkbox กลุ่มแรก
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    checkbox_fields = [
        'station_in', 'station_out', 'borrow_earthing', 'borrow_voltage', 'borrow_item',
        'return_item', 'track_in', 'track_out'
    ]
    for field in checkbox_fields:
        context[field] = markbox(field)
    
     # ========== Section 2: Visual Inspection & Cleaning Procedure (Y3) ==========
    num_general_items = 22

    # Loop for items result1-result28 and remark1-remark28
    for i in range(1, num_general_items + 1):
        context[f"result{i}"] = markbox(f"result{i}")
        context[f"remark{i}"] = request.form.get(f"remark{i}", "")

    # Specific handling for item 15's additional checkboxes
    context["type1_15"] = markbox("type1_15")
    context["type2_15"] = markbox("type2_15")

    # ========== Section 3: VCU-Lite Unit Status (ตารางที่ 1) ==========
    indicators = ["POW", "ERR", "TX", "RX", "MVB", "SC", "WA", "RTS"]
    statuses = ["ON", "OFF", "BLINK"]

    for indicator in indicators:
        for status in statuses:
            # สำหรับ checkbox ของสถานะ LED เช่น POW_ON, ERR_OFF
            context[f"{indicator}_{status}"] = markbox(f"{indicator}_{status}")
        # สำหรับช่องข้อความ Remark เช่น POW_remark, ERR_remark
        context[f"{indicator}_remark"] = request.form.get(f"{indicator}_remark", "")
    
    # ========== Section 6: Other Issues ==========
    for i in range(1, 6):
        context[f"other_issue_{i}"] = request.form.get(f"other_issue_{i}", "")

    # ========== Render Word Template (สร้าง doc ก่อนใช้) ==========
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "docx_templates", "MITRAC (M3).docx")
    doc = DocxTemplate(template_path)

    # ========== Section 7: แนบรูป ==========
    image_keys = ['work_picture_1', 'work_picture_2', 'work_picture_3', 'work_picture_4']  # ตามชื่อใน template.docx

    for key in image_keys:
        file = request.files.get(key)
        if file and file.filename:
            temp_dir = tempfile.mkdtemp()
            safe_filename = secure_filename(file.filename)
            file_path = os.path.join(temp_dir, safe_filename)
            file.save(file_path)
            context[key] = InlineImage(doc, file_path, width=Cm(6))
        else:
            context[key] = ""

    # ========== สร้าง Word จาก context ==========
    doc.render(context)

    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    # ---------- ✨ สร้างชื่อไฟล์ตามรูปแบบที่ต้องการ ✨ ----------
    today_str = datetime.today().strftime("%Y-%m-%d")             # YYYY-MM-DD
    job_name   = context.get("work_description", "Job")
    location   = context.get("location", "Location")
    # ป้องกันอักขระต้องห้ามในชื่อไฟล์ (Windows ฯลฯ)
    job_name = secure_filename(job_name) or "Job"
    location = secure_filename(location) or "Location"

    download_filename = (
        f"KK-{today_str} PM (M3) Mitrac {job_name} At {location}.docx"
    )

    # ---------- ส่งไฟล์ให้ดาวน์โหลด ----------

    return send_file(temp_path.name, as_attachment=True, download_name=download_filename)