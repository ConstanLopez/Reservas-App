import bcrypt
import jwt
from datetime import datetime, timedelta
from app.config import Config

def hash_password(password):
    """Genera hash de la contraseña"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verifica si la contraseña coincide con el hash"""
    password_bytes = password.encode('utf-8')
    password_hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, password_hash_bytes)

def generate_token(user_data):
    """Genera un JWT token"""
    payload = {
        'correo': user_data['correo'],
        'ci': user_data['ci'],
        'nombre': user_data['nombre'],
        'apellido': user_data['apellido'],
        'rol': user_data.get('rol', 'alumno'),
        'tipo_programa': user_data.get('tipo_programa', 'grado'),
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_EXPIRATION)
    }
    
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    """Verifica y decodifica un JWT token"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido