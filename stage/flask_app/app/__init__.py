from flask import Flask
from flask_cors import CORS
import logging
import os

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configure logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    app.config.from_object('app.config.Config')
    
    # Register routes
    from app.routes import register_routes
    register_routes(app)
    
    return app
