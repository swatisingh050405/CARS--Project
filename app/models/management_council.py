from app import db

class ManagementCouncil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    council_date = db.Column(db.Date)
    venue = db.Column(db.String(100))  # Add this
    time = db.Column(db.String(50)) 
    chairperson = db.Column(db.String(100))
    title = db.Column(db.String(200))
    pdc = db.Column(db.String(100))
    cost = db.Column(db.Float)
    council_pdf = db.Column(db.String(200))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
