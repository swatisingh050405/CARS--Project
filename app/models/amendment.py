from app import db
from datetime import date

class AmendmentLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', back_populates='amendment')

    amendment_no = db.Column(db.String(100))
    amendment_date = db.Column(db.Date)
    pi = db.Column(db.String(150))
    co_pi = db.Column(db.String(150), nullable=True)
    institute = db.Column(db.String(200))
    project_duration = db.Column(db.Integer)

    amendment_pdf = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=date.today)

    revised_expenditures = db.relationship('RevisedExpenditure', backref='amendment', cascade="all, delete-orphan")
    schedule_payments = db.relationship('SchedulePayment', backref='amendment', cascade="all, delete-orphan")

   

class RevisedExpenditure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    head = db.Column(db.String(200))
    amount = db.Column(db.Float)
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment_letter.id'))

class SchedulePayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    milestone = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    amount = db.Column(db.Float)
    amendment_id = db.Column(db.Integer, db.ForeignKey('amendment_letter.id'))
