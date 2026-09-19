# app/routes.py
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import get_weather, get_random_quote
from app.models import User
from app.decorators.log_decorator import log_route
from app.logger import get_logger
import time
from sqlalchemy import text

def register_routes(app):
    """Register all routes with the app"""


    @app.route('/test', methods=['GET'])
    def test_check():
        """Test check endpoint (public)"""
        logger = get_logger(app, 'auth')
        logger.warning({
                'event': 'TEST_EVENT'
        })
        logger.warning("Test message!")

        try:
            from app.models import db
            db.session.execute(text('SELECT 1'))
            status = 'healthy'
            db_status = 'connected'
        except Exception as e:
            status = 'unhealthy'
            db_status = 'disconnected'
            # ✅ Use 'app' directly - we have it!
            app.logger.error(f"Health check failed: {e}")
        
        return jsonify({
            'This is test': 'true',
            'status': status,
            'database': db_status,
            'timestamp': time.time()
        }), 200 if status == 'healthy' else 503
    
    









    @app.route('/my-ip', methods=['GET'])
    @log_route(
        level='INFO',
        include_request_body=False,
        event_type='IP_LOOKUP'
    )
    def get_my_ip():
        """Return the client's IP address (public)"""
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        
        return jsonify({
            'ip': ip,
            'timestamp': time.time()
        })
    
    @app.route('/health', methods=['GET'])
    @log_route(
        level='INFO',
        include_request_body=False,
        event_type='HEALTH_CHECK'
    )
    def health_check():
        """Health check endpoint (public)"""
        try:
            from app.models import db
            db.session.execute(text('SELECT 1'))
            status = 'healthy'
            db_status = 'connected'
        except Exception as e:
            status = 'unhealthy'
            db_status = 'disconnected'
            # ✅ Use 'app' directly - we have it!
            app.logger.error(f"Health check failed: {e}")
        
        return jsonify({
            'status': status,
            'database': db_status,
            'timestamp': time.time()
        }), 200 if status == 'healthy' else 503
    
    @app.route('/favicon.ico')
    @log_route(level='DEBUG', include_request_body=False)
    def favicon():
        """Serve favicon.ico"""
        return '', 204
    
    @app.route('/api/weather', methods=['GET'])
    @log_route(
        level='INFO',
        include_request_body=False,
        log_to_business=True,
        event_type='WEATHER_REQUEST'
    )
    @jwt_required()
    def protected_weather():
        """Get weather with user info (protected)"""
        # ✅ Pass app to get_logger
        business_logger = get_logger(app, 'business')
        
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            request.user_id = user.id
            request.username = user.username
            
            location = request.args.get('location')
            if not location:
                return jsonify({'error': 'Location parameter is required'}), 400
            
            business_logger.info({
                'event': 'WEATHER_REQUEST_START',
                'user_id': user.id,
                'username': user.username,
                'location': location,
                'request_id': getattr(request, 'request_id', None)
            })
            
            start_time = time.time()
            weather_data = get_weather(location)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if 'error' in weather_data:
                business_logger.warning({
                    'event': 'WEATHER_REQUEST_FAILED',
                    'user_id': user.id,
                    'username': user.username,
                    'location': location,
                    'error': weather_data['error'],
                    'response_time_ms': response_time,
                    'request_id': getattr(request, 'request_id', None)
                })
                return jsonify(weather_data), 404
            
            weather_data['requested_by'] = user.username
            
            business_logger.info({
                'event': 'WEATHER_REQUEST_SUCCESS',
                'user_id': user.id,
                'username': user.username,
                'location': location,
                'temperature': weather_data.get('temperature'),
                'response_time_ms': response_time,
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify(weather_data), 200
            
        except Exception as e:
            # ✅ Use 'app' directly
            app.logger.error(f"Weather error: {str(e)}")
            return jsonify({'error': 'Failed to get weather'}), 500
    
    @app.route('/api/quotes', methods=['GET'])
    @log_route(
        level='INFO',
        include_request_body=False,
        log_to_business=True,
        event_type='QUOTE_REQUEST'
    )
    @jwt_required()
    def protected_quote():
        """Return a random quote (protected)"""
        # ✅ Pass app to get_logger
        business_logger = get_logger(app, 'business')
        
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            request.user_id = user.id
            request.username = user.username
            
            quote_data = get_random_quote()
            
            business_logger.info({
                'event': 'QUOTE_REQUEST_SUCCESS',
                'user_id': user.id,
                'username': user.username,
                'author': quote_data.get('author'),
                'request_id': getattr(request, 'request_id', None)
            })
            
            return jsonify(quote_data)
            
        except Exception as e:
            # ✅ Use 'app' directly
            app.logger.error(f"Quote error: {str(e)}")
            return jsonify({'error': 'Failed to get quote'}), 500
