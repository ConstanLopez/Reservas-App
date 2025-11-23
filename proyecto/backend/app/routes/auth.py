# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin #cross origin se usa en cada endpoint
from app.models.auth import Auth
from app.database import fetch_query
from app.utils.auth_utils import hash_password, verify_password, generate_token

#Creamos un Blueprint, que va a agrupar todas las rutas bajo el prefijo  /api/auth
bp = Blueprint('auth', __name__, url_prefix='/api/auth')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

@bp.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['POST','OPTIONS'],
              allow_headers=['Content-Type','Authorization'],
              expose_headers=['Authorization'])


def register():
    if request.method == 'OPTIONS': #Esto lo que hace es autorizar el preflight del buscador antes de la query real, esto ya que esta el método OPTIONS del CORS
        return ('', 204) 

    data = request.get_json(silent=True) or {} #Obtenemos el JSON del FRONTEND,  silent=True => evita lanzar error si el JSON no está bien formado, y none como valor por defecto
    required_fields = ['ci', 'nombre', 'apellido', 'email', 'password','rol','nombre_programa'] # campos obligatorios
    for field in required_fields:
        if not data.get(field): # si falta algun dato requerido se devuelve un error
            return jsonify({'error': f'El campo {field} es requerido'}), 400 #se devuelve un JSON con el campo que falta

    #Extrae del JSON de la request los campos requeridos 
    ci = data['ci']; nombre = data['nombre']; apellido = data['apellido']
    email = data['email'].strip().lower(); password = data['password']
    nombre_programa = data['nombre_programa'].strip(); rol = data['rol'];

    row_prog = fetch_query(
        "SELECT tipo FROM programa_academico WHERE nombre_programa = %s",
        (nombre_programa,)
    )

    if not row_prog:
        return jsonify({'error': 'El programa académico seleccionado no existe'}), 400

    tipo_programa = row_prog[0]['tipo']  # 'grado' o 'posgrado'
    
    #Controla si el ci, o el mail ya estan registrados y el largo de la contraseña
    if Auth.email_existe(email):
        return jsonify({'error': 'El email ya está registrado'}), 400
    if Auth.ci_existe(ci):
        return jsonify({'error': 'La CI ya está registrada'}), 400
    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    try:
        #genera el hash de la contrasena con bycrypt
        password_hash = hash_password(password)

        #Crea el nuevo registro en la tabla login y participante
        Auth.crear_login(email, password_hash)
        Auth.crear_participante(ci, nombre, apellido, email)

        #Si el usuario esta en un programa, lo asigna
        if nombre_programa:
            Auth.asignar_programa(ci, nombre_programa, rol)

        #Crea un diccionario con los datos del usuario y con generate_token crea un JWT firmado con la SECRET_KEY
        #Este token  se devuelve al frontend para matener la sesión del usuario
        user_data = {'correo': email, 'ci': ci, 'nombre': nombre,
                     'apellido': apellido, 'rol': rol, 'tipo_programa': tipo_programa}
        token = generate_token(user_data)

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'token': token, #Token JWT
            'user': {'ci': ci, 'nombre': nombre, 'apellido': apellido, 'email': email, 'rol': rol,'tipo_programa': tipo_programa} #Datos visibles del usuario
        }), 201
    except Exception as e:
        print(f"Error en register: {e}")
        return jsonify({'error': 'Error al registrar usuario'}), 500


@bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['POST', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'],
              expose_headers=['Authorization'])
def login():
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    try:
        # 1) Buscar usuario en login + participante (incluye p.rol)
        usuario = Auth.obtener_usuario_por_email(data['email'])

        # 2) Validar contraseña
        if not usuario or not verify_password(data['password'], usuario['password_hash']):
            return jsonify({'error': 'Credenciales inválidas'}), 401

        # 3) Roles académicos (lo que ya tenías)
        roles_academicos = Auth.obtener_roles_usuario(usuario['ci'])
        rol_academico = roles_academicos[0]['rol_academico'] if roles_academicos else 'alumno'
        tipo_programa = roles_academicos[0]['tipo'] if roles_academicos else 'grado'

        # 4) Rol de sistema (para admin / usuario) -> viene de la tabla participante
        rol_sistema = usuario.get('rol_sistema', 'usuario')  # p.rol, default 'usuario'

        # 5) Payload para el JWT
        user_data = {
            'correo': usuario['correo'],
            'ci': usuario['ci'],
            'nombre': usuario['nombre'],
            'apellido': usuario['apellido'],
            'rol': rol_sistema,             # 👈 rol de sistema
            'tipo_programa': tipo_programa,
            'rol_academico': rol_academico  # opcional, por si lo necesitás luego
        }
        token = generate_token(user_data)

        # 6) Respuesta al frontend
        return jsonify({
            'message': 'Login exitoso',
            'token': token,
            'user': {
                'ci': usuario['ci'],
                'nombre': usuario['nombre'],
                'apellido': usuario['apellido'],
                'email': usuario['correo'],
                'rol': rol_sistema,              # 👈 acá el front ve 'admin' o 'usuario'
                'tipo_programa': tipo_programa,
                'rol_academico': rol_academico
            }
        }), 200

    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({'error': 'Error al iniciar sesión'}), 500

#Esta ruta sirve para verificar la validez del token JWT que envía el frontend. Clave para mantener sesiones persistentes o validar accesos
@bp.route('/verify', methods=['GET'])
def verify():
    from app.utils.auth_utils import verify_token
    auth_header = request.headers.get('Authorization') #Busca el header  Authorization en la solicitud
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Token no proporcionado'}), 401
    token = auth_header.split(' ')[1] #divide la cadena en dos Bearer y el token, se queda con la segunda
    payload = verify_token(token) #Verifica el token
    if not payload:
        return jsonify({'error': 'Token inválido o expirado'}), 401
    return jsonify({'valid': True, 'user': payload}), 200


@bp.route('/programas', methods=['GET'])
@cross_origin(
    origins=ORIGINS,
    methods=['GET'],
    allow_headers=['Content-Type', 'Authorization'],
)
def listar_programas():
    """
    Devuelve todos los programas académicos para llenar el combo del registro.
    """
    rows = fetch_query("""
        SELECT 
            nombre_programa,
            tipo      -- 'grado' o 'posgrado'
        FROM programa_academico
        ORDER BY nombre_programa
    """)
    return jsonify(rows), 200