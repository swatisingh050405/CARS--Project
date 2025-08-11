from app import db

class UONumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    uo_number = db.Column(db.String(100))
    personal = db.Column(db.Numeric(10, 2))
    equipment = db.Column(db.Numeric(10, 2))
    travel = db.Column(db.Numeric(10, 2))
    contingencies = db.Column(db.Numeric(10, 2))
    visiting_faculty = db.Column(db.Numeric(10, 2))
    technical_support = db.Column(db.Numeric(10, 2))
    ipr_fees = db.Column(db.Numeric(10, 2))
    overheads = db.Column(db.Numeric(10, 2))
    total_amount = db.Column(db.Numeric(10, 2))
    gst = db.Column(db.Numeric(10, 2), nullable=True)  # GST field, optional

    dynamic_entries = db.relationship('UODynamicEntry', backref='uo', cascade='all, delete-orphan')

class UODynamicEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uo_id = db.Column(db.Integer, db.ForeignKey('uo_number.id'), nullable=False)
    category = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2))
