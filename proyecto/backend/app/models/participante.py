from app.database import fetch_query,execute_query

class Participante:
    @staticmethod
    def get_by_email(email):
        """Obtiene participante por email"""
        query = """
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT ppa.rol) as roles,
                   GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            WHERE p.email = %s
            GROUP BY p.ci
        """
        rows = fetch_query(query, (email,))
        if rows:
            participante = rows[0]
            # Convertir roles y programas en listas
            participante['roles'] = participante['roles'].split(',') if participante['roles'] else []
            participante['programas'] = participante['programas'].split(',') if participante['programas'] else []
            return participante
        return None
    
    @staticmethod
    def get_by_ci(ci):
        """Obtiene participante por CI"""
        query = """
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT ppa.rol) as roles,
                   GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            WHERE p.ci = %s
            GROUP BY p.ci
        """
        rows = fetch_query(query, (ci,))
        if rows:
            participante = rows[0]
            participante['roles'] = participante['roles'].split(',') if participante['roles'] else []
            participante['programas'] = participante['programas'].split(',') if participante['programas'] else []
            return participante
        return None
    
    @staticmethod
    def tiene_sancion_activa(ci):
        """Verifica si el participante tiene una sanción activa"""
        query = """
            SELECT * FROM sancion_participante
            WHERE ci_participante = %s
            AND CURDATE() BETWEEN fecha_inicio AND fecha_fin
        """
        rows = fetch_query(query, (ci,))
        return len(rows) > 0

    @staticmethod
    def get_sancion_activa(ci):
        """Obtiene la sanción activa del participante"""
        query = """
            SELECT * FROM sancion_participante
            WHERE ci_participante = %s
            AND CURDATE() BETWEEN fecha_inicio AND fecha_fin
            ORDER BY fecha_fin DESC
            LIMIT 1
        """
        rows = fetch_query(query, (ci,))
        return rows[0] if rows else None
    
    @staticmethod
    def es_docente(ci):
        """Verifica si el participante es docente"""
        query = """
            SELECT COUNT(*) as count FROM participante_programa_academico
            WHERE ci_participante = %s AND rol = 'docente'
        """
        rows = fetch_query(query, (ci,))
        return rows[0]['count'] > 0 if rows else False
    
    @staticmethod
    def es_posgrado(ci):
        """Verifica si el participante es de posgrado"""
        query = """
            SELECT COUNT(*) as count 
            FROM participante_programa_academico ppa
            JOIN programa_academico pa ON ppa.nombre_programa = pa.nombre_programa
            WHERE ppa.ci_participante = %s AND pa.tipo = 'posgrado' AND ppa.rol = 'alumno'
        """
        rows = fetch_query(query, (ci,))
        return rows[0]['count'] > 0 if rows else False

    
    @staticmethod
    def crear_por_admin(data):
        try:
            query = """INSERT INTO participante (ci, nombre, apellido, email, rol, password_hash)
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            execute_query(query, (data['ci'], data['nombre'], data['apellido'],
                                data['email'], data['rol'], data['password_hash'])) 
            return True, "Participante creado exitosamente"
        except Exception as e:
            return None, str(e)

    @staticmethod
    def actualizar_por_admin(ci, data):
        try:
            fields = []
            values = []
            for key, val in data.items():
                # No actualizar la PK ni campos vacíos/None (excepto password que puede estar vacío)
                if key != 'ci' and val not in [None, ''] or key == 'password':
                    if key == 'password' and val == '':
                        continue  # Skip password vacío
                    fields.append(f"{key} = %s")
                    values.append(val)
            if not fields:
                return True, "No hay campos para actualizar"
            values.append(ci)
            query = f"UPDATE participante SET {', '.join(fields)} WHERE ci = %s"
            ok = execute_query(query, tuple(values))
            return ok, "Participante actualizado correctamente" if ok else "Error al actualizar"
        except Exception as e:
            return False, f"Error al actualizar participante: {str(e)}"

    @staticmethod
    def eliminar_por_admin(ci):
        """Elimina un participante y todas sus relaciones (CASCADE manual)"""
        try:
            # Eliminar en orden por las foreign keys
            # 1. Eliminar sanciones
            execute_query("DELETE FROM sancion_participante WHERE ci_participante = %s", (ci,))

            # 2. Eliminar participaciones en reservas
            execute_query("DELETE FROM reserva_participante WHERE ci_participante = %s", (ci,))

            # 3. Eliminar relaciones con programas académicos
            execute_query("DELETE FROM participante_programa_academico WHERE ci_participante = %s", (ci,))

            # 4. Obtener el email para eliminar el login
            participante = Participante.get_by_ci(ci)
            if participante:
                email = participante['email']
                execute_query("DELETE FROM login WHERE correo = %s", (email,))

            # 5. Finalmente eliminar el participante
            ok = execute_query("DELETE FROM participante WHERE ci = %s", (ci,))
            return ok, "Participante eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar participante: {str(e)}"
    
    @staticmethod
    def get_all():
        query = """
            SELECT p.ci, p.nombre, p.apellido, p.email, p.rol,
                   GROUP_CONCAT(DISTINCT ppa.rol) as roles,
                   GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            GROUP BY p.ci
        """
        rows = fetch_query(query)
        for participante in rows:
            participante['roles'] = participante['roles'].split(',') if participante['roles'] else []
            participante['programas'] = participante['programas'].split(',') if participante['programas'] else []
        return rows
    
    