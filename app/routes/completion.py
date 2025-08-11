from flask import Blueprint, render_template
from flask_login import login_required

completion_bp = Blueprint('completion', __name__)

@completion_bp.route('/completion')
@login_required
def completion():
    return render_template('completion.html')
