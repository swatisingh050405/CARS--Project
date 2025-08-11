from flask import current_app, render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.config import Config
from app.models import Project, SanctionLetter, SanctionCostEntry, SanctionScheduleEntry, SanctionCARSEntry
from app.forms import SanctionLetterForm

sanction_bp = Blueprint('sanction', __name__)

@sanction_bp.route('/sanction/<int:project_id>/sanction', methods=['GET', 'POST'])
@login_required
def sanction_letter(project_id):
    project = Project.query.get_or_404(project_id)
    sanction = SanctionLetter.query.filter_by(project_id=project_id).first()
    form = SanctionLetterForm(obj=sanction)

    # -- Constant rows for table --
    fixed_schedule = [
        'Initial Advance', 'Milestone I', 'Milestone II', 'Final Support'
    ]
    fixed_cars = ['Milestone A', 'Milestone B', 'Milestone C']

    # --- Prepare table data for GET ---
    sanction_costs = {}
    sanction_schedule = []
    sanction_cars = []

    if sanction:
        # Cost table
        for ce in sanction.costs:
            sanction_costs[ce.category] = ce.amount

        # Schedule of Payments table: load milestone name + date + amount
        entries = SanctionScheduleEntry.query.filter_by(sanction_letter_id=sanction.id).all()
        if entries:
            for sch in entries:
                sanction_schedule.append({
                    'milestone': sch.milestone or "",
                    'date': sch.date.strftime("%Y-%m-%d") if sch.date else "",
                    'amount': sch.amount
                })
        else:
            # Always show fixed rows if nothing saved
            for milestone in fixed_schedule:
                sanction_schedule.append({'milestone': milestone, 'date': "", 'amount': ""})

        # CARS table
        for cars in sanction.cars_milestones:
            sanction_cars.append({
                'description': cars.milestone_description,
                'deliverables': cars.deliverables,
                'duration_months': cars.duration_months
            })
        if not sanction_cars:
            for desc in fixed_cars:
                sanction_cars.append({'description': desc, 'deliverables': "", 'duration_months': ""})

    # --- POST handling ---
    if request.method == 'POST':
        if form.validate_on_submit():
            if not sanction:
                sanction = SanctionLetter(project_id=project_id)
                db.session.add(sanction)

            # Main WTForms fields
            sanction.start_date = form.start_date.data
            sanction.project_cost = form.project_cost.data
            sanction.project_duration = form.project_duration.data
            sanction.cars_project_no = form.cars_project_no.data
            sanction.availability_of_funds = form.availability_of_funds.data
            sanction.uo_code = form.uo_code.data
            sanction.usc_code = form.usc_code.data
            sanction.contract_number = form.contract_number.data

            # PDF upload section
            file = form.sanction_pdf.data
            if file and hasattr(file, 'filename') and file.filename:
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                filename = secure_filename(file.filename)
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                sanction.sanction_pdf = filename

            # Clear old entries for reliable update
            SanctionCostEntry.query.filter_by(sanction_letter_id=sanction.id).delete()
            SanctionScheduleEntry.query.filter_by(sanction_letter_id=sanction.id).delete()
            SanctionCARSEntry.query.filter_by(sanction_letter_id=sanction.id).delete()
            db.session.flush()

            # Cost table
            cost_categories = request.form.getlist('cost_category[]')
            cost_amounts = request.form.getlist('cost_amount[]')
            for cat, amt in zip(cost_categories, cost_amounts):
                if cat.strip() and amt:
                    db.session.add(SanctionCostEntry(
                        sanction_letter_id=sanction.id,
                        category=cat.strip(), amount=float(amt)
                    ))

            # Schedule of Payments table (milestone included)
            schedule_milestones = request.form.getlist('schedule_milestone[]')
            schedule_dates = request.form.getlist('schedule_date[]')
            schedule_amounts = request.form.getlist('schedule_amount[]')
            for milestone, date_str, amt in zip(schedule_milestones, schedule_dates, schedule_amounts):
                if milestone.strip() and (date_str or amt):
                    try:
                        pay_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
                    except ValueError:
                        pay_date = None
                    db.session.add(SanctionScheduleEntry(
                        sanction_letter_id=sanction.id,
                        milestone=milestone.strip(),    # <-- Store the name!
                        date=pay_date,
                        amount=float(amt) if amt else None
                    ))

            # CARS table
            cars_desc = request.form.getlist('cars_milestone[]')
            cars_deliv = request.form.getlist('cars_deliverable[]')
            cars_duration = request.form.getlist('cars_duration[]')
            for desc, deliv, duration in zip(cars_desc, cars_deliv, cars_duration):
                if desc and deliv and duration:
                    db.session.add(SanctionCARSEntry(
                        sanction_letter_id=sanction.id,
                        milestone_description=desc.strip(),
                        deliverables=deliv.strip(),
                        duration_months=int(duration)
                    ))

            db.session.commit()

            # Button handler
            if 'save' in request.form:
                flash(' sanction Saved successfully!', 'success')
                return redirect(url_for('sanction.sanction_letter', project_id=project.id))
            elif 'next' in request.form:
                return redirect(url_for('amendment.amendment_letter', project_id=project.id))
            elif 'back' in request.form:
                return redirect(url_for('contract_bp.contract', project_id=project.id))

        else:
            flash('Please fix errors.', 'danger')

    return render_template(
        'sanction.html',
        form=form,
        project=project,
        sanction=sanction,
        sanction_costs=sanction_costs,
        sanction_schedule=sanction_schedule,
        sanction_cars=sanction_cars
    )
