from app import db

class NDASOC(db.Model):
    __tablename__ = 'nda_soc'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, unique=True)

    nda_pdf = db.Column(db.String(255))   # stores filename of uploaded NDA
    soc_pdf = db.Column(db.String(255))   # stores filename of uploaded SOC

    # Relationship back to project (if needed in future)
    project = db.relationship('Project', back_populates='nda_soc')
