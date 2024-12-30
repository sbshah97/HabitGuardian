from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from extensions import db, login_manager
from models import User, Habit, DailyLog

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            plaid_access_token="sandbox_test",
            account_id="test_account"
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', habits=habits, today=datetime.utcnow().date())

@app.route('/habit/create', methods=['GET', 'POST'])
@login_required
def create_habit():
    if request.method == 'POST':
        name = request.form.get('name')
        stake_amount = float(request.form.get('stake_amount'))

        habit = Habit(
            name=name,
            stake_amount=stake_amount,
            user_id=current_user.id
        )
        db.session.add(habit)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_habit.html')

@app.route('/habit/<int:habit_id>/check_in', methods=['POST'])
@login_required
def check_in(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id != current_user.id:
        return redirect(url_for('dashboard'))

    today = datetime.utcnow().date()
    log = DailyLog.query.filter_by(
        habit_id=habit_id,
        date=today
    ).first()

    if not log:
        log = DailyLog(
            habit_id=habit_id,
            date=today,
            completed=True
        )
        db.session.add(log)
        habit.completion_streak += 1
        habit.last_check_in = datetime.utcnow()
        db.session.commit()
        flash('Check-in recorded successfully!')
    else:
        flash('Already checked in today!')

    return redirect(url_for('dashboard'))