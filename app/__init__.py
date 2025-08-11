from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
scheduler = BackgroundScheduler()


def get_gravatar_url(email, size=30):
    """Return the gravatar URL for the given email."""
    email_clean = email.strip().lower()
    hash_email = hashlib.md5(email_clean.encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_email}?s={size}&d=identicon"


def create_app():
    app = Flask(__name__)

    from app.config import Config
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.signup'

    scheduler.start()

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ✅ Context processor to inject user_avatar_url into all templates
    @app.context_processor
    def inject_user_avatar():
        if current_user.is_authenticated and getattr(current_user, 'email', None):
            avatar_url = get_gravatar_url(current_user.email)
        else:
            avatar_url = url_for('static', filename='img/default_avatar.png')
        return dict(user_avatar_url=avatar_url)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.rsqr import rsqr_bp
    from app.routes.council import management_council_bp
    from app.routes.evalution import offer_bp
    from app.routes.summary import summary_offer_bp
    from app.routes.nda_soc import nda_soc_bp
    from app.routes.uo_no import uo_bp
    from app.routes.usc import unique_sanction_bp
    from app.routes.contract import contract_bp
    from app.routes.sanction import sanction_bp
    from app.routes.amendment import amendment_bp
    from app.routes.completion import completion_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(rsqr_bp)
    app.register_blueprint(management_council_bp)
    app.register_blueprint(offer_bp)
    app.register_blueprint(summary_offer_bp)
    app.register_blueprint(nda_soc_bp)
    app.register_blueprint(uo_bp)
    app.register_blueprint(unique_sanction_bp)
    app.register_blueprint(contract_bp)
    app.register_blueprint(sanction_bp)
    app.register_blueprint(amendment_bp)
    app.register_blueprint(completion_bp)

    with app.app_context():
        db.create_all()

    return app
