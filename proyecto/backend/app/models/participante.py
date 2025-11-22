from app.database import fetch_query, execute_query

class Participante:

    @staticmethod
    def get_by_email(email):
        """Obtiene participante por email CON rol académico"""
        query = """
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT ppa.rol_academico) as roles_academicos,
                   GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            WHERE p.email = %s
            GROUP BY p.ci
        """
        rows = fetch_query(query, (email,))
        if rows:
            participante = rows[0]
            participante['roles_academicos'] = participante['roles_academicos'].split(',') if participante['roles_academicos'] else []
            participante['programas'] = participante['programas'].split(',') if participante['programas'] else []
            return participante
        return None
    

    @staticmethod
    def get_by_ci(ci):
        """Obtiene participante por CI CON rol académico"""
        query = """
            SELECT p.*, 
                   GROUP_CONCAT(DISTINCT ppa.rol_academico) as roles_academicos,
                   GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            WHERE p.ci = %s
            GROUP BY p.ci
        """
        rows = fetch_query(query, (ci,))
        if rows:
            participante = rows[0]
            participante['roles_academicos'] = participante['roles_academicos'].split(',') if participante['roles_academicos'] else []
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
        """Verifica si el participante es docente (ROL ACADÉMICO)"""
        query = """
            SELECT COUNT(*) as count FROM participante_programa_academico
            WHERE ci_participante = %s AND rol_academico = 'docente'
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
            WHERE ppa.ci_participante = %s AND pa.tipo = 'posgrado' AND ppa.rol_academico = 'alumno'
        """
        rows = fetch_query(query, (ci,))
        return rows[0]['count'] > 0 if rows else False


    @staticmethod
    def crear_por_admin(data):
        """
        Crear participante desde panel admin.
        data debe contener:
        - ci, nombre, apellido, email, rol_sistema, password (opcional)
        - nombre_programa, rol_academico (para asociar a programa)
        """
        try:
            # 1. Crear participante con ROL DEL SISTEMA
            query = """
                INSERT INTO participante (ci, nombre, apellido, email, rol_sistema)
                VALUES (%s, %s, %s, %s, %s)
            """
            execute_query(query, (
                data['ci'],
                data['nombre'],
                data['apellido'],
                data['email'],
                data.get('rol_sistema', 'usuario')  # Por defecto 'usuario'
            ))

            # 2. Crear login si mandaron password
            if data.get("password"):
                from app.utils.auth_utils import hash_password
                password_hash = hash_password(data["password"])
                execute_query(
                    "INSERT INTO login (correo, contrasena) VALUES (%s, %s)",
                    (data["email"], password_hash)
                )

            # 3. Asignar programa académico con ROL ACADÉMICO
            if data.get("nombre_programa") and data.get("rol_academico"):
                execute_query(
                    """INSERT INTO participante_programa_academico 
                       (ci_participante, nombre_programa, rol_academico) 
                       VALUES (%s, %s, %s)""",
                    (data['ci'], data['nombre_programa'], data['rol_academico'])
                )

            return True, "Participante creado exitosamente"

        except Exception as e:
            print(f"Error en crear_por_admin: {e}")
            return None, str(e)


    @staticmethod
    def actualizar_por_admin(ci, data):
        """
        Actualizar participante desde panel admin.
        Puede actualizar:
        - Datos personales: nombre, apellido, email, rol_sistema
        - Login (si cambia el email o password)
        - Programa académico / rol académico
        """
        try:
            # 1. Obtener datos actuales (incluye email)
            participante_actual = fetch_query(
                "SELECT * FROM participante WHERE ci = %s", (ci,)
            )
            if not participante_actual:
                return False, "Participante no encontrado"

            email_actual = participante_actual[0]["email"]

            # ---------------------------------------------------------
            # 2. Actualizar datos básicos del participante
            # ---------------------------------------------------------
            valid_fields = {"nombre", "apellido", "email", "rol_sistema"}
            fields = []
            values = []

            for key, val in data.items():
                if key in valid_fields and val not in [None, ""]:
                    fields.append(f"{key} = %s")
                    values.append(val)

            if fields:
                values.append(ci)
                query = f"UPDATE participante SET {', '.join(fields)} WHERE ci = %s"
                execute_query(query, tuple(values))

            # ---------------------------------------------------------
            # 3. Si cambia el email → actualizar tabla login también
            # ---------------------------------------------------------
            if "email" in data and data["email"] and data["email"] != email_actual:
                nuevo_email = data["email"]

                # Actualizar correo en tabla login
                execute_query(
                    "UPDATE login SET correo = %s WHERE correo = %s",
                    (nuevo_email, email_actual)
                )

                email_actual = nuevo_email  # actualizar referencia

            # ---------------------------------------------------------
            # 4. Actualizar password si viene
            # ---------------------------------------------------------
            if data.get("password"):
                from app.utils.auth_utils import hash_password
                hashed = hash_password(data["password"])
                execute_query(
                    "UPDATE login SET contrasena = %s WHERE correo = %s",
                    (hashed, email_actual)
                )

            # ---------------------------------------------------------
            # 5. Actualizar programa académico y rol académico
            # ---------------------------------------------------------
            if data.get("nombre_programa") or data.get("rol_academico"):

                nombre_programa = data.get("nombre_programa")
                rol_academico = data.get("rol_academico")

                # ¿Ya tiene un programa asignado?
                existing = fetch_query(
                    "SELECT * FROM participante_programa_academico WHERE ci_participante = %s",
                    (ci,)
                )

                if existing:
                    # Ya existe → actualizar
                    update_fields = []
                    values = []

                    if nombre_programa:
                        update_fields.append("nombre_programa = %s")
                        values.append(nombre_programa)

                    if rol_academico:
                        update_fields.append("rol_academico = %s")
                        values.append(rol_academico)

                    if update_fields:
                        values.append(ci)
                        query = f"""
                            UPDATE participante_programa_academico
                            SET {', '.join(update_fields)}
                            WHERE ci_participante = %s
                        """
                        execute_query(query, tuple(values))

                else:
                    # No existe → insertar si hay ROL ACADÉMICO Y PROGRAMA
                    if nombre_programa and rol_academico:
                        execute_query(
                            """INSERT INTO participante_programa_academico
                            (ci_participante, nombre_programa, rol_academico)
                            VALUES (%s, %s, %s)""",
                            (ci, nombre_programa, rol_academico)
                        )

            return True, "Participante actualizado correctamente"

        except Exception as e:
            print(f"Error en actualizar_por_admin: {e}")
            return False, str(e)



    @staticmethod
    def eliminar_por_admin(ci):
        """Elimina participante y todo lo relacionado (CASCADE se encarga)"""
        try:
            # Obtener email antes de eliminar
            p = Participante.get_by_ci(ci)
            if p:
                # Eliminar login (el CASCADE eliminará el participante)
                execute_query("DELETE FROM login WHERE correo = %s", (p['email'],))
                return True, "Participante eliminado correctamente"
            else:
                return False, "Participante no encontrado"

        except Exception as e:
            print(f"Error en eliminar_por_admin: {e}")
            return False, str(e)


    @staticmethod
    def get_all():
        """
        Lista todos los participantes con:
        - Datos personales
        - Rol del sistema (admin/usuario)
        - Rol académico (alumno/docente) si tiene
        """
        query = """
            SELECT DISTINCT
                p.ci, 
                p.nombre, 
                p.apellido, 
                p.email, 
                p.rol_sistema,
                ppa.rol_academico,
                ppa.nombre_programa
            FROM participante p
            LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
            ORDER BY p.ci
        """
        return fetch_query(query)