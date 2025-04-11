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

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import login_required, current_user
from app.models import db, KnowledgeBase
from .forms import KnowledgeBaseForm, EditKnowledgeBaseForm
import pytz
from pytz import timezone
from datetime import datetime
from app.extensions import db
from . import knowledge_bp
from werkzeug.utils import secure_filename
# from app.static import uploads
import os

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



@knowledge_bp.route('/main')
@login_required
def main():
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
            return redirect(url_for('knowledge_base.main'))
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
            return redirect(url_for('knowledge_base.main'))
        items = KnowledgeBase.query.filter_by(number=number).first()
        if items:
            db.session.delete(items)
            db.session.commit()
            flash("Knowledgebase deleted successfully!", "success")
        else:
            flash("Knowledgebase not found.", "danger")
        #return redirect(url_for('knowledge_base'))
        return redirect(url_for('knowledge_base.main'))

def allowed_file(filename):
    """ ตรวจสอบประเภทไฟล์ที่อนุญาต """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@knowledge_bp.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        import uuid
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        # ใช้โฟลเดอร์ชั่วคราวสำหรับ pending uploads
        temp_folder = os.path.join(current_app.root_path, 'static', 'temp_uploads')
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        filepath = os.path.join(temp_folder, unique_filename)
        file.save(filepath)
        # ส่งกลับ URL ที่ชี้ไปยังไฟล์ในโฟลเดอร์ temp_uploads
        file_url = url_for('static', filename=f'temp_uploads/{unique_filename}', _external=True)
        return jsonify({'location': file_url})
    return jsonify({'error': 'Invalid file type'}), 400


@knowledge_bp.route('/edit_knowledge_base/<int:number>', methods=['GET', 'POST'])
@login_required
def edit_knowledge_base(number):
    """ แก้ไขข้อมูลใน Knowledge Base """
    items = KnowledgeBase.query.get_or_404(number)

    # จำกัดสิทธิ์เฉพาะ Admin
    if current_user.role != 'admin':
        flash("คุณไม่มีสิทธิ์แก้ไขข้อมูลนี้", "danger")
        return redirect(url_for('knowledge_base.knowledge_base_detail', number=number))

    # ใช้ EditKnowledgeBaseForm และโหลดค่าจากฐานข้อมูล
    form = EditKnowledgeBaseForm()

    if request.method == 'GET':
        form.create_date.data = items.create_date.strftime('%Y-%m-%d %H:%M') if items.create_date else ''
        form.device_type.data = items.device_type
        form.topic.data = items.topic
        form.description.data = items.description
        form.create_by.data = items.create_by

    if form.validate_on_submit():
        # อัปเดตค่าต่าง ๆ จากฟอร์ม
        items.device_type = form.device_type.data
        items.topic = form.topic.data
        items.description = form.description.data.replace('../static/', '/static/')
        items.create_by = form.create_by.data

        db.session.commit()
        return redirect(url_for('knowledge_base.knowledge_base_detail', number=items.number))

    return render_template("edit_knowledge_base.html", form=form, items=items)


