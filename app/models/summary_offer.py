from app import db
from sqlalchemy import Numeric, Date

class SummaryOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(Numeric(12, 2))
    gst_amount = db.Column(Numeric(12, 2))
    pdf_filename = db.Column(db.String(255))  # for uploaded summary PDF
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    milestones = db.relationship('MilestoneEntry', backref='summary_offer', cascade='all, delete-orphan')
    cost_entries = db.relationship('CostEntry', backref='summary_offer', cascade='all, delete-orphan')


class CostEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))  # Custom or default e.g., 'Personnel', 'Custom Field X'
    amount = db.Column(Numeric(10, 2))
    summary_offer_id = db.Column(db.Integer, db.ForeignKey('summary_offer.id'), nullable=False)


class MilestoneEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summary_offer_id = db.Column(db.Integer, db.ForeignKey('summary_offer.id'), nullable=False)
    milestone = db.Column(db.String(255), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    amount = db.Column(db.Float, nullable=True)  # ✅ Add this line if missing
    status = db.Column(db.String(50), default='Pending')
    notified = db.Column(db.Boolean, default=False)