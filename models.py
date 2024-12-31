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
    total_forfeited_stakes = db.Column(db.Float, default=0.0)

class HabitCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))
    habits = db.relationship('Habit', backref='category', lazy=True)

    @staticmethod
    def get_default_categories():
        return [
            {'name': 'Health', 'description': 'Health and wellness related habits'},
            {'name': 'Physical Sports', 'description': 'Sports and physical activities'},
            {'name': 'Entertainment', 'description': 'Entertainment and leisure activities'},
            {'name': 'Education', 'description': 'Learning and skill development'},
            {'name': 'Productivity', 'description': 'Work and productivity improvement'}
        ]

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('habit_category.id'))
    name = db.Column(db.String(100), nullable=False)
    stake_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    completion_streak = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    last_check_in = db.Column(db.DateTime)
    donation_status = db.Column(db.String(20), default='pending')  # pending, donated, refunded
    reminder_time = db.Column(db.Time, nullable=True)  # Time for daily reminder
    habit_icon = db.Column(db.String(100), nullable=False, default='bi-check-circle')
    duration_days = db.Column(db.Integer, nullable=False, default=21)
    forfeited_stake = db.Column(db.Float, default=0.0)
    last_reminder_sent = db.Column(db.DateTime)  # Track when the last reminder was sent

    def __init__(self, **kwargs):
        if 'start_date' not in kwargs:
            kwargs['start_date'] = datetime.utcnow()
        if 'duration_days' in kwargs:
            kwargs['duration_days'] = min(kwargs['duration_days'], 21)
        super(Habit, self).__init__(**kwargs)
        if not self.end_date:
            self.end_date = kwargs['start_date'] + timedelta(days=kwargs.get('duration_days', 21))

    @staticmethod
    def get_preset_habits():
        return [
            {
                'name': 'Drink Water',
                'icon': 'bi-droplet-fill',
                'default_reminder': '09:00',
                'description': 'Stay hydrated throughout the day',
                'category': 'Health'
            },
            {
                'name': 'Breakfast',
                'icon': 'bi-egg-fried',
                'default_reminder': '08:00',
                'description': 'Start your day with a healthy breakfast',
                'category': 'Health'
            },
            {
                'name': 'Workout',
                'icon': 'bi-bicycle',
                'default_reminder': '17:00',
                'description': 'Stay fit with daily exercise',
                'category': 'Physical Sports'
            },
            {
                'name': 'Movie Night',
                'icon': 'bi-film',
                'default_reminder': '20:00',
                'description': 'Relax and enjoy a movie',
                'category': 'Entertainment'
            },
            {
                'name': 'Journal',
                'icon': 'bi-journal-text',
                'default_reminder': '22:00',
                'description': 'Reflect on your day',
                'category': 'Productivity'
            }
        ]

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