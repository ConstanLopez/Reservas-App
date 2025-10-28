# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.models.auth import Auth
from app.utils.auth_utils import hash_password, verify_password, generate_token

# 👇 prefijo directo: /api/auth
bp = Blueprint('auth', __name__, url_prefix='/api/auth')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

@bp.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['POST','OPTIONS'],
              allow_headers=['Content-Type','Authorization'],
              expose_headers=['Authorization'])
def register():
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    required_fields = ['ci', 'nombre', 'apellido', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'El campo {field} es requerido'}), 400

    ci = data['ci']; nombre = data['nombre']; apellido = data['apellido']
    email = data['email']; password = data['password']
    nombre_programa = data.get('nombre_programa'); rol = data.get('rol', 'alumno')

    if Auth.email_existe(email):
        return jsonify({'error': 'El email ya está registrado'}), 400
    if Auth.ci_existe(ci):
        return jsonify({'error': 'La CI ya está registrada'}), 400
    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    try:
        password_hash = hash_password(password)
        Auth.crear_login(email, password_hash)
        Auth.crear_participante(ci, nombre, apellido, email)
        if nombre_programa:
            Auth.asignar_programa(ci, nombre_programa, rol)

        user_data = {'correo': email, 'ci': ci, 'nombre': nombre,
                     'apellido': apellido, 'rol': rol, 'tipo_programa': 'grado'}
        token = generate_token(user_data)

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'token': token,
            'user': {'ci': ci, 'nombre': nombre, 'apellido': apellido, 'email': email, 'rol': rol}
        }), 201
    except Exception as e:
        print(f"Error en register: {e}")
        return jsonify({'error': 'Error al registrar usuario'}), 500


@bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['POST','OPTIONS'],
              allow_headers=['Content-Type','Authorization'],
              expose_headers=['Authorization'])
def login():
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    try:
        usuario = Auth.obtener_usuario_por_email(data['email'])
        if not usuario or not verify_password(data['password'], usuario['password_hash']):
            return jsonify({'error': 'Credenciales inválidas'}), 401

        roles = Auth.obtener_roles_usuario(usuario['ci'])
        rol = roles[0]['rol'] if roles else 'alumno'
        tipo_programa = roles[0]['tipo'] if roles else 'grado'

        user_data = {'correo': usuario['correo'], 'ci': usuario['ci'], 'nombre': usuario['nombre'],
                     'apellido': usuario['apellido'], 'rol': rol, 'tipo_programa': tipo_programa}
        token = generate_token(user_data)

        return jsonify({
            'message': 'Login exitoso',
            'token': token,
            'user': {'ci': usuario['ci'], 'nombre': usuario['nombre'], 'apellido': usuario['apellido'],
                     'email': usuario['correo'], 'rol': rol, 'tipo_programa': tipo_programa}
        }), 200
    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({'error': 'Error al iniciar sesión'}), 500


@bp.route('/verify', methods=['GET'])
def verify():
    from app.utils.auth_utils import verify_token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token no proporcionado'}), 401
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Token inválido o expirado'}), 401
    return jsonify({'valid': True, 'user': payload}), 200
