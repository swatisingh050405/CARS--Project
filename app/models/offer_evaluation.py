from app import db

class OfferEvaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evaluation_pdf = db.Column(db.String(200))
    offer_eval_date = db.Column(db.Date)
    meeting_location = db.Column(db.String(200))
    eval_chairperson = db.Column(db.String(100))
    eval_member = db.Column(db.String(100))
    eval_user = db.Column(db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
