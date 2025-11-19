from functools import wraps
from flask import request, jsonify
from app.utils.auth_utils import verify_token

def token_required(f): #exige que el usuario tenga este autneticado con un JWT valido
    """Decorador (funcion que envuelve otra funcion) para proteger rutas en Flask que requieren autenticación y rol"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Obtener token del header
        auth_header = request.headers.get('Authorization') #Se obtiene el token del header
        
        if not auth_header or not auth_header.startswith('Bearer '): #Si el header no esta, o no empieza con Bearer  se devuelve error
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        token = auth_header.split(' ')[1] #Se extrae el token del header
        
        # Verificar token
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Agregar datos del usuario al request (mantener compatibilidad)
        request.user = payload
        
        #  Pasar current_user como keyword argument a la función
        kwargs['current_user'] = payload
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorador para rutas que requieren rol de administrador"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        current_user = kwargs.get('current_user')
        
        if not current_user or current_user.get('rol') != 'admin':
            return jsonify({'error': 'Acceso solo para administradores'}), 403
        
        return f(*args, **kwargs)
    
    return decorated