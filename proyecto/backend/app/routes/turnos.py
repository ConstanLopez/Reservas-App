from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import token_required
from app.models.turno import Turno
from datetime import datetime

bp = Blueprint('turnos', __name__, url_prefix='/api/turnos')

@bp.get('')
@token_required
def get_turnos(current_user):
    """Obtiene todos los turnos disponibles"""
    try:
        turnos = Turno.get_all()
        return jsonify({
            'success': True,
            'data': turnos,
            'count': len(turnos)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/<int:id_turno>')
@token_required
def get_turno_detalle(current_user, id_turno):
    """Obtiene el detalle de un turno específico"""
    try:
        turno = Turno.get_by_id(id_turno)
        
        if not turno:
            return jsonify({'success': False, 'message': 'Turno no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': turno
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/disponibles')
@token_required
def get_turnos_disponibles(current_user):
    """
    Obtiene turnos disponibles para una sala y fecha específicas
    Query params: fecha (YYYY-MM-DD), nombre_sala, edificio
    """
    try:
        fecha_str = request.args.get('fecha')
        nombre_sala = request.args.get('nombre_sala')
        edificio = request.args.get('edificio')
        
        if not all([fecha_str, nombre_sala, edificio]):
            return jsonify({
                'success': False,
                'message': 'Se requieren los parámetros: fecha, nombre_sala y edificio'
            }), 400
        
        # Validar formato de fecha
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        turnos = Turno.get_disponibles_para_sala(fecha, nombre_sala, edificio)
        
        return jsonify({
            'success': True,
            'data': turnos,
            'count': len(turnos)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500