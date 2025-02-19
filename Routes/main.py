from flask import Blueprint, render_template
from flask_login import login_required
from models import Work

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    works = Work.query.all()
    return render_template("index.html", works=works)
