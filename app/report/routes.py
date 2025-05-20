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

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, send_file, abort
from flask_login import login_required, current_user
import pytz
from pytz import timezone
from datetime import datetime
from app.extensions import db
from . import report_bp
from werkzeug.utils import secure_filename
# from app.static import uploads
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tempfile
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uuid
import os
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image
from reportlab.lib.units import cm
from docxtpl import DocxTemplate
from docxtpl import InlineImage
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
            file_path = os.path.join(temp_dir, file.filename)
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
            file_path = os.path.join(temp_dir, file.filename)
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
            file_path = os.path.join(temp_dir, file.filename)
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
            file_path = os.path.join(temp_dir, file.filename)
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