from flask import Blueprint, jsonify, request
from app.models.participante import Participante
from app.middleware.auth_middleware import admin_required
from app.database import fetch_query, execute_query
from flask_cors import cross_origin

bp = Blueprint('admin_sanciones', __name__, url_prefix='/api/admin/sanciones')
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
# GET: todas las sanciones
@bp.route('/', methods=['GET', 'OPTIONS'])
@cross_origin(origins=ORIGINS,
              methods=['GET','OPTIONS'],
              allow_headers=['Content-Type','Authorization'],
              expose_headers=['Authorization'])
@admin_required
def listar_sanciones(current_user):
    if request.method == 'OPTIONS': #Esto lo que hace es autorizar el preflight del buscador antes de la query real, esto ya que esta el método OPTIONS del CORS
        return ('', 204) 
    query = """
        SELECT s.id_sancion, s.ci_participante, p.nombre, p.apellido,
               s.fecha_inicio, s.fecha_fin
        FROM sancion_partcipante s
        JOIN participante p ON s.ci_participante = p.ci
        ORDER BY s.fecha_inicio DESC
    """
    return jsonify({'success': True, 'data': fetch_query(query)}), 200

# GET: sanciones por participante
@bp.get('/<ci>')
@admin_required
def sanciones_por_participante(current_user, ci):
    query = """
        SELECT id_sancion, fecha_inicio, fecha_fin
        FROM sancion_participante
        WHERE ci_participante = %s
        ORDER BY fecha_inicio DESC
    """
    return jsonify({'success': True, 'data': fetch_query(query, (ci,))}), 200

# POST: crear sanción manual
@bp.post('/')
@admin_required
def crear_sancion(current_user):
    data = request.get_json()
    query = """
        INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
        VALUES (%s, %s, %s)
    """
    ok = execute_query(query, (data['ci_participante'], data['fecha_inicio'], data['fecha_fin']))
    return jsonify({'success': ok, 'message': 'Sanción creada manualmente'}), 201 if ok else 400

# DELETE: eliminar (levantar) sanción
@bp.delete('/<int:id_sancion>')
@admin_required
def eliminar_sancion(current_user, id_sancion):
    query = "DELETE FROM sancion_participante WHERE id_sancion = %s"
    ok = execute_query(query, (id_sancion,))
    return jsonify({'success': ok, 'message': 'Sanción levantada'}), 200 if ok else 40