# app/decorators/log_decorator.py
import time
import functools
import uuid
import json
import logging
from flask import request, g, has_request_context, current_app
from app.logger import get_logger

def mask_sensitive_data(data, sensitive_fields=None):
    """Mask sensitive fields in data"""
    if not data:
        return data
    
    if not sensitive_fields:
        sensitive_fields = ['password', 'token', 'refresh_token', 'api_key', 'secret']
    
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in [f.lower() for f in sensitive_fields]:
                masked[key] = '****MASKED****'
            elif isinstance(value, dict):
                masked[key] = mask_sensitive_data(value, sensitive_fields)
            elif isinstance(value, list):
                masked[key] = [mask_sensitive_data(item, sensitive_fields) if isinstance(item, (dict, list)) else item for item in value]
            else:
                masked[key] = value
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, sensitive_fields) if isinstance(item, (dict, list)) else item for item in data]
    else:
        return data

def truncate_data(data, max_length=500):
    """Truncate long data for logging"""
    if not data:
        return data
    
    if isinstance(data, str) and len(data) > max_length:
        return data[:max_length] + '...TRUNCATED'
    elif isinstance(data, dict):
        return {k: truncate_data(v, max_length) for k, v in data.items()}
    elif isinstance(data, list):
        return [truncate_data(item, max_length) if isinstance(item, (str, dict)) else item for item in data]
    else:
        return data

def mask_email(email):
    """Mask email addresses for privacy"""
    if not email:
        return email
    if '@' not in email:
        return email
    parts = email.split('@')
    if len(parts[0]) <= 2:
        return f"{parts[0][0]}***@{parts[1]}"
    return f"{parts[0][0]}***{parts[0][-1]}@{parts[1]}"

def log_route(
    level='INFO',
    include_request_body=False,
    include_response_body=False,
    mask_sensitive=True,
    sensitive_fields=None,
    log_to_security=False,
    log_to_business=False,
    log_to_auth=False,
    audit=False,
    event_type=None
):
    """Comprehensive logging decorator for Flask routes"""
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            # Get the app instance from current_app
            app = current_app._get_current_object()
            
            # Generate request ID
            if has_request_context():
                request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
                g.request_id = request_id
                request.request_id = request_id
            else:
                request_id = str(uuid.uuid4())
            
            # Start timer
            start_time = time.time()
            
            # Get loggers by passing app
            app_logger = get_logger(app, 'app')
            access_logger = get_logger(app, 'access')
            security_logger = get_logger(app, 'security') if log_to_security else None
            business_logger = get_logger(app, 'business') if log_to_business else None
            auth_logger = get_logger(app, 'auth') if log_to_auth else None
            
            # Build request context
            context = {
                'request_id': request_id,
                'route': request.path if has_request_context() else 'unknown',
                'method': request.method if has_request_context() else 'unknown',
                'client_ip': request.remote_addr if has_request_context() else None,
                'user_agent': request.headers.get('User-Agent') if has_request_context() else None
            }
            
            # Add user context if authenticated
            if has_request_context() and hasattr(request, 'user_id'):
                context['user_id'] = request.user_id
            if has_request_context() and hasattr(request, 'username'):
                context['username'] = request.username
            
            # Log request start
            log_data = {
                'event': 'REQUEST_START',
                'context': context
            }
            
            # Add request body if needed
            if include_request_body and has_request_context():
                try:
                    body = request.get_json(silent=True) or {}
                    if mask_sensitive:
                        body = mask_sensitive_data(body, sensitive_fields)
                        if isinstance(body, dict):
                            for key in ['email', 'username']:
                                if key in body and '@' in str(body[key]):
                                    body[key] = mask_email(body[key])
                    log_data['request_body'] = truncate_data(body)
                except:
                    pass
            
            # Log the request
            log_level = getattr(logging, level.upper(), logging.INFO)
            app_logger.log(log_level, json.dumps(log_data))
            
            # Log to access logger
            access_data = {
                'event': 'REQUEST',
                'method': context['method'],
                'path': context['route'],
                'ip': context['client_ip'],
                'request_id': context['request_id']
            }
            if 'user_id' in context:
                access_data['user_id'] = context['user_id']
            access_logger.info(json.dumps(access_data))
            
            # Execute the route
            response = None
            error = None
            try:
                response = f(*args, **kwargs)
                return response
            except Exception as e:
                error = e
                raise
            finally:
                # Calculate response time
                response_time_ms = round((time.time() - start_time) * 1000, 2)
                
                # Get response status
                status_code = getattr(response, 'status_code', 500) if response else 500
                
                # Log response
                response_data = {
                    'event': 'REQUEST_END',
                    'context': {
                        'request_id': request_id,
                        'route': context['route'],
                        'method': context['method'],
                        'response_time_ms': response_time_ms,
                        'status_code': status_code,
                        'success': status_code < 400
                    }
                }
                
                # Add response body if needed
                if include_response_body and response and hasattr(response, 'get_json'):
                    try:
                        body = response.get_json()
                        if mask_sensitive:
                            body = mask_sensitive_data(body, sensitive_fields)
                        response_data['response_body'] = truncate_data(body)
                    except:
                        pass
                
                # Log error if present
                if error:
                    response_data['error'] = str(error)
                    response_data['event'] = 'REQUEST_ERROR'
                
                app_logger.log(log_level, json.dumps(response_data))
                
                # Log to security logger if requested
                if security_logger and (log_to_security or status_code >= 400):
                    security_data = {
                        'event': event_type or 'SECURITY_EVENT',
                        'context': context,
                        'status_code': status_code,
                        'success': status_code < 400,
                        'response_time_ms': response_time_ms
                    }
                    if error:
                        security_data['error'] = str(error)
                    security_logger.warning(json.dumps(security_data))
                
                # Log to business logger if requested
                if business_logger and log_to_business:
                    business_data = {
                        'event': event_type or 'BUSINESS_EVENT',
                        'context': context,
                        'status_code': status_code,
                        'response_time_ms': response_time_ms
                    }
                    business_logger.info(json.dumps(business_data))
                
                # Log to auth logger if requested
                if auth_logger and log_to_auth:
                    auth_data = {
                        'event': event_type or 'AUTH_EVENT',
                        'context': context,
                        'status_code': status_code,
                        'success': status_code < 400
                    }
                    if error:
                        auth_data['error'] = str(error)
                    auth_logger.info(json.dumps(auth_data))
                
                # Audit log for critical events
                if audit:
                    audit_data = {
                        'event': event_type or 'AUDIT_EVENT',
                        'context': context,
                        'timestamp': time.time()
                    }
                    app_logger.critical(json.dumps(audit_data))
        
        return wrapped
    return decorator