from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Project, UONumber, UODynamicEntry
from app.forms import UONumberForm

uo_bp = Blueprint('uo', __name__, url_prefix='/uo')

@uo_bp.route('/uo_number/<int:project_id>', methods=['GET', 'POST'])
@login_required
def uo_number(project_id):
    project = Project.query.get_or_404(project_id)
    form = UONumberForm()

    uo = UONumber.query.filter_by(project_id=project.id).first()
    if not uo:
        uo = UONumber(project_id=project.id)
        db.session.add(uo)
        db.session.commit()

    if form.validate_on_submit():
        uo.uo_number = form.uo_number.data
        uo.personal = form.personal.data or 0
        uo.equipment = form.equipment.data or 0
        uo.travel = form.travel.data or 0
        uo.contingencies = form.contingencies.data or 0
        uo.visiting_faculty = form.visiting_faculty.data or 0
        uo.technical_support = form.technical_support.data or 0
        uo.ipr_fees = form.ipr_fees.data or 0
        uo.overheads = form.overheads.data or 0
        uo.gst = form.gst.data or 0
        uo.total_amount = form.total_amount.data or 0

        # Clear existing dynamic entries
        uo.dynamic_entries.clear()

        # Read dynamic entries from posted form inputs
        categories = request.form.getlist("dynamic_category")
        amounts = request.form.getlist("dynamic_amount")
        for cat, amt in zip(categories, amounts):
            cat = (cat or "").strip()
            if cat:
                try:
                    amt_val = float(amt)
                except (TypeError, ValueError):
                    amt_val = 0
                uo.dynamic_entries.append(UODynamicEntry(category=cat, amount=amt_val))

        db.session.commit()

        if 'save' in request.form:
            flash(' uo number Saved successfully!', 'success')
            return redirect(url_for('uo.uo_number', project_id=project.id))
        elif 'next' in request.form:
            return redirect(url_for('unique_sanction.unique_sanction', project_id=project.id))
        elif 'back' in request.form:
            return redirect(url_for('nda_soc.nda_soc', project_id=project.id))

    else:
        form.uo_number.data = uo.uo_number
        form.personal.data = uo.personal
        form.equipment.data = uo.equipment
        form.travel.data = uo.travel
        form.contingencies.data = uo.contingencies
        form.visiting_faculty.data = uo.visiting_faculty
        form.technical_support.data = uo.technical_support
        form.ipr_fees.data = uo.ipr_fees
        form.overheads.data = uo.overheads
        form.gst.data = uo.gst
        form.total_amount.data = uo.total_amount

        dynamic_entries = list(uo.dynamic_entries)

    return render_template('uo_no.html', form=form, project=project, dynamic_entries=dynamic_entries)
