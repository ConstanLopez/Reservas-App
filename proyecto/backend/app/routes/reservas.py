from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import token_required
from app.models.reserva import Reserva
from app.models.sala import Sala
from app.models.turno import Turno
from datetime import datetime

bp = Blueprint('reservas', __name__, url_prefix='/api/reservas')

@bp.get('/mis-reservas')
@token_required
def get_mis_reservas(current_user):
    """Obtiene todas las reservas del usuario autenticado"""
    try:
        ci = current_user['ci']
        incluir_canceladas = request.args.get('incluir_canceladas', 'false').lower() == 'true'
        
        reservas = Reserva.get_by_participante(ci, incluir_canceladas)
        
        return jsonify({
            'success': True,
            'data': reservas,
            'count': len(reservas)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/activas')
@token_required
def get_reservas_activas(current_user):
    """Obtiene reservas activas futuras del usuario"""
    try:
        ci = current_user['ci']
        reservas = Reserva.get_activas_futuras(ci)
        
        return jsonify({
            'success': True,
            'data': reservas,
            'count': len(reservas)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/<int:id_reserva>')
@token_required
def get_reserva_detalle(current_user, id_reserva):
    """Obtiene el detalle de una reserva específica"""
    try:
        reserva = Reserva.get_by_id(id_reserva)
        
        if not reserva:
            return jsonify({'success': False, 'message': 'Reserva no encontrada'}), 404
        
        # Verificar que la reserva pertenezca al usuario
        if reserva['ci_participante'] != current_user['ci']:
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        
        return jsonify({
            'success': True,
            'data': reserva
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.post('')
@token_required
def crear_reserva(current_user):
    """Crea una nueva reserva"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['nombre_sala', 'edificio', 'fecha', 'id_turno']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False, 
                    'message': f'Campo requerido: {field}'
                }), 400
        
        nombre_sala = data['nombre_sala']
        edificio = data['edificio']
        fecha_str = data['fecha']
        id_turno = data['id_turno']
        ci = current_user['ci']
        
        # Validar formato de fecha
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False, 
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        # Validar que la fecha no sea pasada
        if fecha < datetime.now().date():
            return jsonify({
                'success': False, 
                'message': 'No se pueden crear reservas para fechas pasadas'
            }), 400
        
        # Crear la reserva
        id_reserva, mensaje = Reserva.crear(nombre_sala, edificio, fecha, id_turno, ci)
        
        if id_reserva:
            reserva = Reserva.get_by_id(id_reserva)
            return jsonify({
                'success': True,
                'message': mensaje,
                'data': reserva
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.delete('/<int:id_reserva>')
@token_required
def cancelar_reserva(current_user, id_reserva):
    """Cancela una reserva"""
    try:
        ci = current_user['ci']
        success, mensaje = Reserva.cancelar(id_reserva, ci)
        
        if success:
            return jsonify({
                'success': True,
                'message': mensaje
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500