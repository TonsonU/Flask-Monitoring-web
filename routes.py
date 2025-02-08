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

# routes.py: เก็บเส้นทางของแอป (Routes)
from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import os
from datetime import datetime
from models import db, User, Work, Comment, Line, Location, DeviceType, DeviceName, SerialNumberHistory, ForceDataHistory, MacAddressHistory,ModuleHistory
from forms import RegisterForm, LoginForm, CreateForm, EditForm,CommentForm, EditSerialNumberForm,EditForceDataForm,EditMacAddressForm,EditModuleForm
from pytz import timezone
import pytz

# Routes for the app
def init_app(app):
    # Route สำหรับการสมัครสมาชิก (Register)
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role')  # รับค่า Role จากฟอร์ม

            # ตรวจสอบว่ามี username นี้ในระบบหรือไม่
            if User.query.filter_by(username=username).first():
                flash("Username already exists. Please choose a different one.", "danger")
                return redirect(url_for('register'))

            # ใช้ generate_password_hash โดยไม่ระบุ method (ค่าเริ่มต้นคือ pbkdf2:sha256)
            hashed_password = generate_password_hash(password)

            # บันทึกผู้ใช้ใหม่ลงในฐานข้อมูล
            new_user = User(username=username, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! You can now login.", "success")
            return redirect(url_for('login'))

        return render_template('register.html')
    

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        user_found = True  # Default value, assume user exists

        if request.method == 'POST':
            username = request.form['username']
            new_password = request.form['new_password']

            # ค้นหาผู้ใช้ในฐานข้อมูล
            user = User.query.filter_by(username=username).first()

            if user:
                # อัปเดตรหัสผ่านใหม่
                hashed_password = generate_password_hash(new_password)
                user.password = hashed_password
                db.session.commit()

                flash("Password updated successfully.", "success")
                return redirect(url_for('login'))
            else:
                # ถ้าไม่พบผู้ใช้ให้แสดงข้อความ
                user_found = False
                #flash("User not found. Please register.", "danger")

        return render_template('forgot_password.html', user_found=user_found)


    # Route สำหรับการเข้าสู่ระบบ (Login)
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # ดึงผู้ใช้จากฐานข้อมูล
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):  # ตรวจสอบรหัสผ่าน
                login_user(user)
                #flash("Logged in successfully!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid username or password.", "danger")
        return render_template('login.html')
    

    # Route สำหรับการออกจากระบบ (Logout)
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for('login'))
    
    
    @app.route('/')
    @login_required
    def index():
        works = Work.query.all()
        return render_template("index.html", works=works)
    
    
    @app.route('/create', methods=['GET', 'POST'])
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
                link=link
            )

            # บันทึกข้อมูลลงในฐานข้อมูล
            db.session.add(new_work)
            db.session.commit()
            flash('บันทึกข้อมูลสำเร็จ', "success")

            # หลังจากบันทึกข้อมูลเสร็จแล้ว ให้รีไดเรกต์ไปที่หน้า index
            return redirect(url_for('index'))
        return render_template("create.html", form=form)
    
    
    # Route สำหรับจัดการ Work ที่ปิดแล้ว
    @app.route('/closed',methods=['GET','POST'])
    @login_required
    def closed():
        works = Work.query.all()  
        return render_template("closed.html", works=works)
    
    
    # Route สำหรับจัดการ Work ที่ปิดแล้ว
    @app.route('/open',methods=['GET','POST'])
    @login_required
    def open():
        works = Work.query.all()  
        return render_template("open.html", works=works)
    

    # Route สำหรับการลบ Work (เฉพาะ admin)    
    @app.route('/delete/<int:number>', methods=['POST'])
    @login_required
    def deleteWork(number):
        if current_user.role != 'admin':
            flash("You don't have permission to delete work orders.", "danger")
            return redirect(url_for('index'))
        works = Work.query.filter_by(number=number).first()
        if works:
            db.session.delete(works)
            db.session.commit()
            flash("Work deleted successfully!", "success")
        else:
            flash("Work not found.", "danger")
        #return redirect(url_for('index'))
        return redirect(url_for('index'))
    
    
    # Route สำหรับทำการแก้ไขข้อมูล 
    @app.route('/edit/<number>', methods=['GET', 'POST'], endpoint='edit')
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

            if has_changed:
                db.session.commit()
                flash("Work updated successfully!", "success")
                return redirect(url_for('index'))
            else:
                flash("ไม่มีการเปลี่ยนแปลงข้อมูลใดๆ.", "info")
                return redirect(url_for('edit', number=number))

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
    
    
    # Route สำหรับดูรายละเอียดเพิ่มเติมของ Work   
    @app.route('/work/<int:number>', methods=['GET', 'POST'])
    @login_required
    def work_detail(number):
        # ดึงข้อมูลจากตาราง Work โดยใช้ number
        works = Work.query.get(number)
    
        # ตรวจสอบว่ามีข้อมูลหรือไม่
        if not works:
            abort(404)
    
        # ดึงข้อมูลที่เชื่อมโยงกับ Work
        line = works.line
        location = works.location
        device_type = works.device_type
        device_name = works.device_name

        # สร้างแบบฟอร์มคอมเมนต์
        form = CommentForm()
        if form.validate_on_submit():
            image_url = None
            # จัดการอัปโหลดรูปภาพ
            if form.image.data:
                image_file = form.image.data
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('static/uploads', filename)
                image_file.save(image_path)
                image_url = url_for('static', filename='uploads/' + filename)
                
            # แปลง PDF Path เป็น URL หากจำเป็น
            pdf_url = form.pdf_url.data.strip() if form.pdf_url.data else None

            # กำหนดเขตเวลาของประเทศไทย
            thailand_tz = pytz.timezone('Asia/Bangkok')
            timestamp = datetime.now(thailand_tz)

            
            # สร้าง Comment ใหม่
            comment = Comment(
                content=form.comment.data,
                pdf_url=pdf_url,
                image_url=image_url,
                work_id=number,
                user_id=current_user.id,
                timestamp=timestamp  # บันทึกเวลาที่คอมเมนต์ถูกโพสต์ตามเขตเวลาของประเทศไทย

            )
            db.session.add(comment)
            db.session.commit()
            print("Comment added to DB:", comment)
            flash('Your comment has been posted.', 'success')
            return redirect(url_for('work_detail', number=number))

        # ดึงคอมเมนต์ที่เกี่ยวข้องกับ Work
        comments = Comment.query.filter_by(work_id=number).order_by(Comment.timestamp.desc()).all()

        # ส่งข้อมูลไปยัง template
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
    
    # Route สำหรับลบคอมเมนต์
    @app.route('/delete_comment/<int:comment_id>', methods=['POST'])
    @login_required
    def delete_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        work_id = comment.work_id
        if comment.user_id != current_user.id:
            abort(403)  # Forbidden
        
        # ลบไฟล์รูปภาพถ้ามี
        if comment.image_url:
            image_path = os.path.join('static', comment.image_url.split('static/')[-1])
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(comment)
        db.session.commit()
        flash('Your comment has been deleted.', 'info')
        return redirect(url_for('work_detail', number=work_id))
    

    # Endpoint สำหรับ AJAX ดึง Location ตาม Line
    @app.route('/get_locations/<int:line_id>')
    def get_locations(line_id):
        locations = Location.query.filter_by(line_id=line_id).all()
        data = [{"id": l.id, "name": l.name} for l in locations]
        return jsonify(data)
    

    # Endpoint สำหรับ AJAX ดึง DeviceType ตาม Line
    @app.route('/get_device_types/<int:line_id>')
    def get_device_types(line_id):
        device_types = DeviceType.query.filter_by(line_id=line_id).all()
        data = [{"id": d.id, "name": d.name} for d in device_types]
        return jsonify(data)
    

    # Endpoint สำหรับ AJAX ดึง DeviceName ตาม Location และ DeviceType
    @app.route('/get_device_names/<int:location_id>/<int:device_type_id>')
    def get_device_names(location_id, device_type_id):
        device_names = DeviceName.query.filter_by(location_id=location_id, device_type_id=device_type_id).all()
        data = [{"id": dn.id, "name": dn.name} for dn in device_names]
        return jsonify(data)
    
    
    @app.route('/inventory')
    @login_required
    def inventory():
        devices = DeviceName.query.all()
        return render_template("inventory.html", devices=devices)
    
    @app.route('/inventory/IL', endpoint='inventory_il')
    @login_required
    def inventory_il():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'IL').all()
        return render_template("inventory_il.html", devices=devices)
    
    @app.route('/inventory/tap', endpoint='inventory_tap')
    @login_required
    def inventory_tap():
        # กรองข้อมูลเพื่อแสดงเฉพาะ Device Type ที่เป็น TAP
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'TAP').all()
        return render_template("inventory_tap.html", devices=devices)
    
    @app.route('/inventory/emp', endpoint='inventory_emp')
    @login_required
    def inventory_emp():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'EMP').all()
        return render_template("inventory_emp.html", devices=devices)
    
    @app.route('/inventory/pid', endpoint='inventory_pid')
    @login_required
    def inventory_pid():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'PID').all()
        return render_template("inventory_pid.html", devices=devices)
    
    @app.route('/inventory/obc', endpoint='inventory_obc')
    @login_required
    def inventory_obc():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'OBC').all()
        return render_template("inventory_obc.html", devices=devices)
    
    @app.route('/inventory/tel', endpoint='inventory_tel')
    @login_required
    def inventory_tel():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'TEL').all()
        return render_template("inventory_tel.html", devices=devices)
    
    @app.route('/inventory/ups', endpoint='inventory_ups')
    @login_required
    def inventory_ups():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'UPS').all()
        return render_template("inventory_ups.html", devices=devices)
    
    @app.route('/inventory/point', endpoint='inventory_point')
    @login_required
    def inventory_point():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Point').all()
        force_data_history = {device.id: ForceDataHistory.query.filter_by(device_id=device.id).order_by(ForceDataHistory.changed_at.desc()).first() for device in devices}

        # อัปเดตค่า force_data ของ device จาก ForceDataHistory
        for device in devices:
            if force_data_history[device.id]:
                force_values = [
                    str(force_data_history[device.id].plus_before),
                    str(force_data_history[device.id].minus_before),
                    str(force_data_history[device.id].plus_after),
                    str(force_data_history[device.id].minus_after)
                ]
                device.force_data = ", ".join([value for value in force_values if value != 'None'])



        return render_template("inventory_point.html", devices=devices, force_data_history=force_data_history)
    
    @app.route('/inventory/balise', endpoint='inventory_balise')
    @login_required
    def inventory_balise():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Balise').all()
        return render_template("inventory_balise.html", devices=devices)
    
    @app.route('/inventory/mitrac', endpoint='inventory_mitrac')
    @login_required
    def inventory_mitrac():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Mitrac').all()
        return render_template("inventory_mitrac.html", devices=devices)
    
    @app.route('/inventory/pli', endpoint='inventory_pli')
    @login_required
    def inventory_pli():
        devices = DeviceName.query.join(DeviceType).filter(or_(DeviceType.name == 'PLI', DeviceType.name == 'Depot Area Signal', DeviceType.name == 'Route Indicator') ).all()
        return render_template("inventory_pli.html", devices=devices)
    
    @app.route('/inventory/axle', endpoint='inventory_axle')
    @login_required
    def inventory_axle():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Axle Counter').all()
        return render_template("inventory_axle.html", devices=devices)
    
    @app.route('/inventory/trackname', endpoint='inventory_trackname')
    @login_required
    def inventory_trackname():
        devices = DeviceName.query.join(DeviceType).filter(DeviceType.name == 'Track Name Plate').all()
        return render_template("inventory_trackname.html", devices=devices)


    # Route สำหรับแก้ไข serial_number
    @app.route('/device/<int:device_id>/edit_serial', methods=['GET', 'POST'])
    @login_required
    def edit_serial_number(device_id):
        device = DeviceName.query.get_or_404(device_id)
        ref = request.args.get('ref', url_for('inventory'))  # รับค่า ref หรือใช้ default_page
        form = EditSerialNumberForm(obj=device)

        if form.validate_on_submit():
            old_serial = device.serial_number
            new_serial = form.serial_number.data
            remark = form.remark.data  # ใช้ฟิลด์จากฟอร์มตรงๆ

            if old_serial != new_serial:
                # บันทึกประวัติการเปลี่ยนแปลง
                history = SerialNumberHistory(
                    device_id=device.id,
                    old_serial_number=old_serial,
                    new_serial_number=new_serial,
                    changed_by=current_user.id,
                    remark=remark  # บันทึก remark
                )
                db.session.add(history)

                # อัปเดต serial_number
                device.serial_number = new_serial
                db.session.commit()

                flash('Serial Number updated successfully!', 'success')
                #return redirect(ref)  # เปลี่ยนเป็น 'inventory'
            else:
                flash('No changes detected.', 'info')
                #return redirect(ref)  # เปลี่ยนเป็น 'inventory'

        # ดึงประวัติการเปลี่ยนแปลง
        history_records = SerialNumberHistory.query.filter_by(device_id=device.id).order_by(SerialNumberHistory.changed_at.desc()).all()

        return render_template('edit_serial_number.html', form=form, device=device, history=history_records,ref=ref)
    

    # Route สำหรับแก้ไข force_data
    @app.route('/device/<int:device_id>/edit_force_data', methods=['GET', 'POST'])
    @login_required
    def edit_force_data(device_id):
        device = DeviceName.query.get_or_404(device_id)
        form = EditForceDataForm(obj=device)

        if form.validate_on_submit():
            try:
                plus_before = form.plus_before.data
                minus_before = form.minus_before.data
                plus_after = form.plus_after.data if form.plus_after.data else None
                minus_after = form.minus_after.data if form.minus_after.data else None
                remark = form.remark.data

                # ตั้งค่า Timezone เป็น Asia/Bangkok
                bangkok_tz = pytz.timezone('Asia/Bangkok')
                current_time = datetime.now(bangkok_tz)  # ได้เวลาปัจจุบันเป็นเวลาไทย

                # บันทึกประวัติการเปลี่ยนแปลง
                force_data_history = ForceDataHistory(
                    device_id=device.id,
                    plus_before=plus_before,
                    minus_before=minus_before,
                    plus_after=plus_after,
                    minus_after=minus_after,
                    changed_by=current_user.id,
                    remark=remark,
                    changed_at=current_time,  # บันทึกวันที่และเวลาเป็น Bangkok timezone
                )
                db.session.add(force_data_history)

                # อัปเดตค่า force_data ของ device
                force_values = [str(value) for value in [plus_before, minus_before, plus_after, minus_after] if value is not None]
                device.force_data = ", ".join(force_values)

                print(f"device.force_data: {device.force_data}")

                # บันทึกลงฐานข้อมูล
                db.session.commit()
                flash('Force Data updated successfully!', 'success')

                return redirect(url_for('edit_force_data', device_id=device.id))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error updating force data: {e}")
                flash('เกิดข้อผิดพลาดในการอัปเดตข้อมูล', 'danger')

        # ดึงประวัติการเปลี่ยนแปลง
        history_force_records = ForceDataHistory.query.filter_by(device_id=device.id).order_by(ForceDataHistory.changed_at.desc()).all()

        return render_template('edit_force_data.html', form=form, device=device, history=history_force_records)

    

    # Route สำหรับแก้ไข mac_address
    @app.route('/device/<int:device_id>/edit_mac', methods=['GET', 'POST'])
    @login_required
    def edit_mac_address(device_id):
        device = DeviceName.query.get_or_404(device_id)
        form = EditMacAddressForm(obj=device)

        if form.validate_on_submit():
            old_mac = device.mac_address
            new_mac = form.mac_address.data
            remark = form.remark.data  # ใช้ฟิลด์จากฟอร์มตรงๆ

            if old_mac != new_mac:
                # บันทึกประวัติการเปลี่ยนแปลง
                history = MacAddressHistory(
                    device_id=device.id,
                    old_mac_address=old_mac,
                    new_mac_address=new_mac,
                    changed_by=current_user.id,
                    remark=remark  # บันทึก remark
                )
                db.session.add(history)

                # อัปเดต mac_address
                device.mac_address = new_mac
                db.session.commit()

                flash('MAC Address updated successfully!', 'success')
                return redirect(url_for('edit_mac_address', device_id=device.id))  # เปลี่ยนเป็น 'inventory'
            else:
                flash('No changes detected.', 'info')
                return redirect(url_for('edit_mac_address', device_id=device.id))  # เปลี่ยนเป็น 'inventory'

        # ดึงประวัติการเปลี่ยนแปลง
        history_records = MacAddressHistory.query.filter_by(device_id=device.id).order_by(MacAddressHistory.changed_at.desc()).all()

        return render_template('edit_mac_address.html', form=form, device=device, history=history_records)
    
    # Route สำหรับแก้ไข pli_module
    @app.route('/device/<int:device_id>/edit_pli_module', methods=['GET', 'POST'])
    @login_required
    def edit_pli_module(device_id):
        device = DeviceName.query.get_or_404(device_id)
        form = EditModuleForm(obj=device)

        if form.validate_on_submit():
            old_red_module = device.red_module
            old_white_module = device.white_module
            old_yellow_module = device.yellow_module

            new_red_module = form.red_module.data
            new_white_module = form.white_module.data
            new_yellow_module = form.yellow_module.data
            remark = form.remark.data

            if old_red_module != new_red_module or old_white_module != new_white_module or old_yellow_module != new_yellow_module:
                history = ModuleHistory(
                    device_id=device.id,
                    old_red_module=old_red_module,
                    new_red_module=new_red_module,
                    old_white_module=old_white_module,
                    new_white_module=new_white_module,
                    old_yellow_module=old_yellow_module,
                    new_yellow_module=new_yellow_module,
                    changed_by=current_user.id,
                    remark=remark
                )
                db.session.add(history)

                device.red_module = new_red_module
                device.white_module = new_white_module
                device.yellow_module = new_yellow_module
                db.session.commit()

                flash('PLI Module data updated successfully!', 'success')
            else:
                flash('No changes detected.', 'info')

            return redirect(url_for('edit_pli_module', device_id=device.id))

        history_records = ModuleHistory.query.filter_by(device_id=device.id).order_by(ModuleHistory.changed_at.desc()).all()
        return render_template('edit_pli_module.html', form=form, device=device, history=history_records)
    
    # Route สำหรับแสดงข้อมูล force_data ในรูปแบบกราฟ
    @app.route('/api/get_force_data/<int:device_id>', methods=['GET'])
    @login_required
    def get_force_graph_data(device_id):
        try:
            # Query ข้อมูลจากฐานข้อมูล
            records = ForceDataHistory.query.filter_by(device_id=device_id).order_by(ForceDataHistory.changed_at).all()

            if not records:
                app.logger.warning(f"No records found for device_id {device_id}")
                return jsonify({"error": "No data found"}), 404

            # แปลงข้อมูลจากฐานข้อมูลให้อยู่ในรูปแบบ JSON
            graph_data = {}
            for record in records:
                edit_date = record.changed_at.strftime('%Y-%m-%d')  # เปลี่ยนวันที่เป็น string
                if edit_date not in graph_data:
                    graph_data[edit_date] = {
                        'plus_before': 0,
                        'minus_before': 0,
                        'plus_after': 0,
                        'minus_after': 0
                    }
                
                # แปลงค่าที่ได้จากฐานข้อมูลให้เป็นตัวเลขก่อน
                graph_data[edit_date]['plus_before'] += int(record.plus_before or 0)
                graph_data[edit_date]['minus_before'] += int(record.minus_before or 0)
                graph_data[edit_date]['plus_after'] += int(record.plus_after or 0)
                graph_data[edit_date]['minus_after'] += int(record.minus_after or 0)

            return jsonify(graph_data)
        
        except ValueError as e:
            app.logger.error(f"Error converting data to int: {e}")
            return jsonify({"error": "Invalid data type in database"}), 500
        except Exception as e:
            app.logger.error(f"Error fetching data for device_id {device_id}: {e}")
            return jsonify({"error": "Internal Server Error"}), 500

    # Route สำหรับลบ force_data
    @app.route('/delete_force_data/<int:record_id>', methods=['POST'])
    @login_required
    def delete_force_data(record_id):
        record = ForceDataHistory.query.get_or_404(record_id)

        # ตรวจสอบว่าเป็นเจ้าของข้อมูลหรือไม่
        if record.changed_by != current_user.id:
            flash("คุณไม่มีสิทธิ์ลบข้อมูลนี้", "danger")
            return jsonify({"error": "Unauthorized"}), 403

        try:
            db.session.delete(record)
            db.session.commit()
            flash("ลบข้อมูลสำเร็จ!", "success")
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting record {record_id}: {e}")
            return jsonify({"error": "เกิดข้อผิดพลาดในการลบข้อมูล"}), 500



        

    



    """
    @app.before_request
    def setup_db():
        db.create_all()

        if Line.query.count() == 0:
            # สร้าง Line
            skt3 = Line(name="SKT3")
            depot_kk = Line(name="Depot KK")
            db.session.add(skt3)
            db.session.add(depot_kk)
            db.session.commit()

            # สร้าง Location สำหรับ SKT3 
            skt3_locations = [
                "NEOL-N24", "N24", "N24-N23", "N23", "N23-N22", "N22", 
                "N22-N21", "N21", "N21-N20", "N20", "N20-N19", "N19", 
                "N19-N18", "N18", "N18-N17", "N17", "N17-N16", "N16", 
                "N16-N15", "N15", "N15-N14", "N14", "N14-N13", "N13", 
                "N13-N12", "N12", "N12-N11", "N11", "N11-N10", "N10", 
                "N10-N9", "N9"
            ]

            # เพิ่ม Location สำหรับ SKT3
            for loc_name in skt3_locations:
                db.session.add(Location(name=loc_name, line_id=skt3.id))

            # สร้าง Location สำหรับ Depot KK
            depot_kk_locations = [
                "S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", 
                "S09", "S10", "S11", "S12", "S13", "S14", "S15", "S16", 
                "S17", "S18", "S19", "S20", "W01", "W02", "W03", "W04", 
                "W05", "W06", "W07", "Transfer Track EB", "Transfer Track NB", 
                "Shunting Track", "Test Track", "PW1", "PW2"
            ]

            # เพิ่ม Location สำหรับ Depot KK
            for loc_name in depot_kk_locations:
                db.session.add(Location(name=loc_name, line_id=depot_kk.id))
            db.session.commit()

            # DeviceType สำหรับ SKT3: PLI, Balise, Point
            db.session.add(DeviceType(name="PLI", line_id=skt3.id))
            db.session.add(DeviceType(name="Balise", line_id=skt3.id))
            db.session.add(DeviceType(name="Point", line_id=skt3.id))

            # DeviceType สำหรับ Depot KK: PLI, Balise, Point, Axle Counter
            db.session.add(DeviceType(name="PLI", line_id=depot_kk.id))
            db.session.add(DeviceType(name="Balise", line_id=depot_kk.id))
            db.session.add(DeviceType(name="Point", line_id=depot_kk.id))
            db.session.add(DeviceType(name="Axle Counter", line_id=depot_kk.id))
            db.session.commit()

            # เพิ่ม DeviceName ตัวอย่าง
            skt3_pli = DeviceType.query.filter_by(name="PLI", line_id=skt3.id).first()
            skt3_balise = DeviceType.query.filter_by(name="Balise", line_id=skt3.id).first()
            skt3_point = DeviceType.query.filter_by(name="Point", line_id=skt3.id).first()

            depot_pli = DeviceType.query.filter_by(name="PLI", line_id=depot_kk.id).first()
            depot_balise = DeviceType.query.filter_by(name="Balise", line_id=depot_kk.id).first()
            depot_point = DeviceType.query.filter_by(name="Point", line_id=depot_kk.id).first()
            depot_axle = DeviceType.query.filter_by(name="Axle Counter", line_id=depot_kk.id).first()

            n9 = Location.query.filter_by(name="N9", line_id=skt3.id).first()
            s01 = Location.query.filter_by(name="S01", line_id=depot_kk.id).first()

            db.session.add(DeviceName(name="PLI1441", device_type_id=skt3_pli.id, location_id=n9.id))
            db.session.add(DeviceName(name="F9000", device_type_id=skt3_balise.id, location_id=n9.id))
            db.session.add(DeviceName(name="T5661", device_type_id=skt3_point.id, location_id=n9.id))

            db.session.add(DeviceName(name="PLI1441", device_type_id=depot_pli.id, location_id=s01.id))
            db.session.add(DeviceName(name="F9000", device_type_id=depot_balise.id, location_id=s01.id))
            db.session.add(DeviceName(name="T5661", device_type_id=depot_point.id, location_id=s01.id))
            db.session.add(DeviceName(name="A2445/2447", device_type_id=depot_axle.id, location_id=s01.id))

            db.session.commit()
    """

            
    # ลบข้อมูลทั้งหมดในตาราง Work
    @app.route('/clear-tables', methods=['GET'])
    @login_required 
    def clear_tables():
        if current_user.role != 'admin':
            flash("You don't have permission to clear tables.", "danger")
            return redirect(url_for('index'))
        
        #db.session.query(User).delete()
        db.session.query(Work).delete()
        db.session.query(Line).delete()
        db.session.query(Location).delete()
        db.session.query(DeviceType).delete()
        db.session.query(DeviceName).delete()
        db.session.query(SerialNumberHistory).delete()
        db.session.query(ForceDataHistory).delete()
        db.session.query(Comment).delete()
        db.session.query(MacAddressHistory).delete()
        
        db.session.commit()
        flash("Table cleared!", "success")
        return redirect(url_for('index'))
    
