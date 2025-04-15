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
from urllib.parse import urlparse
# from app.static import uploads
import os
import re
import shutil

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

            # ⏬ Post-process: ย้ายรูปจาก temp_uploads ไปยัง uploads ⏬
            
            updated = False
            new_description = new_item.description

            temp_prefix1 = '/static/temp_uploads/'
            temp_prefix2 = '../../static/temp_uploads/'
            perm_prefix = '/static/uploads/'

            temp_folder = os.path.join(current_app.root_path, 'static', 'temp_uploads')
            perm_folder = os.path.join(current_app.root_path, 'static', 'uploads')

            if not os.path.exists(perm_folder):
                os.makedirs(perm_folder)

            matches = re.findall(r'src="([^"]+)"', new_description)
            for src in matches:
                relative_path = None
                if src.startswith(temp_prefix1):
                    relative_path = src[len(temp_prefix1):]
                elif src.startswith(temp_prefix2):
                    relative_path = src[len(temp_prefix2):]

                if relative_path:
                    temp_file_path = os.path.join(temp_folder, relative_path)
                    perm_file_path = os.path.join(perm_folder, relative_path)
                    if os.path.exists(temp_file_path):
                        try:
                            os.rename(temp_file_path, perm_file_path)
                            new_url = url_for('static', filename=f'uploads/{relative_path}', _external=True)
                            new_description = new_description.replace(src, new_url)
                            updated = True
                            current_app.logger.info(f"Moved file '{relative_path}' to uploads.")
                        except Exception as e:
                            current_app.logger.error(f"Error moving file: {e}")
                    else:
                        current_app.logger.warning(f"File not found: {temp_file_path}")

            # หากมีการเปลี่ยน URL ใน description ให้บันทึกกลับไปยัง DB
            if updated:
                new_item.description = new_description
                db.session.commit()

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
import re
from urllib.parse import urlparse

@knowledge_bp.route('/delete/<int:number>', methods=['POST'])
@login_required
def deleteknowledge(number):
    if current_user.role != 'admin':
        flash("You don't have permission to delete knowledgebase.", "danger")
        return redirect(url_for('knowledge_base.main'))

    items = KnowledgeBase.query.filter_by(number=number).first()

    if not items:
        flash("Knowledgebase not found.", "danger")
        return redirect(url_for('knowledge_base.main'))

    # ✅ ดึง URL รูปทั้งหมดจาก description
    image_srcs = re.findall(r'<img\s+[^>]*src="([^"]+)"', items.description)

    for src in image_srcs:
        relative_path = None

        # ตรวจสอบ path ที่ขึ้นต้นด้วย ../../static/uploads/
        if src.startswith('../../static/uploads/'):
            relative_path = src.split('../../static/uploads/')[-1]
        elif src.startswith('/static/uploads/'):
            relative_path = src.split('/static/uploads/')[-1]
        else:
            parsed = urlparse(src)
            if parsed.path.startswith('/static/uploads/'):
                relative_path = parsed.path.split('/static/uploads/')[-1]

        if relative_path:
            image_path = os.path.join(current_app.root_path, 'static', 'uploads', relative_path)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    current_app.logger.info(f"Deleted image file: {image_path}")
                except Exception as e:
                    current_app.logger.error(f"Error deleting image file {image_path}: {e}")
            else:
                current_app.logger.warning(f"Image file not found: {image_path}")
        else:
            current_app.logger.warning(f"Unexpected image src format: {src}")

    # ลบข้อมูลจากฐานข้อมูล
    db.session.delete(items)
    db.session.commit()
    flash("Knowledgebase deleted successfully!", "success")
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
        
        raw_description = form.description.data
        new_description = raw_description
        updated = False

        temp_folder = os.path.join(current_app.root_path, 'static', 'temp_uploads')
        perm_folder = os.path.join(current_app.root_path, 'static', 'uploads')

        if not os.path.exists(perm_folder):
            os.makedirs(perm_folder)

        # ✅ ดึง <img src="..."> ทั้งหมดจาก description เดิมก่อน edit
        old_srcs = re.findall(r'src="([^"]+)"', items.description or '')

        # ✅ ดึง <img src="..."> ที่ยังอยู่ในฟอร์มใหม่ (หลัง edit)
        new_srcs = re.findall(r'src="([^"]+)"', raw_description or '')

        # ✅ คำนวณรูปที่ถูกลบออกไป
        deleted_srcs = set(old_srcs) - set(new_srcs)

        # ✅ ลบรูปที่ถูกลบออกไปจาก uploads
        for src in deleted_srcs:
            if '/static/uploads/' in src:
                relative_path = src.split('/static/uploads/')[-1]
                image_path = os.path.join(perm_folder, relative_path)
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        current_app.logger.info(f"🗑️ Deleted unused image: {relative_path}")
                    except Exception as e:
                        current_app.logger.error(f"❌ Failed to delete image: {e}")

        # ✅ ตรวจสอบและย้ายรูปใหม่จาก temp → uploads
        matches = re.findall(r'src="([^"]+)"', raw_description)
        for src in matches:
            relative_path = None
            for prefix in [ '/static/temp_uploads/', '../../static/temp_uploads/', request.host_url.rstrip('/') + '/static/temp_uploads/' ]:
                if src.startswith(prefix):
                    relative_path = src.split(prefix)[-1]
                    break

            if relative_path:
                temp_path = os.path.join(temp_folder, relative_path)
                perm_path = os.path.join(perm_folder, relative_path)

                if os.path.exists(temp_path):
                    try:
                        shutil.move(temp_path, perm_path)
                        new_url = url_for('static', filename=f'uploads/{relative_path}', _external=True)
                        new_description = new_description.replace(src, new_url)
                        updated = True
                    except Exception as e:
                        flash("เกิดข้อผิดพลาดขณะย้ายไฟล์", "danger")
                        return redirect(url_for('knowledge_base.edit_knowledge_base', number=number))

        # อัปเดตค่าต่าง ๆ จากฟอร์ม
        items.device_type = form.device_type.data
        items.topic = form.topic.data
        items.description = new_description if updated else raw_description
        items.create_by = form.create_by.data

        db.session.commit()
        flash("บันทึกการแก้ไขเรียบร้อย", "success")
        return redirect(url_for('knowledge_base.knowledge_base_detail', number=items.number))

    return render_template("edit_knowledge_base.html", form=form, items=items)


