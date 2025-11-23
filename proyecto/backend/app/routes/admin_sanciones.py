from flask import Blueprint, jsonify, request
from app.models.participante import Participante
from app.middleware.auth_middleware import admin_required
from app.database import fetch_query, execute_query
from flask_cors import cross_origin

bp = Blueprint('admin_sanciones', __name__, url_prefix='/api/admin/sanciones')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

@bp.route('/', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET','OPTIONS'],
              allow_headers=['Content-Type','Authorization'],
              expose_headers=['Authorization'])
@admin_required
def listar_sanciones(current_user):
    #Nos muestra todas las sanciones de los participantes
    if request.method == 'OPTIONS':
        return ('', 204)
    try:
        query = """
            SELECT s.ci_participante, p.nombre, p.apellido,
                   DATE_FORMAT(s.fecha_inicio, '%Y-%m-%d') as fecha_inicio,
                   DATE_FORMAT(s.fecha_fin, '%Y-%m-%d') as fecha_fin
            FROM sancion_participante s
            JOIN participante p ON s.ci_participante = p.ci
            ORDER BY s.fecha_inicio DESC
        """
        todas = fetch_query(query)
        
        # Eliminar duplicados
        vistas = set()
        unicas = []
        for sancion in todas:
            clave = (sancion['ci_participante'], sancion['fecha_inicio'], sancion['fecha_fin'])
            if clave not in vistas:
                vistas.add(clave)
                unicas.append(sancion)
        
        return jsonify({'success': True, 'data': unicas}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.post('/')
@admin_required
def crear_sancion(current_user):
    #Creamos una nueva sanción para un participante
    try:
        data = request.get_json()
        required = ['ci_participante', 'fecha_inicio', 'fecha_fin']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400

        query = """
            INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s)
        """
        ok = execute_query(query, (data['ci_participante'], data['fecha_inicio'], data['fecha_fin']))
        return jsonify({'success': ok, 'message': 'Sanción creada exitosamente'}), 201 if ok else 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.put('/')
@admin_required
def actualizar_sancion(current_user):
    #Actualizamos una sanción existente
    try:
        data = request.get_json()
        print(f"[UPDATE SANCION] Data recibida: {data}")
        required = ['ci_participante', 'fecha_inicio', 'fecha_fin']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400

        ci_old = data.get('ci_participante_old', data['ci_participante'])
        fecha_inicio_old = data.get('fecha_inicio_old', data['fecha_inicio'])
        fecha_fin_old = data.get('fecha_fin_old', data['fecha_fin'])

        print(f"[UPDATE SANCION] Valores OLD: ci={ci_old}, inicio={fecha_inicio_old}, fin={fecha_fin_old}")
        print(f"[UPDATE SANCION] Valores NEW: ci={data['ci_participante']}, inicio={data['fecha_inicio']}, fin={data['fecha_fin']}")

        delete_query = """
            DELETE FROM sancion_participante
            WHERE ci_participante = %s
            AND DATE(fecha_inicio) = DATE(%s)
            AND DATE(fecha_fin) = DATE(%s)
        """
        ok_delete = execute_query(delete_query, (ci_old, fecha_inicio_old, fecha_fin_old))
        print(f"[UPDATE SANCION] Delete resultado: {ok_delete}")

        insert_query = """
            INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s)
        """
        ok = execute_query(insert_query, (data['ci_participante'], data['fecha_inicio'], data['fecha_fin']))
        print(f"[UPDATE SANCION] Insert resultado: {ok}")
        return jsonify({'success': ok, 'message': 'Sanción actualizada'}), 200 if ok else 400
    except Exception as e:
        print(f"[UPDATE SANCION] Exception: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.delete('/')
@admin_required
def eliminar_sancion(current_user):
    #Eliminamos una sanción existente
    try:
        data = request.get_json()
        print(f"[DELETE SANCION] Data recibida: {data}")
        required = ['ci_participante', 'fecha_inicio', 'fecha_fin']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Falta campo: {field}'}), 400

        query = """
            DELETE FROM sancion_participante
            WHERE ci_participante = %s
            AND DATE(fecha_inicio) = DATE(%s)
            AND DATE(fecha_fin) = DATE(%s)
        """
        print(f"[DELETE SANCION] Ejecutando query con: ci={data['ci_participante']}, inicio={data['fecha_inicio']}, fin={data['fecha_fin']}")
        ok = execute_query(query, (data['ci_participante'], data['fecha_inicio'], data['fecha_fin']))
        print(f"[DELETE SANCION] Resultado: {ok}")
        return jsonify({'success': ok, 'message': 'Sanción eliminada' if ok else 'Error al eliminar'}), 200 if ok else 400
    except Exception as e:
        print(f"[DELETE SANCION] Exception: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
