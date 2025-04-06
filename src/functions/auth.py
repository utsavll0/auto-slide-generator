import time
from ..helpers import http_request
import os
from flask import g, session

AUTH_URL = "https://api.getalai.com/auth/v1/token?grant_type=password"

def authenticate(username, password):
    """Authenticate user with third-party API."""
    response = http_request.post_request(
        AUTH_URL,
        data={
            "email": username,
            "password": password,
            "gotrue_meta_security": {}
        },
        headers={"Apikey": os.getenv("ALAI_API_KEY")}
    )
    if response.status_code == 200:
        data = response.json()
        session[username] = {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": data["expires_at"],
        }
        return data
    return None


def refresh_token(username):
    """Refresh user's access token using refresh token."""
    if username not in session:
        return None

    refresh_token = session[username]["refresh_token"]
    refresh_response = http_request.post_request(
        AUTH_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )

    if refresh_response.status_code == 200:
        data = refresh_response.json()
        session[username]["access_token"] = data["access_token"]
        session[username]["expires_at"] = data["expires_at"]
        return data["access_token"]
    
    return None


def get_user_token(username):
    """Retrieve valid access token for user, refreshing if necessary."""
    if username not in session:
        return None

    user_session = session[username]
    current_time = time.time()

    if user_session["expires_at"] < current_time:  # Token expired
        new_token = refresh_token(username)
        if new_token:
            return new_token
        else:
            return None  # Token refresh failed

    return user_session["access_token"]