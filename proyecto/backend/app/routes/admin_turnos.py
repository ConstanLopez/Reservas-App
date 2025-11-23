from flask import Blueprint, jsonify, request
from app.models.turno import Turno
from app.middleware.auth_middleware import admin_required
from flask_cors import cross_origin

bp = Blueprint('admin_turnos', __name__, url_prefix='/api/admin/turnos')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

@bp.route('/', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET', 'OPTIONS'],
              allow_headers=['Content-Type', 'Authorization'],
              expose_headers=['Authorization'])
@admin_required
def listar_turnos(current_user):
    #Listamos todos los turnos disponibles
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        turnos = Turno.get_all()
        return jsonify({'success': True, 'data': turnos}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.post('/')
@admin_required
def crear_turno(current_user):
    #Creamos un nuevo turno
    try:
        data = request.get_json()
        required = ['hora_inicio', 'hora_fin']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400

        ok, msg = Turno.crear(data['hora_inicio'], data['hora_fin'])
        status = 201 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.put('/<int:id_turno>')
@admin_required
def actualizar_turno(current_user, id_turno):
    #Actualizamos un turno existente
    try:
        data = request.get_json()
        required = ['hora_inicio', 'hora_fin']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400

        ok, msg = Turno.actualizar(id_turno, data['hora_inicio'], data['hora_fin'])
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.delete('/<int:id_turno>')
@admin_required
def eliminar_turno(current_user, id_turno):
    #Eliminamos un turno existente
    try:
        ok, msg = Turno.eliminar(id_turno)
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
