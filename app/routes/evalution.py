
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.dashboard import Project
from app.models.offer_evaluation import OfferEvaluation
from app.forms import OfferEvaluationForm

offer_bp = Blueprint('offer_bp', __name__)
UPLOAD_FOLDER = 'app/static/uploads'  # Make sure this path exists! Use absolute if needed.

@offer_bp.route('/offer-evaluation/<int:project_id>', methods=['GET', 'POST'])
@login_required
def offer_evaluation(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    form = OfferEvaluationForm()

    # Fetch existing or create new OfferEvaluation record
    offer_evaluation = OfferEvaluation.query.filter_by(project_id=project_id).first()
    if not offer_evaluation:
        offer_evaluation = OfferEvaluation(project_id=project_id)

    # Handle POST
    if request.method == 'POST' and form.validate_on_submit():
        # Handle PDF upload
        if form.evaluation_pdf.data:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(form.evaluation_pdf.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.evaluation_pdf.data.save(filepath)
            offer_evaluation.evaluation_pdf = filename

        # Save other fields
        offer_evaluation.offer_eval_date = form.offer_eval_date.data
        offer_evaluation.eval_chairperson = form.eval_chairperson.data
        offer_evaluation.eval_member = form.eval_member.data
        offer_evaluation.eval_user = form.eval_user.data
        offer_evaluation.meeting_location = form.meeting_location.data
        project.pi = request.form.get("pi_name", project.pi)
        project.institute = request.form.get("institute", project.institute)

        db.session.add(project)

        db.session.add(offer_evaluation)
        db.session.commit()

        # Redirects and flash
        if 'save' in request.form:
            flash('Offer Evaluation saved successfully!', 'success')
            return redirect(url_for('offer_bp.offer_evaluation', project_id=project.id))
        elif 'next' in request.form:
            return redirect(url_for('summary_offer.summary_offer', project_id=project.id))
        elif 'back' in request.form:
            return redirect(url_for('management_council.management_council', project_id=project.id))

    # Pre-fill template vars for display
    rsqr_title = project.rsqr.title if hasattr(project, 'rsqr') and project.rsqr else ''
    pi_name = project.pi
    institute = project.institute

    # Pre-fill form values if editing
    if offer_evaluation and request.method == 'GET':
        form.offer_eval_date.data = offer_evaluation.offer_eval_date
        form.eval_chairperson.data = offer_evaluation.eval_chairperson
        form.eval_member.data = offer_evaluation.eval_member
        form.eval_user.data = offer_evaluation.eval_user
        form.meeting_location.data = offer_evaluation.meeting_location

    return render_template(
        'evalution.html',
        form=form,
        project=project,
        rsqr_title=rsqr_title,
        pi_name=pi_name,
        institute=institute,
        offer_evaluation=offer_evaluation  # <--- pass record as offer_evaluation
    )
