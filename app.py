import os
import logging
from datetime import datetime
from flask import Flask
from extensions import db, login_manager
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.DEBUG)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_key_123")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://localhost/habits")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize Flask extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models and routes after db initialization
from models import User, Habit
from routes import *

with app.app_context():
    db.create_all()

    # Create demo user if not exists
    if not User.query.filter_by(email="demo@example.com").first():
        demo_user = User(
            email="demo@example.com",
            password_hash=generate_password_hash("demo123"),
            plaid_access_token="sandbox_test",
            account_id="test_account"
        )
        db.session.add(demo_user)
        db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)