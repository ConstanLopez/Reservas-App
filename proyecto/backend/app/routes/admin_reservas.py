from flask import Blueprint, jsonify, request
from app.models.reserva import Reserva
from app.middleware.auth_middleware import admin_required

bp = Blueprint('admin_reservas', __name__, url_prefix='/api/admin/reservas')


@bp.get('/')
@admin_required
def listar_reservas(current_user):
    try:
        #Listamos todas las reservas
        reservas = Reserva.get_all()  # método nuevo
        return jsonify({'success': True, 'data': reservas}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.put('/<int:id_reserva>')
@admin_required
def actualizar_reserva(current_user, id_reserva):
    try:
        data = request.get_json()
        #Actualizamos la reserva
        ok, msg = Reserva.actualizar_por_admin(id_reserva, data)
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.delete('/<int:id_reserva>')
@admin_required
def eliminar_reserva(current_user, id_reserva):
    try:
        #Eliminamos la reserva
        ok, msg = Reserva.eliminar_por_admin(id_reserva)
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
