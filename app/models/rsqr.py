from app import db

class RSQR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    requirements = db.Column(db.Text)
    justification = db.Column(db.Text)
    deliverables = db.Column(db.Text)
    pdf_filename = db.Column(db.String(255))  # <-- Add this line
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
