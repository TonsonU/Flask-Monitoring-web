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
# from app.static import uploads
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import tempfile
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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

