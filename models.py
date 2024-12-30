from datetime import datetime, timedelta
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    plaid_access_token = db.Column(db.String(100))
    account_id = db.Column(db.String(100))
    habits = db.relationship('Habit', backref='user', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    stake_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    completion_streak = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    last_check_in = db.Column(db.DateTime)
    donation_status = db.Column(db.String(20), default='pending')  # pending, donated, refunded

    def __init__(self, **kwargs):
        super(Habit, self).__init__(**kwargs)
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=21)

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    badge_type = db.Column(db.String(50), nullable=False)  # e.g., 'streak_7', 'streak_30'
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)
    shared = db.Column(db.Boolean, default=False)
    habit = db.relationship('Habit', backref='achievements')