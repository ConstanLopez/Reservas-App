from flask import Blueprint, jsonify, request
from app.middleware.auth_middleware import token_required
from app.models.reserva import Reserva
from app.models.sala import Sala
from app.models.turno import Turno
from app.models.participante import Participante
from datetime import datetime

#Definimos el conjunto de rutas agrupadas para las rutas de reservas 
bp = Blueprint('reservas', __name__, url_prefix='/api/reservas')

@bp.get('/mis-reservas')
@token_required
def get_mis_reservas(current_user):
    """Obtiene todas las reservas del usuario autenticado según su cédula"""
    try:
        ci = current_user['ci'] #Se extrae la cédula
        incluir_canceladas = request.args.get('incluir_canceladas', 'false').lower() == 'true' #incuye reservas canceladas
        
        reservas = Reserva.get_by_participante(ci, incluir_canceladas) #Llamamos al método para obtener las reservas de cada participante segun su CI
        
        for r in reservas:
            r['participantes'] = Reserva.get_participantes_de_reserva(r['id_reserva'])

        return jsonify({ #Devolvemos un JSON
            'success': True, 
            'data': reservas,
            'count': len(reservas) #Cuenta la cantidad total de reservas
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.get('/activas')
@token_required
def get_reservas_activas(current_user):
    """Obtiene reservas activas futuras del usuario"""
    try:
        ci = current_user['ci']
        reservas = Reserva.get_activas_futuras(ci) #Filtra las reservas por ci
        
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
        reserva = Reserva.get_by_id(id_reserva) #Obtiene una reserva por si id en especifico
        
        if not reserva: #si el id de la reserva  no existe
            return jsonify({'success': False, 'message': 'Reserva no encontrada'}), 404
        
        # Verificar que la reserva pertenezca al usuario y no a usuarios ajenos
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
        data = request.get_json() #recibimos el json de la request
        # Validar campos requeridos
        required_fields = ['nombre_sala', 'edificio', 'fecha', 'id_turno']
        for field in required_fields:
            if field not in data: #si falta algun campo requerido
                return jsonify({
                    'success': False, 
                    'message': f'Campo requerido: {field}'
                }), 400
        #extraemos los campos 
        nombre_sala = data['nombre_sala']
        edificio = data['edificio']
        fecha_str = data['fecha']
        id_turno = data['id_turno']
        ci = current_user['ci']
        participantes = data.get('participantes', [])
        hora_inicio_rango = data.get('hora_inicio_rango')
        hora_fin_rango = data.get('hora_fin_rango')
        if participantes is None:
            participantes = []
        
        
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
        id_reserva, mensaje = Reserva.crear(nombre_sala, edificio, fecha, id_turno, ci,participantes,hora_inicio_rango, hora_fin_rango)
        
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
        success, mensaje = Reserva.cancelar(id_reserva, ci) # verifica si la reserva pertenece al usuario , si esta activa, actualiza el estado
        
        if success: # se cancelo la reserva correctamente
            return jsonify({
                'success': True,
                'message': mensaje
            }), 200
        else: # no se pudo cancelar la reserva
            return jsonify({
                'success': False,
                'message': mensaje
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500