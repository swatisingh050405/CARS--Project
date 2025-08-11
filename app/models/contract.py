from app import db
from datetime import datetime

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    contract_number = db.Column(db.String(20))
    date = db.Column(db.Date)
    contract_pdf = db.Column(db.String(200))
    
    project = db.relationship('Project', back_populates='contract')
    cost_entries = db.relationship('ContractCostEntry', backref='contract', cascade='all, delete-orphan')
    milestones = db.relationship('ContractMilestone', backref='contract', cascade='all, delete-orphan')


class ContractCostEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    category = db.Column(db.String(100))
    amount = db.Column(db.Float)


class ContractMilestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'), nullable=False)
    description = db.Column(db.String(100))  # For fixed: Initial, Milestone I/II, Final
    amount = db.Column(db.Float)
    due_date = db.Column(db.Date)
    
