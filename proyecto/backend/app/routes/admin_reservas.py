from flask import Blueprint, jsonify, request
from app.models.reserva import Reserva
from app.middleware.auth_middleware import admin_required

bp = Blueprint('admin_reservas', __name__, url_prefix='/api/admin/reservas')

# GET: listar todas las reservas
@bp.get('/')
@admin_required
def listar_reservas(current_user):
    try:
        reservas = Reserva.get_all()  # método nuevo
        return jsonify({'success': True, 'data': reservas}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# PUT: modificar reserva (fecha, turno o estado)
# Permite al admin cambiar datos de una reserva existente
@bp.put('/<int:id_reserva>')
@admin_required
def actualizar_reserva(current_user, id_reserva):
    try:
        data = request.get_json()
        ok, msg = Reserva.actualizar_por_admin(id_reserva, data)
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# DELETE: cancelar o eliminar reserva
# Cancela/elimina una reserva identificada por su ID
@bp.delete('/<int:id_reserva>')
@admin_required
def eliminar_reserva(current_user, id_reserva):
    try:
        ok, msg = Reserva.cancelar_por_admin(id_reserva)
        status = 200 if ok else 400
        return jsonify({'success': ok, 'message': msg}), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
