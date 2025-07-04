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

from flask import Blueprint

report_bp = Blueprint('report', __name__, template_folder='templates/report')

from . import routes  # Import routes.py
