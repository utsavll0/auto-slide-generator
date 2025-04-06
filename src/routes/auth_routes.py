from flask import Blueprint, request, jsonify
from ..functions.auth import authenticate

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return access token.
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "utsav"
            password:
              type: string
              example: "securepassword123"
    responses:
      200:
        description: Successful authentication
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            expires_at:
              type: integer
      401:
        description: Authentication failed
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    auth_response = authenticate(username, password)
    if auth_response:
        return jsonify(auth_response)

    return jsonify({"error": "Invalid credentials"}), 401