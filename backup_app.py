from flask import Flask, render_template, request, session, flash, redirect, url_for, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, RadioField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, URL, ValidationError
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
import enum
from wtforms.widgets import Input


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Model สำหรับจัดการผู้ใช้งาน
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # ควรแฮชรหัสผ่าน
    role = db.Column(db.String(20), nullable=False)   #role เก็บเป็น 'admin' หรือ 'user'

    def __repr__(self):
        return f"<User {self.username}>"

@login_manager.user_loader 
def load_user(user_id): 
    return User.query.get(int(user_id))

# Model สำหรับ Work
class Work(db.Model):
    number = db.Column(db.Integer, primary_key=True, autoincrement=True)  # เลข 6 หลัก รันอัตโนมัติ
    create_date = db.Column(db.DateTime, default=datetime.utcnow)  # วันที่และเวลา สร้างอัตโนมัติ
    work_order = db.Column(db.String(50), nullable=False)          # Work Order
    equipment = db.Column(db.String(50), nullable=False)           # Equipment ID
    description = db.Column(db.Text, nullable=False)               # รายละเอียด
    location = db.Column(db.String(50), nullable=False)            # ตำแหน่ง
    report_by = db.Column(db.String(50), nullable=False)           # ผู้รายงาน
    status = db.Column(db.String(20), nullable=False, default="open")  # สถานะ (ค่าเริ่มต้น: open)
    action = db.Column(db.Text, nullable=True)                     # รายละเอียดของการดำเนินการ
    link = db.Column(db.String(255), nullable=True)                # URL ของไฟล์

    def __repr__(self):
        return f"<Work {self.number}>"

# ฟอร์มสำหรับการสมัครสมาชิก (Register)
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

    def validate_password(self, password):
        if self.password.data != self.confirm_password.data:
            raise ValidationError('Passwords must match.')

# ฟอร์มสำหรับการ Login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateForm(FlaskForm):
    create_date = StringField("Create Date", validators=[DataRequired()])             # วันที่และเวลา
    work_order = StringField("Work Order", validators=[DataRequired()])               # Work Order
    equipment = StringField("Equipment", validators=[DataRequired()])                 # Equipment ID
    description = TextAreaField("Description", validators=[DataRequired()])           # รายละเอียด
    location = StringField("Location", validators=[DataRequired()])                   # ตำแหน่ง
    report_by = StringField("Report By", validators=[DataRequired()])                 # ผู้รายงาน
    status = SelectField("Status", choices=[("Open", "Open"), ("Closed", "Closed")], validators=[DataRequired()])  # สถานะ
    action = TextAreaField("Action", validators=[DataRequired()])                     # รายละเอียดของการดำเนินการ
    link = StringField("Link", validators=[DataRequired(),])                       # URL ของไฟล์
    submit = SubmitField("Submit")


class EditForm(FlaskForm):
    create_date = StringField("Create Date", validators=[DataRequired()])             # วันที่และเวลา
    work_order = StringField("Work Order", validators=[DataRequired()])               # Work Order
    equipment = StringField("Equipment", validators=[DataRequired()])                 # Equipment ID
    description = TextAreaField("Description", validators=[DataRequired()])           # รายละเอียด
    location = StringField("Location", validators=[DataRequired()])                   # ตำแหน่ง
    report_by = StringField("Report By", validators=[DataRequired()])                 # ผู้รายงาน
    status = SelectField("Status", choices=[("Open", "Open"), ("Closed", "Closed")], validators=[DataRequired()])  # สถานะ
    action = TextAreaField("Action", validators=[DataRequired()])                     # รายละเอียดของการดำเนินการ
    link = StringField("Link", validators=[DataRequired(),])                       # URL ของไฟล์
    submit = SubmitField("Submit")
    

    
    
# ลบข้อมูลทั้งหมดในตาราง Work
'''@app.route('/clear-tables', methods=['GET']) 
def clear_tables():
    db.session.query(Work).delete()
    db.session.commit()
    return "Table cleared!" '''

# สร้างตารางในฐานข้อมูล 
@app.before_request
def create_tables():
    db.create_all()

# Route สำหรับการสร้าง Work
@app.route('/create',methods=['GET','POST'])
@login_required
def create():
    form = CreateForm()

    if form.validate_on_submit():
        flash('บันทึกข้อมูลสำเร็จ', "success")

        # สร้าง object Work ใหม่จากข้อมูลในฟอร์ม
        create_date = datetime.strptime(form.create_date.data, '%Y-%m-%d %H:%M') if form.create_date.data else None

        new_work = Work(
            create_date=create_date,
            work_order=form.work_order.data,
            equipment=form.equipment.data,
            description=form.description.data,
            location=form.location.data,
            report_by=form.report_by.data,
            status=form.status.data,
            action=form.action.data,
            link=form.link.data
        )

        # บันทึกข้อมูลลงในฐานข้อมูล
        db.session.add(new_work)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template("create.html", form=form)
# Route สำหรับจัดการ Work
@app.route('/',methods=['GET','POST'])
@login_required
def index():
    works = Work.query.all()  
    return render_template("index.html", works=works)

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



if __name__ == "__main__":
    app.run(debug=True)
    