from app import db

class SanctionLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), unique=True, nullable=False)
    project = db.relationship('Project', back_populates='sanction', uselist=False)
    start_date = db.Column(db.Date)
    project_cost = db.Column(db.Float)
    project_duration = db.Column(db.Integer)
    cars_project_no = db.Column(db.String(100))
    availability_of_funds = db.Column(db.String(100))
    uo_code = db.Column(db.String(100))
    usc_code = db.Column(db.String(100))
    sanction_pdf = db.Column(db.String(200))

    costs = db.relationship('SanctionCostEntry', backref='sanction_letter', cascade="all, delete-orphan")
    schedule_milestones = db.relationship('SanctionScheduleEntry', backref='sanction_letter', cascade="all, delete-orphan")
    cars_milestones = db.relationship('SanctionCARSEntry', backref='sanction_letter', cascade="all, delete-orphan")


class SanctionCostEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sanction_letter_id = db.Column(db.Integer, db.ForeignKey('sanction_letter.id'))
    category = db.Column(db.String(100))
    amount = db.Column(db.Float)


class SanctionScheduleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sanction_letter_id = db.Column(db.Integer, db.ForeignKey('sanction_letter.id'))
    milestone = db.Column(db.String(200))
    date = db.Column(db.Date)
    amount = db.Column(db.Float)


class SanctionCARSEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sanction_letter_id = db.Column(db.Integer, db.ForeignKey('sanction_letter.id'))
    milestone_description = db.Column(db.String(200))
    deliverables = db.Column(db.String(300))
    duration_months = db.Column(db.Integer)