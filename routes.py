from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from extensions import db, login_manager
from models import User, Habit, DailyLog, Achievement
from services.plaid_service import PlaidService

plaid_service = PlaidService()

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

        # Check for achievements
        streak_achievements = {
            7: ("Week Warrior", "7-day streak"),
            30: ("Monthly Master", "30-day streak"),
            100: ("Century Champion", "100-day streak"),
            365: ("Year Legend", "365-day streak")
        }

        for streak, (name, desc) in streak_achievements.items():
            if habit.completion_streak == streak:
                achievement = Achievement(
                    user_id=current_user.id,
                    habit_id=habit.id,
                    name=name,
                    description=desc,
                    badge_type=f"streak_{streak}"
                )
                db.session.add(achievement)
                flash(f'🎉 Achievement Unlocked: {name}!')

        db.session.commit()
        flash('Check-in recorded successfully!')
    else:
        flash('Already checked in today!')

    return redirect(url_for('dashboard'))


@app.route('/link-account')
@login_required
def link_account():
    """Initialize Plaid Link for bank account connection"""
    link_token = plaid_service.create_link_token(current_user.id)
    if not link_token:
        flash('Error creating link token')
        return redirect(url_for('dashboard'))
    return render_template('link_account.html', link_token=link_token)

@app.route('/set-access-token', methods=['POST'])
@login_required
def set_access_token():
    """Handle Plaid OAuth callback and set access token"""
    public_token = request.json.get('public_token')
    account_id = request.json.get('account_id')

    if not public_token or not account_id:
        return jsonify({'error': 'Missing required fields'}), 400

    access_token = plaid_service.exchange_public_token(public_token)
    if not access_token:
        return jsonify({'error': 'Failed to exchange token'}), 400

    current_user.plaid_access_token = access_token
    current_user.account_id = account_id
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/achievements')
@login_required
def achievements():
    achievements = Achievement.query.filter_by(user_id=current_user.id).order_by(Achievement.achieved_at.desc()).all()
    return render_template('achievements.html', achievements=achievements)

@app.route('/share/linkedin/<int:achievement_id>')
@login_required
def share_to_linkedin(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)

    if achievement.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('achievements'))

    # Generate LinkedIn share URL with achievement details
    title = f"I've achieved {achievement.name} on HabitBuilder!"
    summary = f"I maintained a {achievement.description} with HabitBuilder's financial accountability system."
    url = url_for('achievements', _external=True)

    linkedin_url = (
        "https://www.linkedin.com/sharing/share-offsite/?"
        f"url={url}&"
        f"title={title}&"
        f"summary={summary}"
    )

    achievement.shared = True
    db.session.commit()

    return redirect(linkedin_url)

@app.route('/leaderboard')
def leaderboard():
    # Get users with their total streak days and achievement counts
    leaderboard_data = db.session.query(
        User,
        db.func.sum(Habit.completion_streak).label('total_streaks'),
        db.func.count(Achievement.id).label('achievement_count')
    ).join(Habit, User.id == Habit.user_id)\
     .outerjoin(Achievement, User.id == Achievement.user_id)\
     .group_by(User.id)\
     .order_by(db.desc('total_streaks'), db.desc('achievement_count'))\
     .all()

    # Format data for template
    rankings = []
    for idx, (user, total_streaks, achievement_count) in enumerate(leaderboard_data, 1):
        rankings.append({
            'rank': idx,
            'email': user.email,
            'total_streaks': total_streaks or 0,
            'achievement_count': achievement_count or 0
        })

    return render_template('leaderboard.html', rankings=rankings)