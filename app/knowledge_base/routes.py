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

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from app.models import db, KnowledgeBase
from .forms import KnowledgeBaseForm
import pytz
from pytz import timezone
from datetime import datetime
from app.extensions import db
from . import knowledge_bp
from werkzeug.utils import secure_filename
from app.static import uploads
import os

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



@knowledge_bp.route('/knowledge_base')
@login_required
def knowledge_base():
        items = KnowledgeBase.query.all()
        return render_template('knowledge_base.html', items=items) 
    
@knowledge_bp.route('/create_knowledge_base', methods=['GET', 'POST'])
@login_required
def create_knowledge_base():
    # สร้างฟอร์มจาก CreateForm
        form = KnowledgeBaseForm()
        thailand_tz = pytz.timezone('Asia/Bangkok')
        utc_tz = timezone('UTC')

        if request.method == 'GET':
            now_th = datetime.now(thailand_tz)
            form.create_date.data = now_th.strftime('%Y-%m-%d %H:%M')

    # ตรวจสอบว่าผู้ใช้ทำการส่งฟอร์มหรือไม่
        if form.validate_on_submit():
            # ดึงค่าจากฟอร์ม

            device_type = form.device_type.data
            topic = form.topic.data
            description = form.description.data
            create_by = form.create_by.data


            # แปลงค่า create_date เป็น datetime หากมีการกรอก
            create_date_str = form.create_date.data
            
            try:
                create_date_naive = datetime.strptime(create_date_str, '%Y-%m-%d %H:%M')
                create_date = thailand_tz.localize(create_date_naive)
            except ValueError:
                flash('รูปแบบวันที่และเวลาไม่ถูกต้อง', 'danger')
                return render_template("create_knowledge_base.html", form=form)

            # สร้างอ็อบเจกต์ใหม่เพื่อบันทึกข้อมูล
            new_item = KnowledgeBase(
                create_date=create_date,
                device_type=device_type,
                topic=topic,
                description = form.description.data.replace('../static/', '/static/'),
                create_by=create_by,
            )

            # บันทึกข้อมูลลงในฐานข้อมูล
            db.session.add(new_item)
            db.session.commit()
            flash('บันทึกข้อมูลสำเร็จ', "success")

            # หลังจากบันทึกข้อมูลเสร็จแล้ว ให้รีไดเรกต์ไปที่หน้า index
            return redirect(url_for('knowledge_base.knowledge_base'))
        return render_template("create_knowledge_base.html", form=form)
    
    # Route สำหรับดูรายละเอียดเพิ่มเติมของ Work   
@knowledge_bp.route('/knowledge_basenumber/<int:number>', methods=['GET', 'POST'])
@login_required
def knowledge_base_detail(number):
        # ดึงข้อมูลจากตาราง Work โดยใช้ number
        items = KnowledgeBase.query.get(number)
    
        # ตรวจสอบว่ามีข้อมูลหรือไม่
        if not items:
            abort(404)
    
        # ดึงข้อมูลที่เชื่อมโยงกับ Work
        create_date = items.create_date
        device_type = items.device_type
        topic = items.topic
        create_by = items.create_by

       

        # ส่งข้อมูลไปยัง template
        return render_template(
        "knowledge_base_detail.html", 
        items=items, 
        create_date=create_date, 
        topic=topic, 
        device_type=device_type, 
        create_by=create_by, 
        )
    
    # Route สำหรับการลบ Work (เฉพาะ admin)    
@knowledge_bp.route('/delete/<int:number>', methods=['POST'])
@login_required
def deleteknowledge(number):
        if current_user.role != 'admin':
            flash("You don't have permission to delete knowledgebase.", "danger")
            return redirect(url_for('knowledge_base.knowledge_base'))
        items = KnowledgeBase.query.filter_by(number=number).first()
        if items:
            db.session.delete(items)
            db.session.commit()
            flash("Knowledgebase deleted successfully!", "success")
        else:
            flash("Knowledgebase not found.", "danger")
        #return redirect(url_for('knowledge_base'))
        return redirect(url_for('knowledge_base.knowledge_base'))

def allowed_file(filename):
    """ ตรวจสอบประเภทไฟล์ที่อนุญาต """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@knowledge_bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    """ API สำหรับอัปโหลดรูปจาก Summernote """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        file.save(filepath)

        # ส่ง URL ของรูปที่อัปโหลดกลับไปให้ Summernote
        return jsonify({'location': f'/static/uploads/{filename}'})

    return jsonify({'error': 'Invalid file type'}), 400
