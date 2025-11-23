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
        - ci, nombre, apellido, email, rol_sistema, password (obligatorio para alta)
        - nombre_programa, rol_academico (para asociar a programa, opcional)
        """
        try:
            ci = data["ci"]
            nombre = data["nombre"]
            apellido = data["apellido"]
            email = data["email"]
            rol_sistema = data.get("rol_sistema", "usuario")
            password = data.get("password")

            # 🔐 0. Para un alta nueva, exigimos password
            if not password:
                return None, "Para crear un nuevo participante es necesario indicar un password."

            # 1️⃣ Crear LOGIN primero (por el FK participante.email → login.correo)
            from app.utils.auth_utils import hash_password
            password_hash = hash_password(password)

            ok_login = execute_query(
                "INSERT INTO login (correo, contrasena) VALUES (%s, %s)",
                (email, password_hash)
            )
            if not ok_login:
                return None, "No se pudo crear el login (correo duplicado u otro error en BD)."

            # 2️⃣ Crear PARTICIPANTE
            ok_participante = execute_query(
                """
                INSERT INTO participante (ci, nombre, apellido, email, rol_sistema)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (ci, nombre, apellido, email, rol_sistema)
            )
            if not ok_participante:
                # rollback mínimo: si no pude crear el participante, borro el login recién creado
                execute_query("DELETE FROM login WHERE correo = %s", (email,))
                return None, "No se pudo crear el participante (CI duplicada u otro error en BD)."

            # 3️⃣ Asignar PROGRAMA ACADÉMICO (opcional)
            nombre_programa = data.get("nombre_programa")
            rol_academico = data.get("rol_academico")

            if nombre_programa and rol_academico:
                ok_prog = execute_query(
                    """
                    INSERT INTO participante_programa_academico
                        (ci_participante, nombre_programa, rol_academico)
                    VALUES (%s, %s, %s)
                    """,
                    (ci, nombre_programa, rol_academico)
                )
                if not ok_prog:
                    # Podés decidir si devolvés warning o error. Yo devuelvo error “suave”.
                    return None, (
                        "El participante se creó, pero hubo un error al asociarlo al programa académico."
                    )

            return True, "Participante creado exitosamente"

        except Exception as e:
            print(f"Error en crear_por_admin: {e}")
            return None, str(e)



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
    def actualizar_por_admin(ci, data):
        """
        Actualiza un participante desde el panel admin.

        Puede actualizar:
        - nombre, apellido, email, rol_sistema
        - password (opcional)
        - nombre_programa + rol_academico (tabla participante_programa_academico)

        NOTA: el CI no se cambia (en el front lo tenés readOnlyInEdit).
        """
        try:
            # 0️⃣ Traer datos actuales
            actual = Participante.get_by_ci(ci)
            if not actual:
                return False, "Participante no encontrado"

            nombre_nuevo = data.get("nombre", actual["nombre"])
            apellido_nuevo = data.get("apellido", actual["apellido"])
            email_nuevo = data.get("email", actual["email"])
            rol_sistema_nuevo = data.get("rol_sistema", actual["rol_sistema"])
            password_nuevo = data.get("password")  # puede venir vacío

            # 1️⃣ Si cambió el email, hay que mantener la integridad con login
            email_viejo = actual["email"]

            if email_nuevo != email_viejo:
                # Tomamos el hash de la contraseña actual
                filas_login = fetch_query(
                    "SELECT contrasena FROM login WHERE correo = %s",
                    (email_viejo,)
                )
                if not filas_login:
                    return False, "No se encontró el login asociado al participante"

                hash_actual = filas_login[0]["contrasena"]

                # Creamos login nuevo con el mismo hash
                ok = execute_query(
                    "INSERT INTO login (correo, contrasena) VALUES (%s, %s)",
                    (email_nuevo, hash_actual)
                )
                if not ok:
                    return False, "No se pudo crear el nuevo login (correo ya usado?)"

                # Actualizamos participante para que apunte al nuevo correo
                ok = execute_query(
                    "UPDATE participante SET email = %s WHERE ci = %s",
                    (email_nuevo, ci)
                )
                if not ok:
                    return False, "No se pudo actualizar el email del participante"

                # Borramos el login viejo (ya nadie lo referencia)
                execute_query(
                    "DELETE FROM login WHERE correo = %s",
                    (email_viejo,)
                )

            # 2️⃣ Actualizar nombre, apellido y rol_sistema
            ok = execute_query(
                """
                UPDATE participante
                SET nombre = %s,
                    apellido = %s,
                    rol_sistema = %s
                WHERE ci = %s
                """,
                (nombre_nuevo, apellido_nuevo, rol_sistema_nuevo, ci)
            )
            if not ok:
                return False, "No se pudieron actualizar los datos básicos del participante"

            # 3️⃣ Si vino un password nuevo, actualizarlo en login
            if password_nuevo:
                from app.utils.auth_utils import hash_password
                nuevo_hash = hash_password(password_nuevo)
                execute_query(
                    "UPDATE login SET contrasena = %s WHERE correo = %s",
                    (nuevo_hash, email_nuevo)
                )

            # 4️⃣ Actualizar programa académico / rol_acad (si se mandan)
            nombre_programa = data.get("nombre_programa")
            rol_academico = data.get("rol_academico")

            if nombre_programa and rol_academico:
                # ¿Ya tiene fila en participante_programa_academico?
                filas_prog = fetch_query(
                    """
                    SELECT id_alumno_programa
                    FROM participante_programa_academico
                    WHERE ci_participante = %s
                    """,
                    (ci,)
                )

                if filas_prog:
                    # Actualizamos la fila existente
                    execute_query(
                        """
                        UPDATE participante_programa_academico
                        SET nombre_programa = %s,
                            rol_academico = %s
                        WHERE ci_participante = %s
                        """,
                        (nombre_programa, rol_academico, ci)
                    )
                else:
                    # No tenía programa → insert
                    execute_query(
                        """
                        INSERT INTO participante_programa_academico
                            (ci_participante, nombre_programa, rol_academico)
                        VALUES (%s, %s, %s)
                        """,
                        (ci, nombre_programa, rol_academico)
                    )

            return True, "Participante actualizado correctamente"

        except Exception as e:
            print(f"Error en actualizar_por_admin: {e}")
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
