# routes/rsqr.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from io import BytesIO
from reportlab.pdfgen import canvas
from app import db
from app.models.dashboard import Project
from app.models.rsqr import RSQR
from app.forms import RSQRForm
import os
from werkzeug.utils import secure_filename

rsqr_bp = Blueprint('rsqr', __name__)

@rsqr_bp.route('/rsqr', methods=['GET', 'POST'])
@rsqr_bp.route('/rsqr/<int:project_id>', methods=['GET', 'POST'])
@login_required
def rsqr(project_id=None):
    form = RSQRForm()
    project = None
    rsqr = None

    if project_id:
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard.dashboard'))

        rsqr = project.rsqr

    if request.method == 'POST' and ('save' in request.form or 'next' in request.form) and form.validate_on_submit():
        if not project:
            project = Project(
                title=form.title.data,
                user_id=current_user.id
            )
            db.session.add(project)
            db.session.commit()

        # Handle PDF upload
        pdf_filename = None
        if form.pdf_file.data:
            pdf_file = form.pdf_file.data
            filename = secure_filename(pdf_file.filename)
            upload_folder = os.path.join('app', 'static', 'uploads', 'rsqr')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            pdf_file.save(file_path)
            pdf_filename = filename

        if rsqr:
            rsqr.title = form.title.data
            rsqr.requirements = form.requirements.data
            rsqr.justification = form.justification.data
            rsqr.deliverables = form.deliverables.data
            if pdf_filename:
                rsqr.pdf_filename = pdf_filename
        else:
            rsqr = RSQR(
                title=form.title.data,
                requirements=form.requirements.data,
                justification=form.justification.data,
                deliverables=form.deliverables.data,
                pdf_filename=pdf_filename,
                project_id=project.id
            )
            db.session.add(rsqr)

        project.update_status()
        db.session.commit()

        if 'next' in request.form:
            return redirect(url_for('management_council.management_council', project_id=project.id))
        else:
            flash('RSQR saved successfully!', 'success')
            return redirect(url_for('rsqr.rsqr', project_id=project.id))

    # Pre-fill form fields for GET request
    if project and rsqr:
        form.title.data = project.title
        form.requirements.data = rsqr.requirements
        form.justification.data = rsqr.justification
        form.deliverables.data = rsqr.deliverables

    return render_template('rsqr.html', form=form, project=project)
