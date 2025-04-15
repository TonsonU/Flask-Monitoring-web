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

knowledge_bp = Blueprint('knowledge_base', __name__, template_folder='templates/knowledge_base')

from . import routes  # Import routes.py
