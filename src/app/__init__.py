# app/__init__.py
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import uuid

from app.config import Config
from app.models import db, bcrypt
from app.logger import setup_logging, get_logger
from app.auth import register_auth_routes
from app.routes import register_routes

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Log the database URL (without credentials for security)
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    # Mask credentials for logging
    masked_url = db_url.replace(db_url.split('://')[1].split('@')[0].split(':')[0], '***')
    app.logger.info(f"Using database: {masked_url}")
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Setup logging
    setup_logging(app)
    
    # Get logger by passing app
    logger = get_logger(app, 'app')
    logger.info("Application starting up")
    
    # Request ID middleware
    @app.before_request
    def set_request_id():
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.request_id = request_id
        request.request_id = request_id
    
    # User context middleware
    @app.before_request
    def set_user_context():
        request.user_id = None
        request.username = None
    
    # Register routes
    register_routes(app)
    register_auth_routes(app)
    
    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        sec_logger = get_logger(app, 'security')
        sec_logger.warning({
            'event': 'UNAUTHORIZED_ACCESS',
            'path': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(request, 'request_id', None)
        })
        return jsonify({'error': 'Missing or invalid token'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        sec_logger = get_logger(app, 'security')
        sec_logger.warning({
            'event': 'INVALID_TOKEN',
            'path': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(request, 'request_id', None)
        })
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.expired_token_loader
    def expired_token_response(callback):
        sec_logger = get_logger(app, 'security')
        sec_logger.warning({
            'event': 'EXPIRED_TOKEN',
            'path': request.path,
            'ip': request.remote_addr,
            'request_id': getattr(request, 'request_id', None)
        })
        return jsonify({'error': 'Token has expired'}), 401
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        err_logger = get_logger(app, 'error')
        err_logger.error({
            'event': 'NOT_FOUND',
            'path': request.path,
            'method': request.method,
            'ip': request.remote_addr,
            'request_id': getattr(request, 'request_id', None)
        })
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        err_logger = get_logger(app, 'error')
        err_logger.error({
            'event': 'INTERNAL_ERROR',
            'path': request.path,
            'method': request.method,
            'error': str(error),
            'request_id': getattr(request, 'request_id', None)
        })
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create tables (if they don't exist)
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    return app