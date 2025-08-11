from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from datetime import datetime
from app import db
from app.models import MilestoneEntry

def check_and_alert_missed_milestones():
    with current_app.app_context():
        today = datetime.today().date()
        milestones = MilestoneEntry.query.filter(
            MilestoneEntry.due_date < today,
            MilestoneEntry.status == 'Pending',
        ).all()
        # For now, you can log or flag—but DO NOT email
        for ms in milestones:
            print(f"[REMINDER] {ms.milestone} overdue (due {ms.due_date})")
        # (ms.notified = True) only if you want to track, not needed for UI message
        db.session.commit()
