from flask import Blueprint, jsonify, request
from app.models.sala import Sala
from app.middleware.auth_middleware import admin_required
from flask_cors import cross_origin
bp = Blueprint('admin_salas', __name__, url_prefix='/api/admin/salas')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

@bp.route('/',methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET','OPTIONS'],
              allow_headers=['Content-Type','Authorization'],
              expose_headers=['Authorization'])
def listar_salas():
    try:
        salas = Sala.get_all()
        return jsonify({'success': True, 'data': salas}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# CREAR SALA (solo admin)
@bp.post('/')
@admin_required
def crear_sala(current_user):
    try:
        data = request.get_json()
        required = ['nombre_sala', 'edificio', 'capacidad', 'tipo_sala']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400

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

# ACTUALIZAR SALA (solo admin)
@bp.put('/')
@admin_required
def actualizar_sala(current_user):
    """
    Podés identificar la sala por nombre_sala + edificio que vengan en el body.
    """
    try:
        data = request.get_json()
        required = ['nombre_sala', 'edificio', 'capacidad', 'tipo_sala']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400

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


# ELIMINAR SALA (solo admin)
@bp.delete('/')
@admin_required
def eliminar_sala(current_user):
    try:
        data = request.get_json()
        required = ['nombre_sala', 'edificio']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400

        ok, msg = Sala.eliminar(data['nombre_sala'], data['edificio'])
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500