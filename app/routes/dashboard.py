from flask import Blueprint, render_template, abort, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Project
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

# ===== Dashboard page =====
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # With event listeners, no need to recalculate all status here
    projects = Project.query.filter_by(user_id=current_user.id) \
                            .order_by(Project.created_date.desc()).all()

    return render_template(
        'dashboard.html',
        projects=projects,
        current_user=current_user
    )


# ===== Add Project =====
@dashboard_bp.route('/dashboard/add_project', methods=['POST'])
@login_required
def add_project():
    data = request.get_json()
    title = (data.get('title') or '').strip()
    pi = (data.get('pi') or '').strip() or None
    institute = (data.get('institute') or '').strip() or None
    date_str = (data.get('date') or '').strip()

    if not title:
        return jsonify(error="Title is required"), 400

    try:
        created_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
    except ValueError:
        return jsonify(error="Invalid date format. Use YYYY-MM-DD."), 400

    project = Project(
        title=title,
        pi=pi,
        institute=institute,
        user_id=current_user.id,
        created_date=created_date
    )

    # Initial status calculation
    project.update_status()

    db.session.add(project)
    db.session.commit()

    return jsonify(
        success=True,
        project_id=project.id,
        created_date=project.created_date.strftime("%d/%m/%Y"),
        status=project.status
    )


# ===== Update Project =====
@dashboard_bp.route('/dashboard/update_project/<int:project_id>', methods=['POST'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        abort(403)

    data = request.get_json()
    project.title = data.get('title', project.title)
    project.pi = data.get('pi') or None
    project.institute = data.get('institute') or None

    # Optionally recalc status — mostly redundant with events
    project.update_status()

    db.session.commit()
    return jsonify(success=True, status=project.status)


# ===== Delete Project =====
@dashboard_bp.route('/dashboard/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify(success=False, error="Forbidden"), 403

    db.session.delete(project)
    db.session.commit()

    return jsonify(success=True, message="Project deleted successfully")
