from flask import request, jsonify, current_app, send_from_directory
from app.utils import get_weather, get_random_quote
import time
import os

def register_routes(app):
    """Register all routes with the app"""
    
    @app.before_request
    def log_request_info():
        """Log incoming requests"""
        current_app.logger.info(f"Request: {request.method} {request.url}")
        if request.data:
            current_app.logger.debug(f"Request Body: {request.data}")
        if request.args:
            current_app.logger.debug(f"Request Args: {request.args}")

    @app.after_request
    def log_response_info(response):
        """Log outgoing responses"""
        current_app.logger.info(f"Response: {response.status_code} - {request.method} {request.url}")
        return response

    @app.route('/my-ip', methods=['GET'])
    def get_my_ip():
        """Return the client's IP address"""
        current_app.logger.debug(f"=== /my-ip REQUEST START ===")
        current_app.logger.debug(f"Headers: {dict(request.headers)}")
        
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        current_app.logger.debug(f"Raw IP: {ip}")
        
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
            current_app.logger.debug(f"After split: {ip}")
        
        response = jsonify({
            'ip': ip,
            'timestamp': time.time()
        })
        
        current_app.logger.debug(f"Response: {response.get_json()}")
        current_app.logger.debug(f"=== /my-ip REQUEST END ===")
        return response
        # ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        # if ip and ',' in ip:
        #     ip = ip.split(',')[0].strip()
        
        # return jsonify({
        #     'ip': ip,
        #     'timestamp': time.time()
        # })

    @app.route('/weather', methods=['GET'])
    def weather():
        """Return weather information for a location"""
        location = request.args.get('location')
        
        if not location:
            return jsonify({'error': 'Location parameter is required'}), 400
        
        weather_data = get_weather(location)
        
        if 'error' in weather_data:
            return jsonify(weather_data), 404
        
        return jsonify(weather_data)

    @app.route('/quote', methods=['GET'])
    def quote():
        """Return a random quote"""
        quote_data = get_random_quote()
        return jsonify(quote_data)

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({'status': 'healthy', 'timestamp': time.time()})

    @app.route('/crash')
    def crash():
        """Intentionally crash to test debugger"""
        # This will cause a ZeroDivisionError
        result = 1 / 0
        return jsonify({'result': result})
        
    @app.route('/favicon.ico')
    def favicon():
        """Serve favicon.ico"""
        return '', 204
#        return send_from_directory('static', 'favicon.ico')
#        return redirect(url_for('static', filename='favicon.ico'))
#        return send_from_directory(
#            os.path.join(app.root_path, 'static'),
#            'favicon.ico',
#            mimetype='image/vnd.microsoft.icon'
#            )
