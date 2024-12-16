# routes.py: เก็บเส้นทางของแอป (Routes)
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Work
from forms import RegisterForm, LoginForm, CreateForm, EditForm

# Routes for the app
def init_app(app):
    @app.route('/')
    @login_required
    def index():
        works = Work.query.all()
        return render_template("index.html", works=works)

    @app.route('/create', methods=['GET', 'POST'])
    @login_required
    def create():
        form = CreateForm()
        if form.validate_on_submit():
            new_work = Work(
                create_date=datetime.strptime(form.create_date.data, '%Y-%m-%d %H:%M'),
                work_order=form.work_order.data,
                equipment=form.equipment.data,
                description=form.description.data,
                location=form.location.data,
                report_by=form.report_by.data,
                status=form.status.data,
                action=form.action.data,
                link=form.link.data
            )
            db.session.add(new_work)
            db.session.commit()
            flash('บันทึกข้อมูลสำเร็จ', "success")
            return redirect(url_for('index'))
        return render_template("create.html", form=form)
    # Route สำหรับจัดการ Work ที่ปิดแล้ว
    @app.route('/closed',methods=['GET','POST'])
    @login_required
    def closed():
        works = Work.query.all()  
        return render_template("closed.html", works=works)

    # Route สำหรับการลบ Work (เฉพาะ admin)    
    @app.route('/delete/<int:number>', methods=['GET'])
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
        return redirect("/")

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

    # Route สำหรับทำการแก้ไขข้อมูล 
    @app.route('/edit/<int:number>', methods=['GET','POST'])
    @login_required
    def editWork(number):
        works = Work.query.filter_by(number=number).first()
        form = EditForm()
        
        if form.validate_on_submit():
            works.create_date = form.create_date.data
            works.work_order = form.work_order.data
            works.equipment = form.equipment.data
            works.description = form.description.data
            works.location = form.location.data
            works.report_by = form.report_by.data
            works.status = form.status.data
            works.action = form.action.data
            works.link = form.link.data
            
            date_object = datetime.strptime(works.create_date, "%Y-%m-%d %H:%M")
            works = Work.query.get(number)
            works.create_date = date_object
            
            
            db.session.commit()
            flash("Work updated successfully!", "success")
            return redirect(url_for('index'))
            
        if request.method == 'GET':
            form.create_date.data = works.create_date
            form.work_order.data = works.work_order
            form.equipment.data = works.equipment
            form.description.data = works.description
            form.location.data = works.location
            form.report_by.data = works.report_by
            form.status.data = works.status
            form.action.data= works.action
            form.link.data = works.link
            
        return render_template("edit.html",form=form, works=works)

    # Route สำหรับดูรายละเอียดเพิ่มเติมของ Work   
    @app.route('/work/<int:number>', methods=['GET'])
    @login_required
    def work_detail(number):
        works = Work.query.get(number)
        if not works:
            abort(404)
        return render_template("work_detail.html", works=works)
        # เพิ่ม route อื่นๆ เช่น edit, delete, login, register, logout เป็นต้น
