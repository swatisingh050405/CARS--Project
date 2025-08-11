from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Project, NDASOC
from app.forms import NDASOCForm

nda_soc_bp = Blueprint('nda_soc', __name__)

@nda_soc_bp.route('/nda-soc/<int:project_id>', methods=['GET', 'POST'])
@login_required
def nda_soc(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))

    form = NDASOCForm()
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Check if NDA & SOC record exists
    record = NDASOC.query.filter_by(project_id=project_id).first()
    if not record:
        record = NDASOC(project_id=project_id)
        db.session.add(record)

    if request.method == 'POST' and form.validate_on_submit():
        # NDA file handling
        if form.nda_pdf.data:
            if record.nda_pdf:
                old_nda = os.path.join(upload_folder, record.nda_pdf)
                if os.path.exists(old_nda):
                    os.remove(old_nda)
            nda_filename = secure_filename(form.nda_pdf.data.filename)
            form.nda_pdf.data.save(os.path.join(upload_folder, nda_filename))
            record.nda_pdf = nda_filename

        # SOC file handling
        if form.soc_pdf.data:
            if record.soc_pdf:
                old_soc = os.path.join(upload_folder, record.soc_pdf)
                if os.path.exists(old_soc):
                    os.remove(old_soc)
            soc_filename = secure_filename(form.soc_pdf.data.filename)
            form.soc_pdf.data.save(os.path.join(upload_folder, soc_filename))
            record.soc_pdf = soc_filename

        
        db.session.commit()

        if 'save' in request.form:
            flash(' nda_soc Saved successfully!', 'success')
            return redirect(url_for('nda_soc.nda_soc', project_id=project.id))
        elif 'next' in request.form:
            return redirect(url_for('uo.uo_number', project_id=project.id))
        elif 'back' in request.form:
            return redirect(url_for('summary_offer.summary_offer', project_id=project.id))

    return render_template('nda_soc.html', form=form, project=project, record=record)
