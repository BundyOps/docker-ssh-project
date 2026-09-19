# app/auth.py
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from app.models import db, User
from app.decorators.log_decorator import log_route
from app.logger import get_logger

def register_auth_routes(app):
    """Register all authentication routes"""
    
    @app.route('/api/auth/register', methods=['POST'])
    @log_route(
        level='INFO',
        include_request_body=True,
        mask_sensitive=True,
        sensitive_fields=['password'],
        log_to_security=True,
        log_to_auth=True,
        audit=True,
        event_type='USER_REGISTERED'
    )
    def register():
        """Register a new user"""
        # ✅ Pass app to get_logger
        logger = get_logger(app, 'auth')
        security_logger = get_logger(app, 'security')
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            if User.query.filter_by(username=data['username']).first():
                security_logger.warning({
                    'event': 'REGISTRATION_FAILED',
                    'reason': 'Username taken',
                    'username': data['username'],
                    'ip': request.remote_addr,
                    'request_id': getattr(request, 'request_id', None)
                })
                return jsonify({'error': 'Username already taken'}), 409
            
            if User.query.filter_by(email=data['email']).first():
                security_logger.warning({
                    'event': 'REGISTRATION_FAILED',
                    'reason': 'Email taken',
                    'email': data['email'],
                    'ip': request.remote_addr,
                    'request_id': getattr(request, 'request_id', None)
                })
                return jsonify({'error': 'Email already registered'}), 409
            
            user = User(
                username=data['username'],
                email=data['email']
            )
            user.password = data['password']
            db.session.add(user)
            db.session.commit()
            
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            logger.info({
                'event': 'REGISTRATION_SUCCESS',
                'user_id': user.id,
                'username': user.username,
                'ip': request.remote_addr,
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'message': 'User created successfully',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 201
            
        except ValueError as e:
            logger.warning({
                'event': 'REGISTRATION_VALIDATION_ERROR',
                'error': str(e),
                'ip': request.remote_addr,
                'request_id': getattr(request, 'request_id', None)
            })
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            # ✅ Use 'app' directly
            app.logger.error(f"Registration error: {str(e)}")
            return jsonify({'error': 'Registration failed'}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    @log_route(
        level='INFO',
        include_request_body=True,
        mask_sensitive=True,
        sensitive_fields=['password'],
        log_to_security=True,
        log_to_auth=True,
        audit=True,
        event_type='USER_LOGIN'
    )
    def login():
        """Login user and return tokens"""
        # ✅ Pass app to get_logger
        logger = get_logger(app, 'auth')
        security_logger = get_logger(app, 'security')
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            identifier = data.get('username') or data.get('email')
            password = data.get('password')
            
            if not identifier or not password:
                return jsonify({'error': 'Username/email and password required'}), 400
            
            user = User.query.filter(
                (User.username == identifier) | (User.email == identifier)
            ).first()
            
            if not user or not user.is_active:
                security_logger.warning({
                    'event': 'LOGIN_FAILED',
                    'reason': 'User not found or inactive',
                    'identifier': identifier,
                    'ip': request.remote_addr,
                    'request_id': getattr(request, 'request_id', None)
                })
                return jsonify({'error': 'Invalid credentials'}), 401
            
            if not user.check_password(password):
                security_logger.warning({
                    'event': 'LOGIN_FAILED',
                    'reason': 'Invalid password',
                    'user_id': user.id,
                    'username': user.username,
                    'ip': request.remote_addr,
                    'request_id': getattr(request, 'request_id', None)
                })
                return jsonify({'error': 'Invalid credentials'}), 401
            
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            logger.info({
                'event': 'LOGIN_SUCCESS',
                'user_id': user.id,
                'username': user.username,
                'ip': request.remote_addr,
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 200
            
        except Exception as e:
            # ✅ Use 'app' directly
            app.logger.error(f"Login error: {str(e)}")
            return jsonify({'error': 'Login failed'}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    @log_route(
        level='INFO',
        include_request_body=False,
        log_to_security=True,
        log_to_auth=True,
        event_type='TOKEN_REFRESHED'
    )
    @jwt_required(refresh=True)
    def refresh():
        """Get new access token using refresh token"""
        # ✅ Pass app to get_logger
        logger = get_logger(app, 'auth')
        
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            new_access_token = create_access_token(identity=str(user.id))
            
            logger.info({
                'event': 'TOKEN_REFRESH_SUCCESS',
                'user_id': user.id,
                'username': user.username,
                'ip': request.remote_addr,
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify({
                'access_token': new_access_token
            }), 200
            
        except Exception as e:
            # ✅ Use 'app' directly
            app.logger.error(f"Refresh error: {str(e)}")
            return jsonify({'error': 'Refresh failed'}), 500
    
    @app.route('/api/auth/me', methods=['GET'])
    @log_route(
        level='INFO',
        include_request_body=False,
        log_to_auth=True,
        event_type='USER_PROFILE_ACCESS'
    )
    @jwt_required()
    def get_current_user():
        """Get current user info"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Set user context for logging
            request.user_id = user.id
            request.username = user.username
            
            return jsonify(user.to_dict()), 200
            
        except Exception as e:
            # ✅ Use 'app' directly
            app.logger.error(f"Get user error: {str(e)}")
            return jsonify({'error': 'Failed to get user'}), 500