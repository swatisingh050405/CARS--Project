from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from flask_login import login_required, current_user
from app import db
from app.models.dashboard import Project
from app.models.management_council import ManagementCouncil
from app.forms import ManagementCouncilForm
from werkzeug.utils import secure_filename
import os

management_council_bp = Blueprint('management_council', __name__)

@management_council_bp.route('/management-council/<int:project_id>', methods=['GET', 'POST'])
@login_required
def management_council(project_id):
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for('dashboard.dashboard'))

    form = ManagementCouncilForm()
    existing_council = ManagementCouncil.query.filter_by(project_id=project.id).first()

    if form.validate_on_submit():
        if not existing_council:
            existing_council = ManagementCouncil(project_id=project.id)
            db.session.add(existing_council)

        # Fill form data
        existing_council.council_date = form.council_date.data
        existing_council.chairperson = form.chairperson.data
        existing_council.venue = form.venue.data              # ✅ Added
        existing_council.time = form.time.data 
        existing_council.title = form.title.data
        existing_council.pdc = form.pdc.data
        existing_council.cost = form.cost.data

        # Handle PDF upload
        if form.council_pdf.data:
             filename = secure_filename(form.council_pdf.data.filename)
             folder = os.path.join(app.config['UPLOAD_FOLDER'])  
             os.makedirs(folder, exist_ok=True)  # ✅ Create folder if not exists
             filepath = os.path.join(folder, filename)
             form.council_pdf.data.save(filepath)
             existing_council.council_pdf = filename
        # Update project status
        db.session.commit()
        if 'save' in request.form:
            flash(' management council Saved successfully!', 'success')
            return redirect(url_for('management_council.management_council', project_id=project.id))

        elif 'next' in request.form:
            return redirect(url_for('offer_bp.offer_evaluation', project_id=project.id))
        
        elif 'back' in request.form:
         return redirect(url_for('rsqr.rsqr', project_id=project.id))
    # Pre-fill form if data exists
    if existing_council:
        form.council_date.data = existing_council.council_date
        form.chairperson.data = existing_council.chairperson
        form.title.data = existing_council.title
        form.venue.data = existing_council.venue             
        form.time.data = existing_council.time               
        form.pdc.data = existing_council.pdc
        form.cost.data = existing_council.cost               
    is_viewing_existing = bool(existing_council and existing_council.council_date)

    return render_template(
        'council.html',
        form=form,
        project=project,
        is_viewing_existing=is_viewing_existing
    )
