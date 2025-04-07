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

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Work, Comment, Line, Location, DeviceType, DeviceName
from .forms import CreateForm, CommentForm, EditForm
import pytz
from pytz import timezone
from datetime import datetime
from . import work_bp
from werkzeug.utils import secure_filename
import os
import re



@work_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # สร้างฟอร์มจาก CreateForm
        form = CreateForm()
        thailand_tz = pytz.timezone('Asia/Bangkok')
        utc_tz = timezone('UTC')

        if request.method == 'GET':
            now_th = datetime.now(thailand_tz)
            form.create_date.data = now_th.strftime('%Y-%m-%d %H:%M')

    # ตรวจสอบว่าผู้ใช้ทำการส่งฟอร์มหรือไม่
        if form.validate_on_submit():
            # ดึงค่าจากฟอร์ม
            work_order = form.work_order.data
            line_id = form.line_name.data.id if form.line_name.data else None  # ใช้ ID ของ Line
            location_id = form.location_name.data.id if form.location_name.data else None  # ใช้ ID ของ Location
            device_type_id = form.device_type_name.data.id if form.device_type_name.data else None  # ใช้ ID ของ DeviceType
            device_name_id = form.device_name.data.id if form.device_name.data else None  # ใช้ ID ของ DeviceName
            description = form.description.data
            report_by = form.report_by.data
            status = form.status.data
            link = form.link.data

            # แปลงค่า create_date เป็น datetime หากมีการกรอก
            create_date_str = form.create_date.data
            
            try:
                create_date_naive = datetime.strptime(create_date_str, '%Y-%m-%d %H:%M')
                create_date = thailand_tz.localize(create_date_naive)
            except ValueError:
                flash('รูปแบบวันที่และเวลาไม่ถูกต้อง', 'danger')
                return render_template("create.html", form=form)
            
            # ตรวจสอบว่า device_type เป็น "Point" หรือไม่
            selected_device_type = form.device_type_name.data.name.lower() if form.device_type_name.data else ""

            if selected_device_type == "point":
                cause_id = form.cause.data.id if form.cause.data else None
                point_casedetail_id = form.point_casedetail.data.id if form.point_casedetail.data else None
            else:
                cause_id = None
                point_casedetail_id = None

            # สร้างอ็อบเจกต์ใหม่เพื่อบันทึกข้อมูล
            new_work = Work(
                create_date=create_date,
                work_order=work_order,
                line_id=line_id,  # เก็บ ID ของ Line
                location_id=location_id,  # เก็บ ID ของ Location
                device_type_id=device_type_id,  # เก็บ ID ของ DeviceType
                device_name_id=device_name_id,  # เก็บ ID ของ DeviceName
                description=description,
                report_by=report_by,
                status=status,
                link=link,
                cause_id=cause_id,
                point_casedetail_id=point_casedetail_id
            )

            # บันทึกข้อมูลลงในฐานข้อมูล
            db.session.add(new_work)
            db.session.commit()
            flash('บันทึกข้อมูลสำเร็จ', "success")

            # หลังจากบันทึกข้อมูลเสร็จแล้ว ให้รีไดเรกต์ไปที่หน้า index
            return redirect(url_for('main.index'))
        return render_template("create.html", form=form)

# Route สำหรับจัดการ Work ที่ปิดแล้ว
@work_bp.route('/closed',methods=['GET','POST'])
@login_required
def closed():
        works = Work.query.all()  
        return render_template("closed.html", works=works)
    
    
    # Route สำหรับจัดการ Work ที่ปิดแล้ว
@work_bp.route('/open',methods=['GET','POST'])
@login_required
def open():
        works = Work.query.all()  
        return render_template("open.html", works=works)
    

    # Route สำหรับการลบ Work (เฉพาะ admin)    
@work_bp.route('/delete/<int:number>', methods=['POST'])
@login_required
def deleteWork(number):
        if current_user.role != 'admin':
            flash("You don't have permission to delete work orders.", "danger")
            return redirect(url_for('main.index'))
        works = Work.query.filter_by(number=number).first()
        if works:
            db.session.delete(works)
            db.session.commit()
            flash("Work deleted successfully!", "success")
        else:
            flash("Work not found.", "danger")
        #return redirect(url_for('index'))
        return redirect(url_for('main.index'))
    
    
    # Route สำหรับทำการแก้ไขข้อมูล 
@work_bp.route('/edit/<number>', methods=['GET', 'POST'], endpoint='edit')
@login_required
def editWork(number):
        works = Work.query.filter_by(number=number).first_or_404()
        form = EditForm(obj=works)

        if form.validate_on_submit():
            # ตรวจสอบว่ามีการเปลี่ยนแปลงในแต่ละฟิลด์
            has_changed = False

            # เปรียบเทียบและอัปเดตแต่ละฟิลด์ถ้ามีการเปลี่ยนแปลง
            if form.create_date.data:
                new_create_date = datetime.strptime(form.create_date.data, "%Y-%m-%d %H:%M")
                if new_create_date != works.create_date:
                    works.create_date = new_create_date
                    has_changed = True

            if form.work_order.data != works.work_order:
                works.work_order = form.work_order.data
                has_changed = True

            if form.description.data != works.description:
                works.description = form.description.data
                has_changed = True

            if form.report_by.data != works.report_by:
                works.report_by = form.report_by.data
                has_changed = True

            if form.status.data != works.status:
                works.status = form.status.data
                has_changed = True

            if form.link.data != works.link:
                works.link = form.link.data
                has_changed = True

            # อัปเดต ForeignKey
            if form.line_name.data != works.line:
                works.line = form.line_name.data
                has_changed = True

            if form.location_name.data != works.location:
                works.location = form.location_name.data
                has_changed = True

            if form.device_type_name.data != works.device_type:
                works.device_type = form.device_type_name.data
                has_changed = True

            if form.device_name.data != works.device_name:
                works.device_name = form.device_name.data
                has_changed = True

            # ✅ อัปเดต Cause และ Point Case Detail
            if form.cause.data != works.cause:
                works.cause = form.cause.data
                has_changed = True

            if form.point_casedetail.data != works.point_casedetail:
                works.point_casedetail = form.point_casedetail.data
                has_changed = True

            if has_changed:
                db.session.commit()
                flash("Work updated successfully!", "success")
                return redirect(url_for('main.index'))
            else:
                flash("ไม่มีการเปลี่ยนแปลงข้อมูลใดๆ.", "info")
                return redirect(url_for('work.edit', number=number))

        elif request.method == 'GET':
            form.create_date.data = works.create_date.strftime("%Y-%m-%d %H:%M") if works.create_date else None
            form.work_order.data = works.work_order
            form.description.data = works.description
            form.report_by.data = works.report_by
            form.status.data = works.status
            form.link.data = works.link

            # โหลดค่าที่เชื่อมโยงกับ ForeignKey
            form.line_name.data = works.line
            form.location_name.data = works.location
            form.device_type_name.data = works.device_type
            form.device_name.data = works.device_name

        return render_template("edit.html", form=form, works=works)
    
    
@work_bp.route('/worknumber/<int:number>', methods=['GET', 'POST'])
@login_required
def work_detail(number):
    # ดึงข้อมูลจากตาราง Work โดยใช้ number
    works = Work.query.get(number)
    if not works:
        abort(404)

    # ดึงข้อมูลที่เชื่อมโยงกับ Work
    line = works.line
    location = works.location
    device_type = works.device_type
    device_name = works.device_name

    form = CommentForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            # ตรวจสอบไฟล์ extension (ตัวอย่างใช้ .png, .jpg, .jpeg, .gif)
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in filename and filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                flash('File type not allowed', 'danger')
                return redirect(url_for('work.work_detail', number=number))
            # เพิ่มความเป็นเอกลักษณ์ให้กับชื่อไฟล์
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static/uploads'))
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_path = os.path.join(upload_folder, unique_filename)
            try:
                image_file.save(image_path)
                image_url = url_for('static', filename=f'uploads/{unique_filename}', _external=True)
            except Exception as e:
                current_app.logger.error(f"Error saving image: {e}")
                flash('Error uploading image', 'danger')
                return redirect(url_for('work.work_detail', number=number))
                
        pdf_url = form.pdf_url.data.strip() if form.pdf_url.data else None

        # กำหนดเขตเวลาของประเทศไทย
        thailand_tz = pytz.timezone('Asia/Bangkok')
        timestamp = datetime.now(thailand_tz)

        comment = Comment(
            content=form.comment.data,
            pdf_url=pdf_url,
            image_url=image_url,
            work_id=number,
            user_id=current_user.id,
            timestamp=timestamp
        )
        db.session.add(comment)
        db.session.commit()
        current_app.logger.info(f"Comment added to DB: {comment}")
        flash('Your comment has been posted.', 'success')
        return redirect(url_for('work.work_detail', number=number))

    comments = Comment.query.filter_by(work_id=number).order_by(Comment.timestamp.desc()).all()

    return render_template(
        "work_detail.html", 
        works=works, 
        line=line, 
        location=location, 
        device_type=device_type, 
        device_name=device_name, 
        form=form, 
        comments=comments
    )

    
@work_bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    import re  # Import โมดูล re สำหรับ regex
    comment = Comment.query.get_or_404(comment_id)
    work_id = comment.work_id
    if comment.user_id != current_user.id:
        abort(403)  # Forbidden

    # Extract image URLs จาก comment.content โดยใช้ regex
    image_srcs = re.findall(r'<img\s+[^>]*src="([^"]+)"', comment.content)

    # ถ้ามี comment.image_url (เก็บแยกไว้) และยังไม่อยู่ใน image_srcs ให้เพิ่มเข้าไป
    if comment.image_url and comment.image_url not in image_srcs:
        image_srcs.append(comment.image_url)

    for src in image_srcs:
        # หาก src มีรูปแบบ "../../static/..." ให้ตัดเอา relative path ออกมา
        if src.startswith('../../static/'):
            relative_path = src.split('../../static/')[-1]
        # หาก src มีรูปแบบ "/static/..." ให้ตัดเอา relative path ออกมา
        elif src.startswith('/static/'):
            relative_path = src.split('/static/')[-1]
        else:
            current_app.logger.warning(f"Unexpected image src format: {src}")
            continue

        # สร้าง absolute path โดยใช้ current_app.root_path
        image_path = os.path.join(current_app.root_path, 'static', relative_path)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                current_app.logger.info(f"Deleted image file: {image_path}")
            except Exception as e:
                current_app.logger.error(f"Error deleting image file {image_path}: {e}")
        else:
            current_app.logger.warning(f"Image file not found: {image_path}")

    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted.', 'info')
    return redirect(url_for('work.work_detail', number=work_id))


@work_bp.route('/delete_uploaded_image', methods=['POST'])
@login_required
def delete_uploaded_image():
    data = request.get_json()
    image_url = data.get('image_url')
    if not image_url:
        return jsonify({'error': 'No image URL provided'}), 400
    if '/static/' in image_url:
        relative_path = image_url.split('/static/')[-1]  # ควรได้ "uploads/unique_filename.png"
        image_path = os.path.join(current_app.root_path, 'static', relative_path)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                current_app.logger.info(f"Deleted uploaded image via AJAX: {image_path}")
                return jsonify({'success': True})
            except Exception as e:
                current_app.logger.error(f"Error deleting image file: {e}")
                return jsonify({'error': 'Error deleting image file'}), 500
        else:
            return jsonify({'error': 'File not found'}), 404
    else:
        return jsonify({'error': 'Invalid image URL format'}), 400

    

# Endpoint สำหรับ AJAX ดึง Location ตาม Line
@work_bp.route('/get_locations/<int:line_id>')
def get_locations(line_id):
    locations = Location.query.filter_by(line_id=line_id).all()
    data = [{"id": l.id, "name": l.name} for l in locations]
    return jsonify(data)
    

    # Endpoint สำหรับ AJAX ดึง DeviceType ตาม Line
@work_bp.route('/get_device_types/<int:line_id>')
def get_device_types(line_id):
    device_types = DeviceType.query.filter_by(line_id=line_id).all()
    data = [{"id": d.id, "name": d.name} for d in device_types]
    return jsonify(data)
    

    # Endpoint สำหรับ AJAX ดึง DeviceName ตาม Location และ DeviceType
@work_bp.route('/get_device_names/<int:location_id>/<int:device_type_id>')
def get_device_names(location_id, device_type_id):
    device_names = DeviceName.query.filter_by(location_id=location_id, device_type_id=device_type_id).all()
    data = [{"id": dn.id, "name": dn.name} for dn in device_names]
    return jsonify(data)
