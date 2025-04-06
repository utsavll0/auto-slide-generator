from ..functions.auth import get_user_token
from flask import request, g, jsonify
from functools import wraps

def auth_required(f):
    """Decorator to enforce authentication on protected endpoints."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        username = request.headers.get("X-Username")
        if not username:
            return jsonify({"error": "Username header required"}), 400

        token = get_user_token(username)
        if not token:
            return jsonify({"error": "Authentication required"}), 401

        g.access_token = token
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper