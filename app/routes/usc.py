# app/routes/unique_section_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Project, UniqueSanction
from app.forms import UniqueSanctionForm

unique_sanction_bp = Blueprint('unique_sanction', __name__)

@unique_sanction_bp.route('/unique-sanction/<int:project_id>', methods=['GET', 'POST'])
@login_required
def unique_sanction(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))

    sanction = UniqueSanction.query.filter_by(project_id=project.id).first()
    form = UniqueSanctionForm(obj=sanction)

    if form.validate_on_submit():
        if sanction:
            sanction.sanction_code = form.sanction_code.data
        else:
            sanction = UniqueSanction(
                project_id=project.id,
                sanction_code=form.sanction_code.data
            )
            db.session.add(sanction)

       
        db.session.commit()

        if 'save' in request.form:
            flash(' unique sanction Saved successfully!', 'success')
            return redirect(url_for('unique_sanction.unique_sanction', project_id=project.id))
        elif 'next' in request.form:
            return redirect(url_for('contract_bp.contract', project_id=project.id))
        elif 'back' in request.form:
            return redirect(url_for('uo.uo_number', project_id=project.id))

    return render_template('usc.html', form=form, project=project)
