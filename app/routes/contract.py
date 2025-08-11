from flask import render_template, request, redirect, url_for, flash,Blueprint
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.config import Config
from app.models import Project, Contract, ContractCostEntry, ContractMilestone
from app.forms import ContractForm

contract_bp = Blueprint('contract_bp', __name__)

@contract_bp.route('/contract/<int:project_id>', methods=['GET', 'POST'])
@login_required
def contract(project_id):
    project = Project.query.get_or_404(project_id)
    contract = Contract.query.filter_by(project_id=project.id).first()

    if not contract:
        contract = Contract(project_id=project.id)
        db.session.add(contract)
        db.session.commit()

    form = ContractForm(obj=contract)

    # Prepare data for GET rendering
    contract_costs = {}
    contract_milestones = []
    if contract.cost_entries:
        for ce in contract.cost_entries:
            contract_costs[ce.category] = float(ce.amount)
    if contract.milestones:
        for ms in contract.milestones:
            contract_milestones.append({
                "description": ms.description,
                "due_date": ms.due_date.strftime("%Y-%m-%d") if ms.due_date else "",
                "amount": ms.amount
            })

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('unique_sanction.unique_sanction', project_id=project.id))
        if form.validate_on_submit():
            contract.contract_number = form.contract_number.data
            contract.date = form.date.data

            file = form.contract_pdf.data
            if file and hasattr(file, 'filename') and file.filename:
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                filename = secure_filename(file.filename)
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                contract.contract_pdf = filename

            # Delete old cost and milestone entries
            ContractCostEntry.query.filter_by(contract_id=contract.id).delete()
            ContractMilestone.query.filter_by(contract_id=contract.id).delete()
            db.session.flush()

            # Parse cost entries
            cost_categories = request.form.getlist('cost_category[]')
            cost_amounts = request.form.getlist('cost_amount[]')
            for cat, amt in zip(cost_categories, cost_amounts):
                if cat.strip() and amt:
                    db.session.add(ContractCostEntry(
                        contract_id=contract.id,
                        category=cat.strip(),
                        amount=float(amt)
                    ))

            # Parse milestones
            milestone_names = request.form.getlist('milestone_name[]')
            milestone_dates = request.form.getlist('milestone_date[]')
            milestone_amounts = request.form.getlist('milestone_amount[]')
            for name, date_str, amt in zip(milestone_names, milestone_dates, milestone_amounts):
                if name and date_str and amt:
                    try:
                        due_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        due_date = None
                    db.session.add(ContractMilestone(
                        contract_id=contract.id,
                        description=name.strip(),
                        amount=float(amt),
                        due_date=due_date
                    ))

            db.session.commit()
            

            if 'save' in request.form:
                flash(' contract Saved successfully!', 'success')
                return redirect(url_for('contract_bp.contract', project_id=project.id))
            elif 'next' in request.form:
                return redirect(url_for('sanction.sanction_letter', project_id=project.id))
            elif 'back' in request.form:
                return redirect(url_for('unique_sanction.unique_sanction', project_id=project.id))

        else:
            flash('Please fix errors.', 'danger')

    return render_template(
        'contract.html',
        form=form,
        project=project,
        contract=contract,
        contract_costs=contract_costs,
        contract_milestones=contract_milestones
    )
