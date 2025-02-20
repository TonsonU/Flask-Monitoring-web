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

from flask import flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Work, Comment, Line, Location, DeviceType, DeviceName, SerialNumberHistory, ForceDataHistory, MacAddressHistory
from flask import Blueprint

clear_tables_bp = Blueprint('clear_tables', __name__)

# ลบข้อมูลทั้งหมดในตาราง Work
@clear_tables_bp.route('/clear-tables', methods=['GET'])
@login_required 
def clear_tables():
        if current_user.role != 'admin':
            flash("You don't have permission to clear tables.", "danger")
            return redirect(url_for('main.index'))
        
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
        return redirect(url_for('main.index'))