from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.models import Project, AmendmentLetter, RevisedExpenditure, SchedulePayment
from app.forms import AmendmentLetterForm

amendment_bp = Blueprint('amendment', __name__)

@amendment_bp.route('/amendment/<int:project_id>', methods=['GET', 'POST'])
@login_required
def amendment_letter(project_id):
    project = Project.query.get_or_404(project_id)
    amendment = AmendmentLetter.query.filter_by(project_id=project.id).first()

    fixed_exp = ['Personal', 'Equipment']
    fixed_sop = ['Initial Advance', 'Milestone 1']

    form = AmendmentLetterForm(obj=amendment)
    form.pi.data = project.pi
    form.institute.data = project.institute
    form.project_duration.data = project.sanction.project_duration if project.sanction else None

    fixed_exp_amounts = {h: "" for h in fixed_exp}
    dynamic_exp = []
    fixed_sop_rows = [{"milestone": m, "due_date": "", "amount": ""} for m in fixed_sop]
    dynamic_sop_rows = []

    if amendment:
        for e in amendment.revised_expenditures:
            if e.head in fixed_exp:
                fixed_exp_amounts[e.head] = e.amount
            else:
                dynamic_exp.append({"head": e.head, "amount": e.amount})

        for row in fixed_sop:
            existing = next((s for s in amendment.schedule_payments if s.milestone == row), None)
            if existing:
                idx = fixed_sop.index(row)
                fixed_sop_rows[idx] = {
                    "milestone": existing.milestone,
                    "due_date": existing.due_date.strftime("%Y-%m-%d") if existing.due_date else "",
                    "amount": existing.amount
                }

        for s in amendment.schedule_payments:
            if s.milestone not in fixed_sop:
                dynamic_sop_rows.append({
                    "milestone": s.milestone,
                    "due_date": s.due_date.strftime("%Y-%m-%d") if s.due_date else "",
                    "amount": s.amount
                })

    if request.method == 'POST' and form.validate_on_submit():
        if not amendment:
            amendment = AmendmentLetter(project_id=project.id)
            db.session.add(amendment)

        amendment.amendment_no = form.amendment_no.data
        amendment.amendment_date = form.amendment_date.data
        amendment.pi = form.pi.data
        amendment.co_pi = form.co_pi.data
        amendment.institute = form.institute.data
        amendment.project_duration = form.project_duration.data

        # Save PDF if uploaded
        file = form.amendment_pdf.data
        if file and hasattr(file, 'filename') and file.filename:
            upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_dir, exist_ok=True)
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_dir, filename))
            amendment.amendment_pdf = filename

        # Clear child data
        RevisedExpenditure.query.filter_by(amendment_id=amendment.id).delete()
        SchedulePayment.query.filter_by(amendment_id=amendment.id).delete()
        db.session.flush()

        # Save fixed expenditures
        for head in fixed_exp:
            amt = request.form.get(f'fixed_revised_{head.lower()}')
            if amt:
                db.session.add(RevisedExpenditure(head=head, amount=float(amt), amendment_id=amendment.id))

        # Save dynamic expenditures
        dyn_heads = request.form.getlist('dynamic_revised_head[]')
        dyn_amounts = request.form.getlist('dynamic_revised_amount[]')
        for h, a in zip(dyn_heads, dyn_amounts):
            if h and a:
                db.session.add(RevisedExpenditure(head=h, amount=float(a), amendment_id=amendment.id))

        # Save fixed SOP
        fixed_due_list = request.form.getlist('fixed_due_date')
        fixed_amt_list = request.form.getlist('fixed_amount')
        for m, d, a in zip(fixed_sop, fixed_due_list, fixed_amt_list):
            if d and a:
                db.session.add(SchedulePayment(
                    milestone=m,
                    due_date=datetime.strptime(d, "%Y-%m-%d").date(),
                    amount=float(a),
                    amendment_id=amendment.id
                ))

        # Save dynamic SOP
        sop_m = request.form.getlist('dynamic_sop_milestone[]')
        sop_d = request.form.getlist('dynamic_sop_due[]')
        sop_a = request.form.getlist('dynamic_sop_amount[]')
        for m, d, a in zip(sop_m, sop_d, sop_a):
            if m and d and a:
                db.session.add(SchedulePayment(
                    milestone=m,
                    due_date=datetime.strptime(d, "%Y-%m-%d").date(),
                    amount=float(a),
                    amendment_id=amendment.id
                ))

        # ✅ Force status update before commit
        project.update_status()
        db.session.commit()

        # Redirect logic
        if 'save' in request.form:
            flash('Amendment saved successfully!', 'success')
            return redirect(url_for('amendment.amendment_letter', project_id=project.id))
        elif 'next' in request.form:
            return redirect(url_for('completion.completion', project_id=project.id))
        elif 'back' in request.form:
            return redirect(url_for('sanction.sanction_letter', project_id=project.id))

    return render_template(
        'amendment.html',
        form=form,
        project=project,
        amendment=amendment,
        fixed_exp_amounts=fixed_exp_amounts,
        dynamic_exp=dynamic_exp,
        fixed_sop_rows=fixed_sop_rows,
        dynamic_sop_rows=dynamic_sop_rows
    )
