# app/logger.py
import logging
import logging.handlers
import os
import json
from datetime import datetime
from flask import request, has_request_context

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage()
        }
        
        # Add request context if available
        if has_request_context():
            log_data['request_id'] = getattr(request, 'request_id', None)
            log_data['client_ip'] = request.remote_addr
            log_data['method'] = request.method
            log_data['path'] = request.path
            
            # Add user context if available
            if hasattr(request, 'user_id'):
                log_data['user_id'] = request.user_id
            if hasattr(request, 'username'):
                log_data['username'] = request.username
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data)

# app/logger.py
def setup_logging(app):
    """Configure logging for the application"""
    
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    app.logger.handlers.clear()
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    # 1. Main app log
    app_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10_000_000,
        backupCount=10
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(JSONFormatter())
    app.logger.addHandler(app_handler)
    app.logger.setLevel(log_level)  # ✅ SET LOGGER LEVEL
    
    # 2. Access log
    access_logger = logging.getLogger('access')
    access_logger.handlers.clear()
    access_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'access.log'),
        maxBytes=10_000_000,
        backupCount=10
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(JSONFormatter())
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)  # ✅ SET LOGGER LEVEL
    access_logger.propagate = False
    
    # 3. Security log
    security_logger = logging.getLogger('security')
    security_logger.handlers.clear()
    security_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'security.log'),
        maxBytes=10_000_000,
        backupCount=10
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(JSONFormatter())
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)  # ✅ SET LOGGER LEVEL
    security_logger.propagate = False
    
    # 4. Business log
    business_logger = logging.getLogger('business')
    business_logger.handlers.clear()
    business_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'business.log'),
        maxBytes=10_000_000,
        backupCount=10
    )
    business_handler.setLevel(logging.INFO)
    business_handler.setFormatter(JSONFormatter())
    business_logger.addHandler(business_handler)
    business_logger.setLevel(logging.INFO)  # ✅ SET LOGGER LEVEL
    business_logger.propagate = False
    
    # 5. Auth log - ✅ THIS IS THE ONE THAT WAS BROKEN
    auth_logger = logging.getLogger('auth')
    auth_logger.handlers.clear()
    auth_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'auth.log'),
        maxBytes=10_000_000,
        backupCount=10
    )
    auth_handler.setLevel(logging.INFO)
    auth_handler.setFormatter(JSONFormatter())
    auth_logger.addHandler(auth_handler)
    auth_logger.setLevel(logging.INFO)  # ✅ SET LOGGER LEVEL - THIS WAS MISSING!
    auth_logger.propagate = False
    
    # 6. Error log
    error_logger = logging.getLogger('error')
    error_logger.handlers.clear()
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10_000_000,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    error_logger.addHandler(error_handler)
    error_logger.setLevel(logging.ERROR)  # ✅ SET LOGGER LEVEL
    error_logger.propagate = False
    
    # 7. Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    app.logger.addHandler(console_handler)
    
    # Store loggers in app config
    app.config['LOGGERS'] = {
        'app': app.logger,
        'access': access_logger,
        'security': security_logger,
        'business': business_logger,
        'auth': auth_logger,
        'error': error_logger
    }
    
    return app.logger

def get_logger(app, name='app'):
    """
    Get a logger by name.
    Simply pass the app instance to get the logger.
    """
    if 'LOGGERS' in app.config:
        return app.config['LOGGERS'].get(name, app.logger)
    return app.logger

# Convenience functions - pass app to these
def get_access_logger(app):
    return get_logger(app, 'access')

def get_security_logger(app):
    return get_logger(app, 'security')

def get_business_logger(app):
    return get_logger(app, 'business')

def get_auth_logger(app):
    return get_logger(app, 'auth')

def get_error_logger(app):
    return get_logger(app, 'error')