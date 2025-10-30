import bcrypt #Libreria para encriptar contraseñas
import jwt #json web token
from datetime import datetime, timedelta # sirve para manejar la caducacion del JWT
from app.config import Config

'''
Tenemos métodos para :
-Generar hash seguro de contraseña 
-Comprobar si la contraseña coincide
-Crear un token JWT con datos del usuario y fecha de expiración
-Validar token JWT y devolver su contenido si es válido
'''
def hash_password(password):
    """Genera hash de la contraseña"""
    password_bytes = password.encode('utf-8') #convierte la contraseña a bytes ya que bycript trabaja en binario
    salt = bcrypt.gensalt() # Genera una sal aleatoria (cadena aleatoria que se agrega al password antes de cifrar).Esto garantiza que dos usuarios con la misma contraseña tendrán hashes distintos.
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8') # aplica bycrypt usando esa sal y convierte los bytes a texto legible para guardarlos en la db

def verify_password(password, password_hash):
    """Verifica si la contraseña coincide con el hash guardado en la base de datos"""
    password_bytes = password.encode('utf-8') #convierte la contraseña a bytes ya que bycript trabaja en binario
    password_hash_bytes = password_hash.encode('utf-8') #convierte el hash a bytes ya que bycript trabaja en binario
    return bcrypt.checkpw(password_bytes, password_hash_bytes) # Compara el password ingresado con el hash original devuele True si coinciden, sino devuelve False


'''
Un JWT (JSON Web Token) es una cadena codificada que contiene información verificable 
sobre un usuario (sin necesidad de guardar sesión en el servidor).
El JWT tiene tres partes HEADER.PAYLOAD.SIGNATURE
'''
def generate_token(user_data):
    """Genera un JWT token que contiene los datos del usuario  y una fecha de expiración"""
    payload = { # son los datos que van a estar dentro del token
        'correo': user_data['correo'],
        'ci': user_data['ci'],
        'nombre': user_data['nombre'],
        'apellido': user_data['apellido'],
        'rol': user_data.get('rol', 'alumno'),
        'tipo_programa': user_data.get('tipo_programa', 'grado'),
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_EXPIRATION)
    }
    
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256') #usa la calve secreta para firmar el token y el agloritmo estandar de JWT HS256 
    return token # devuelve el token, que es una cadena alfanumérica codificada

def verify_token(token):
    """Verifica y decodifica un JWT token"""
    try:
        '''Si es correcto el token y no expiro devuelve el payload'''
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        '''Si expiro el token'''
        return None  # Token expirado
    except jwt.InvalidTokenError:
        '''Si el token es inválido o tiene un error'''
        return None  # Token inválido