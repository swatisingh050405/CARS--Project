from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app import db
from app.models import Project, SummaryOffer, CostEntry, MilestoneEntry
from app.forms import SummaryOfferForm

summary_offer_bp = Blueprint('summary_offer', __name__)

@summary_offer_bp.route('/summary-offer/<int:project_id>', methods=['GET', 'POST'])
@login_required
def summary_offer(project_id):
    # --- Access control ---
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash("Access denied", "danger")
        return redirect(url_for("dashboard.dashboard"))

    form = SummaryOfferForm()
    existing_offer = SummaryOffer.query.filter_by(project_id=project.id).first()

    # ---------- POST ----------
    if request.method == 'POST':
        if not existing_offer:
            summary_offer = SummaryOffer(project_id=project.id)
            db.session.add(summary_offer)
            db.session.commit()
        else:
            summary_offer = existing_offer
            # Clear old entries so we can replace fresh
            CostEntry.query.filter_by(summary_offer_id=summary_offer.id).delete()
            MilestoneEntry.query.filter_by(summary_offer_id=summary_offer.id).delete()

        db.session.flush()

        # COST entries - fixed
        total = 0
        fixed_costs = [
            ("Personal", request.form.get("cost_personal")),
            ("Equipment", request.form.get("cost_equipment")),
            ("Other", request.form.get("cost_other"))
        ]
        for category, amount_str in fixed_costs:
            if amount_str:
                try:
                    amount = float(amount_str)
                    total += amount
                    db.session.add(CostEntry(
                        summary_offer_id=summary_offer.id,
                        category=category,
                        amount=amount
                    ))
                except ValueError:
                    pass

        # COST entries - custom
        custom_heads = request.form.getlist("custom_cost_head[]")
        custom_amounts = request.form.getlist("custom_cost_amount[]")
        for head, amt_str in zip(custom_heads, custom_amounts):
            if head.strip() and amt_str:
                try:
                    amount = float(amt_str)
                    total += amount
                    db.session.add(CostEntry(
                        summary_offer_id=summary_offer.id,
                        category=head.strip(),
                        amount=amount
                    ))
                except ValueError:
                    pass

        # GST calculation and add as separate cost entry
        gst_amount = round(total * 0.18, 2)
        total_with_gst = round(total + gst_amount, 2)
        summary_offer.gst_amount = gst_amount
        summary_offer.total_amount = total_with_gst
        db.session.add(CostEntry(
            summary_offer_id=summary_offer.id,
            category="GST (18%)",
            amount=gst_amount
        ))

        # MILESTONES (fixed + dynamic all together)
        milestone_names = request.form.getlist('milestone_name[]')
        milestone_dates = request.form.getlist('milestone_date[]')
        milestone_amounts = request.form.getlist('milestone_amount[]')
        milestone_statuses = request.form.getlist('milestone_status[]')

        for name, date_str, amount_str, status in zip(milestone_names, milestone_dates, milestone_amounts, milestone_statuses):
            if name and date_str and amount_str:
                try:
                    due_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    amount = float(amount_str)
                    db.session.add(MilestoneEntry(
                        summary_offer_id=summary_offer.id,
                        milestone=name.strip(),
                        due_date=due_date,
                        amount=amount,
                        status=status,
                        notified=False
                    ))
                except ValueError:
                    pass

        # PDF upload
        file = form.summary_pdf.data
        if file and hasattr(file, 'filename') and file.filename:
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            summary_offer.pdf_filename = filename
        
        
        db.session.commit()

        # Redirect logic
        if 'save' in request.form:
            flash(' summary Saved successfully!', 'success')
            return redirect(url_for('summary_offer.summary_offer', project_id=project.id))
        elif 'next' in request.form:
            return redirect(url_for('nda_soc.nda_soc', project_id=project.id))
        elif 'back' in request.form:
            return redirect(url_for('offer_bp.offer_evaluation', project_id=project.id))

    # ---------- GET ----------
    overdue_milestones = []
    milestone_rows = []
    fixed_milestones = ['Initial Advance', 'Milestone 1', 'Milestone 2']

    if existing_offer:
        overdue_milestones = MilestoneEntry.query.filter(
            MilestoneEntry.summary_offer_id == existing_offer.id,
            MilestoneEntry.status == 'Pending',
            MilestoneEntry.due_date < datetime.today().date()
        ).all()

        # Build milestone lookup to prefill fixed ones
        milestone_lookup = {m.milestone: m for m in existing_offer.milestones}

        # Add fixed milestones in defined order
        for name in fixed_milestones:
            milestone_rows.append({
                "milestone": name,
                "due_date": milestone_lookup.get(name).due_date if name in milestone_lookup else None,
                "amount": milestone_lookup.get(name).amount if name in milestone_lookup else None,
                "status": milestone_lookup.get(name).status if name in milestone_lookup else "Pending"
            })

        # Append dynamic (non-fixed) milestones
        for m in existing_offer.milestones:
            if m.milestone not in fixed_milestones:
                milestone_rows.append({
                    "milestone": m.milestone,
                    "due_date": m.due_date,
                    "amount": m.amount,
                    "status": m.status
                })
    else:
        # New form — only fixed milestones with blank values
        for name in fixed_milestones:
            milestone_rows.append({
                "milestone": name,
                "due_date": None,
                "amount": None,
                "status": "Pending"
            })

    return render_template(
        "summary.html",
        form=form,
        project=project,
        existing_offer=existing_offer,
        overdue_milestones=overdue_milestones,
        milestone_rows=milestone_rows
    )
