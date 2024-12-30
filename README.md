
# HabitBuilder - Habit Formation with Financial Incentives

A Flask web application that helps users build habits by putting financial stakes on their commitments. The app uses the Plaid API to handle financial transactions and provides achievement-based gamification.

## Features

- User authentication (login/register)
- Create and track habits with financial stakes
- Daily check-ins and streak tracking
- Achievement system with badges
- Financial accountability via Plaid integration
- Leaderboard for community engagement
- LinkedIn sharing for achievements

## Setup

1. Configure environment variables:
```bash
FLASK_SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://localhost/habits
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

The app will be available at `http://0.0.0.0:5000`

## Database Models

- User: Handles authentication and Plaid account linking
- Habit: Tracks habit details, stakes, and progress
- DailyLog: Records daily check-ins
- Achievement: Stores user achievements and badges

## API Integration

The app uses Plaid API for:
- Linking bank accounts
- Processing stake amounts
- Managing financial transactions

## Routes

- `/`: Landing page
- `/login` & `/register`: Authentication
- `/dashboard`: Main habit tracking interface
- `/habit/create`: Create new habits
- `/achievements`: View and share achievements
- `/leaderboard`: Community rankings
- `/api-docs`: API documentation

## Stack

- Flask: Web framework
- SQLAlchemy: Database ORM
- Flask-Login: User session management
- Plaid: Financial integration
- PostgreSQL: Database
