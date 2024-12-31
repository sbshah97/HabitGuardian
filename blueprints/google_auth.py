import os
import json
import requests
from flask import Blueprint, redirect, request, url_for, current_app
from flask_login import login_user
from authlib.integrations.flask_client import OAuth
from models import User, db

google_auth = Blueprint('google_auth', __name__)
oauth = OAuth()

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

@google_auth.route('/login/google')
def google_login():
    redirect_uri = url_for('google_auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@google_auth.route('/login/google/callback')
def google_callback():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    
    email = user_info['email']
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Create new user
        user = User(
            email=email,
            username=user_info.get('given_name', email.split('@')[0]),
            first_name=user_info.get('given_name'),
            last_name=user_info.get('family_name'),
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('index'))
