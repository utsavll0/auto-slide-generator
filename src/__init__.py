import os
import dotenv
from flask import Flask
from flasgger import Swagger
from .routes.auth_routes import auth_bp
from .routes.presentation_routes import presentation_bp

def create_app():
    """Application factory function for Flask app."""
    dotenv.load_dotenv()
    print("Starting the application...")
    
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    
    # Initialize extensions
    swagger = Swagger(app)
    
    # Register blueprints
    app.register_blueprint(presentation_bp, url_prefix='/presentation')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app