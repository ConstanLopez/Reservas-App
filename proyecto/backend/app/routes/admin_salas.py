from flask import Blueprint, jsonify, request
from app.models.sala import Sala
from app.middleware.auth_middleware import admin_required
from flask_cors import cross_origin
from app.database import fetch_query

bp = Blueprint('admin_salas', __name__, url_prefix='/api/admin/salas')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

@bp.route('/',methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET','OPTIONS'],
              allow_headers=['Content-Type','Authorization'],
              expose_headers=['Authorization'])
def listar_salas():
    try:
        #Listamos todas las salas
        salas = Sala.get_all()
        return jsonify({'success': True, 'data': salas}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.post('/')
@admin_required
def crear_sala(current_user):
    try:
        data = request.get_json()
        required = ['nombre_sala', 'edificio', 'capacidad', 'tipo_sala']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400
        #Creamos la sala con los datos recibidos
        ok, msg = Sala.crear(
            data['nombre_sala'],
            data['edificio'],
            data['capacidad'],
            data['tipo_sala']
        )
        status = 201 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.put('/')
@admin_required
def actualizar_sala(current_user):
    try:
        data = request.get_json()
        required = ['nombre_sala', 'edificio', 'capacidad', 'tipo_sala']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400
        #Actualizamos la sala con los datos recibidos
        ok, msg = Sala.actualizar(
            data['nombre_sala'],
            data['edificio'],
            data['capacidad'],
            data['tipo_sala']
        )
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@bp.delete('/')
@admin_required
def eliminar_sala(current_user):
    try:
        data = request.get_json()
        required = ['nombre_sala', 'edificio']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400
        #Eliminamos la sala con los datos recibidos
        ok, msg = Sala.eliminar(data['nombre_sala'], data['edificio'])
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
@bp.route('/edificios', methods=['GET', 'OPTIONS'])
@cross_origin(
    origins=ORIGINS,
    methods=['GET', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Authorization'],
)
def listar_edificios():
    try:
        #Listamos todos los edificios donde estan las salas
        rows = fetch_query("""
            SELECT nombre_edificio
            FROM edificio
            ORDER BY nombre_edificio
        """)
        return jsonify({
            'success': True,
            'data': rows
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500