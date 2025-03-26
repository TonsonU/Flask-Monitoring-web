from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
import pytz
from pytz import timezone
from datetime import datetime
from app.extensions import db
from . import report_bp
from werkzeug.utils import secure_filename
from app.static import uploads



@report_bp.route('/main')
@login_required
def main():
    return render_template('report.html') 

