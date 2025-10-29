from functools import wraps
from flask import request, jsonify
from app.utils.auth_utils import verify_token

def token_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obtener token del header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verificar token
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Agregar datos del usuario al request (mantener compatibilidad)
        request.user = payload
        
        # NUEVO: Pasar current_user como keyword argument a la función
        kwargs['current_user'] = payload
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorador para rutas que requieren rol de docente/admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'user'):
            return jsonify({'error': 'No autorizado'}), 403
        
        if request.user.get('rol') != 'docente':
            return jsonify({'error': 'Requiere permisos de docente'}), 403
        
        return f(*args, **kwargs)
    
    return decorated