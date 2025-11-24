Para iniciar el proyecto:

# Requisitos:
-Tener Docker Desktop
# -Dependencias Backend:
  ¿Cómo instalarlas?
    Dentro de la carpeta backend, ejecutar en la consola : pip install -r requirements.txt

# -Dependencias Frontend
   ¿Cómo instalarlas?
    Dentro de la carpeta frontend, ejecutar en la consola : npm install

 # ¿Como levantar el compose de Docker para la db?
 Ejecutar en la consola el comando: docker-compose -f "docker-compose APP.yml" up

# ¿Como correr el programa?
Ejecutar el backend: Desde la carpeta backend ejecutar el comando python -m app.main en la consola
Ejecutar el frontend: Desde la carpeta frontend ejecutar el comando npm run dev en la consola

# ¿Cómo conectar la bd para verla en dataGrip?
Usar los siguentes campos:
host: localhost
port: 3307
user:appuser
password:apppass
db name: reservas_db

# ¿Como usar el software?

Usuario Normal (No admin):
-Puede crear y ver sus reservas, si se quiere realizar una reserva en un horario que es más de un bloque de hora ej; (10:30-12:00) se debe tocar el seleccionar bloques automaticamente.

Usuario admin (En la db se proporciona uno, con la password 123456 y el mail correspondiente (el password se ve hasheado, por eso la aclaracion )
-Puede hacer ABM de participantes, salas , turnos, sanciones y reservas. En la parte superior derecha, esta la pestaña para acceder al BI

# -Restricciones de uso:
-Se usa un JWT de una hora, por lo tanto a partir de esa hora, es necesario volver a iniciar sesion, ya que no se va a poder realizar acciones.
