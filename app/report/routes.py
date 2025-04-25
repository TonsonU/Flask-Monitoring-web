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



@report_bp.route('/main')
@login_required
def main():
    return render_template('report.html') 

@report_bp.route('/interlocking_form')
def interlocking_form():
    return render_template('interlocking_form.html')

@report_bp.route('/generate_interlocking_pdf', methods=['POST'])
def generate_interlocking_pdf():
    # รับข้อมูลจากฟอร์ม
    field1 = request.form['field1']
    field2 = request.form['field2']

    # สร้าง pdf
    pdf_path = create_pdf(field1, field2)

    # วันที่ปัจจุบันในรูปแบบ KK-YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"KK-{today} PM Interlocking.pdf"

    # ส่งไฟล์กลับให้ผู้ใช้
    return send_file(pdf_path, as_attachment=True, download_name=filename)

def create_pdf(field1, field2):
    pdfmetrics.registerFont(TTFont('AngsanaNew', 'static/fonts/Angsana_0.ttf'))
    pdfmetrics.registerFont(TTFont('AngsanaNew-Bold', 'static/fonts/Angsana_1.ttf'))

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')

    c = canvas.Canvas(temp_file.name, pagesize=A4)
    width, height = A4

    c.setFont("AngsanaNew-Bold", 18)
    c.drawString(50, height - 50, "Interlocking Report")

    c.setFont("AngsanaNew", 12)
    c.drawString(50, height - 100, f"Field 1: {field1}")
    c.drawString(50, height - 120, f"Field 2: {field2}")

    c.save()
    return temp_file.name

@report_bp.route('/tap_form')
def tap_form():
    return render_template('tap_form.html')

@report_bp.route("/generate_tap_pdf", methods=["POST"])
def generate_tap_pdf():
    context = {key: request.form.get(key, "") for key in [
        "date", "work_order", "work_type", "loation", "track_no", "apostle",
        "unit_name_1", "sn_installed_1", "sn_removed_1", "qty_1",
        "unit_name_2", "sn_installed_2", "sn_removed_2", "qty_2",
        "unit_name_3", "sn_installed_3", "sn_removed_3", "qty_3",
        "person_1", "person_2", "person_3", "person_4", "person_5",
        "person_6", "person_7", "person_8", "person_9", "person_10",
        "maintenance_action"
    ]}

    uid = str(uuid.uuid4())
    pdf_path = os.path.join(tempfile.gettempdir(), f"{uid}.pdf")
    filename = f"KK-{datetime.now().strftime('%Y-%m-%d')} PM TAP.pdf"

    # ลงทะเบียนฟอนต์
    pdfmetrics.registerFont(TTFont('AngsanaNew', 'static/fonts/Angsana_0.ttf'))
    pdfmetrics.registerFont(TTFont('AngsanaNew-Bold', 'static/fonts/Angsana_1.ttf'))

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="MyTitle", fontName="AngsanaNew-Bold", fontSize=18, alignment=1, spaceAfter=10))
    styles.add(ParagraphStyle(name="Bold", fontName="AngsanaNew-Bold", fontSize=16, spaceAfter=6))
    styles.add(ParagraphStyle(name="Text", fontName="AngsanaNew", fontSize=16))
    styles.add(ParagraphStyle(name="Cell", fontName="AngsanaNew", fontSize=14, leading=18))
    cell_style = styles["Cell"]

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=30)
    elements = []

    # ✅ LOGO + TITLE อยู่บรรทัดเดียว ตรงกลางเอกสาร
    logo_path = os.path.join("static", "images", "logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.79 * cm, height=2.09 * cm)
    else:
        logo = ""

    header_table = Table([
        [logo, Paragraph("MAINTENANCE DAILY REPORT", styles["MyTitle"]), ""]
    ], colWidths=[1.79 * cm, 12 * cm, 1.79 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))

    # INFO TABLE
    info_table = [
        ["Date", context["date"]],
        ["Work Order No", context["work_order"]],
        ["Work Type", context["work_type"], "Location", context["loation"]],
        ["Track Possession No", context["track_no"], "Apostle Name", context["apostle"]],
    ]
    for r in range(len(info_table)):
        for c in range(len(info_table[r])):
            info_table[r][c] = Paragraph(info_table[r][c], cell_style)
    t1 = Table(info_table, colWidths=[120, 180, 100, 100])
    t1.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,3), 'AngsanaNew-Bold'),
        ('FONTNAME', (2,2), (2,3), 'AngsanaNew-Bold'),
        ('FONTNAME', (1,0), (3,3), 'AngsanaNew'),
        ('BACKGROUND', (0,0), (0,3), colors.lightgrey),
        ('BACKGROUND', (2,2), (2,3), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 12))

    # EQUIPMENT TABLE
    elements.append(Paragraph("Exchanged Equipment/Replaceable Units<br/><br/>", styles["Bold"]))
    equip_table = [
        ["Maintenance Description", "Serial/No. Unit installed", "Serial/No. Unit removed", "Qty"],
        [context["unit_name_1"], context["sn_installed_1"], context["sn_removed_1"], context["qty_1"]],
        [context["unit_name_2"], context["sn_installed_2"], context["sn_removed_2"], context["qty_2"]],
        [context["unit_name_3"], context["sn_installed_3"], context["sn_removed_3"], context["qty_3"]],
    ]
    for r in range(len(equip_table)):
        for c in range(len(equip_table[r])):
            equip_table[r][c] = Paragraph(equip_table[r][c], cell_style)
    t2 = Table(equip_table, colWidths=[150, 130, 130, 90])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'AngsanaNew-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'AngsanaNew'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 12))

    # TEAM TABLE
    elements.append(Paragraph("Team Service Maintenance<br/><br/>", styles["Bold"]))
    team_table = [["No.", "Name Surname", "No.", "Name Surname"]]
    for i in range(5):
        team_table.append([
            str(i+1), context[f"person_{i+1}"],
            str(i+6), context[f"person_{i+6}"]
        ])
    for r in range(len(team_table)):
        for c in range(len(team_table[r])):
            team_table[r][c] = Paragraph(team_table[r][c], cell_style)
    t3 = Table(team_table, colWidths=[30, 220, 30, 220])
    t3.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'AngsanaNew-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'AngsanaNew'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 12))

    # MAINTENANCE ACTION
    elements.append(Paragraph("Maintenance Action<br/><br/>", styles["Bold"]))
    elements.append(Paragraph(context["maintenance_action"], styles["Text"]))

    try:
        doc.build(elements)
    except Exception as e:
        print("PDF Build Error:", e)
        abort(500, "PDF generation failed.")

    return send_file(pdf_path, as_attachment=True, download_name=filename)

@report_bp.route('/emp_form')
def emp_form():
    return render_template('emp_form.html')

@report_bp.route("/generate_emp_pdf", methods=["POST"])
def generate_emp_pdf():
    # เก็บค่า text field
    context = {
        'leader': request.form.get('leader'),
        'date': request.form.get('date'),
        'hh': request.form.get('hh'),
        'mm': request.form.get('mm'),
        'coordinate': request.form.get('coordinate'),
        'station': request.form.get('station'),
        'location': request.form.get('location'),
        'apostle': request.form.get('apostle'),
        'tpr': request.form.get('tpr'),
        'person1': request.form.get('person1'),
        'person2': request.form.get('person2'),
        'person3': request.form.get('person3'),
        'person4': request.form.get('person4'),
        'person5': request.form.get('person5'),
        'person6': request.form.get('person6'),
        'person7': request.form.get('person7'),
        'work': request.form.get('work'),
        'workdes': request.form.get('workdes'),
        'poi_1': request.form.get('poi_1'),
        'poi_2': request.form.get('poi_2'),
        'poi_3': request.form.get('poi_3')
    }

    # ฟังก์ชันสำหรับแปลง checkbox เป็น ✔ หรือ ☐
    def markbox(name):
        return '✔' if request.form.get(name) else '☐'

    # รายการ checkbox ทั้งหมด
    checkbox_fields = ['checkin', 'checkout', 'earthing_borrow', 'voltage_borrow', 'borrow', 'return', 'tra_in', 'tra_out']
    for field in checkbox_fields:
        context[field] = markbox(field)

    # เติมข้อมูลลง Word Template
    base_dir = os.path.dirname(os.path.abspath(__file__))  # path ของไฟล์ report.py
    template_path = os.path.join(base_dir, "templates", "forms", "Point M1.docx")

    doc = DocxTemplate(template_path)  # ✅ ใช้ path ที่ถูกต้อง
    doc.render(context)

    # สร้างไฟล์ชั่วคราวสำหรับ .docx
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(temp_path.name)

    return send_file(temp_path.name, as_attachment=True, download_name="filled_form.docx")