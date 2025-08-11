from app import db
from datetime import datetime
from sqlalchemy import event

# ✅ Import the actual mapped classes
from app.models.rsqr import RSQR
from app.models.offer_evaluation import OfferEvaluation
from app.models.summary_offer import SummaryOffer
from app.models.management_council import ManagementCouncil
from app.models.amendment import AmendmentLetter


class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    pi = db.Column(db.String(100), nullable=True)
    institute = db.Column(db.String(200), nullable=True)
    reference_no = db.Column(db.String(50))
    status = db.Column(db.String(50), default='INITIAL STAGE')
    created_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # ========== Relationships (all cascade delete) ==========
    rsqr = db.relationship('RSQR', uselist=False, backref='project', cascade="all, delete-orphan")
    management_council = db.relationship('ManagementCouncil', uselist=False, backref='project', cascade="all, delete-orphan")
    offer_evaluation = db.relationship('OfferEvaluation', uselist=False, backref='project', cascade="all, delete-orphan")
    summary_offer = db.relationship('SummaryOffer', uselist=False, backref='project', cascade="all, delete-orphan")
    nda_soc = db.relationship('NDASOC', back_populates='project', uselist=False, cascade="all, delete-orphan")
    uo_number = db.relationship('UONumber', backref='project', uselist=False, cascade="all, delete-orphan")
    unique_sanction = db.relationship('UniqueSanction', back_populates='project', uselist=False, cascade="all, delete-orphan")
    contract = db.relationship('Contract', back_populates='project', uselist=False, cascade="all, delete-orphan")
    sanction = db.relationship('SanctionLetter', back_populates='project', uselist=False, cascade="all, delete-orphan")
    amendment = db.relationship('AmendmentLetter', back_populates='project', uselist=False, cascade="all, delete-orphan")

    # ===== Status calculation =====
    def compute_project_status(self):
        steps_complete = all([
            self.rsqr is not None,
            self.offer_evaluation is not None,
            self.summary_offer is not None,
            self.management_council is not None
        ])

        # ✅ Amendment considered done if amendment_no OR amendment_pdf present
        amendment_present = (
            self.amendment is not None and (
                (self.amendment.amendment_no and str(self.amendment.amendment_no).strip() != "")
                or (self.amendment.amendment_pdf and self.amendment.amendment_pdf.strip())
            )
        )

        if steps_complete and amendment_present:
            return "COMPLETE"
        elif steps_complete:
            return "ACTIVE"
        return "INITIAL STAGE"

    def update_status(self):
        self.status = self.compute_project_status()


# ===== Automatic status update events =====
def _auto_update_status(mapper, connection, target):
    session = db.object_session(target)
    if target.project:
        with session.no_autoflush:  # avoid flush recursion issue
            target.project.update_status()

# ✅ Register events for main step models
for model in (RSQR, OfferEvaluation, SummaryOffer, ManagementCouncil, AmendmentLetter):
    event.listen(model, 'after_insert', _auto_update_status)
    event.listen(model, 'after_update', _auto_update_status)
    event.listen(model, 'after_delete', _auto_update_status)
