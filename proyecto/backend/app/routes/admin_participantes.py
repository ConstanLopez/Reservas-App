from flask import Blueprint, request, jsonify
from app.middleware.auth_middleware import admin_required
from app.models.participante import Participante
from app.models.sala import Sala
from flask_cors import cross_origin

bp = Blueprint('admin_participantes', __name__, url_prefix='/api/admin/participantes')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
# ABM Particpantes

@bp.route('/', methods=['GET', 'OPTIONS'])
@cross_origin(
    origins=ORIGINS,
    methods=['GET', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization'],
    expose_headers=['Authorization'],
)
@admin_required
def listar_participantes(current_user):
    # Preflight: solo devolvemos 204 sin nada, nos ataja errores
    if request.method == 'OPTIONS':
        return ('', 204)

    try:
        # Obtenemos todos los participantes
        participantes = Participante.get_all()  
        return jsonify({'success': True, 'data': participantes}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
# POST: crear participante (solo admin)
@bp.post('/')
@admin_required
def crear_participante(current_user):
    try:
        data = request.get_json()
        # Creamos el participante
        nuevo_id, msg = Participante.crear_por_admin(data)
        if not nuevo_id:
            return jsonify({'success': False, 'message': msg}), 400
        return jsonify({'success': True, 'message': msg}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.put('/<ci>')
@admin_required
def actualizar_participante(current_user, ci):
    try:
        data = request.get_json()
        #Actualizamos el participante
        ok, msg = Participante.actualizar_por_admin(ci, data)
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.delete('/<ci>')
@admin_required
def eliminar_participante(current_user, ci):
    try:
        #Eliminamos el participante
        ok, msg = Participante.eliminar_por_admin(ci)
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500