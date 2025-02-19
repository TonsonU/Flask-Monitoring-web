from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import os
from datetime import datetime
from models import db, User, Work, Comment, Line, Location, DeviceType, DeviceName, SerialNumberHistory, ForceDataHistory, MacAddressHistory, ModuleHistory, KnowledgeBase
from forms import RegisterForm, LoginForm, CreateForm, EditForm,CommentForm, EditSerialNumberForm,EditForceDataForm,EditMacAddressForm,EditModuleForm,KnowledgeBaseForm
from pytz import timezone
import pytz
from flask import Blueprint

clear_tables_bp = Blueprint('clear_tables', __name__)

# ลบข้อมูลทั้งหมดในตาราง Work
@clear_tables_bp.route('/clear-tables', methods=['GET'])
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