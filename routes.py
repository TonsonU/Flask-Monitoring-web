# routes.py: เก็บเส้นทางของแอป (Routes)
from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Work
from forms import RegisterForm, LoginForm, CreateForm, EditForm
from models import Line, Location, DeviceType, DeviceName

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
            create_date = datetime.strptime(form.create_date.data, '%Y-%m-%d %H:%M') if form.create_date.data else None

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

        return render_template('create.html', form=form)
   
    # Route สำหรับจัดการ Work ที่ปิดแล้ว
    @app.route('/closed',methods=['GET','POST'])
    @login_required
    def closed():
        works = Work.query.all()  
        return render_template("closed.html", works=works)

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
        form = EditForm()

        if form.validate_on_submit():
            if form.create_date.data:
                works.create_date = datetime.strptime(form.create_date.data, "%Y-%m-%d %H:%M")

            works.work_order = form.work_order.data
            works.description = form.description.data
            works.report_by = form.report_by.data
            works.status = form.status.data
            works.link = form.link.data

            # เก็บค่า ForeignKey
            works.line = form.line_name.data
            works.location = form.location_name.data
            works.device_type = form.device_type_name.data
            works.device_name = form.device_name.data

            db.session.commit()
            flash("Work updated successfully!", "success")
            return redirect(url_for('index'))

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
    @app.route('/work/<int:number>', methods=['GET'])
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

        # ส่งข้อมูลไปยัง template
        return render_template("work_detail.html", works=works, line=line, location=location, device_type=device_type, device_name=device_name)

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
            
    # ลบข้อมูลทั้งหมดในตาราง Work
    @app.route('/clear-tables', methods=['GET'])
    @login_required 
    def clear_tables():
        if current_user.role != 'admin':
            flash("You don't have permission to clear tables.", "danger")
            return redirect(url_for('index'))
        db.session.query(Work).delete()
        db.session.commit()
        flash("Table cleared!", "success")
        return redirect(url_for('index'))