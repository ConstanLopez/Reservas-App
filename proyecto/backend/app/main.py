from flask import Flask, jsonify, request 
from flask_cors import CORS
'''
jsonify convierte el diccionario o lista de python en un JSON que es lo válido para la API
request es la solicitud HTTP actual que hizo el cliente, se usa para acceder a datos enviados por el usuario
request.json → cuerpo en JSON
request.args → parámetros de URL
request.headers → encabezados HTTP

CORS Cross-Origin Resource Sharing Es una política de seguridad del navegador: bloquea peticiones HTTP que vienen desde un origen distinto
Por esto se precisa habilitar el CORS
'''
def create_app():
    app = Flask(__name__) #instancia principal del framework Flask, nos habilita a crear  una aplicación web que puede recibir y responder peticiones HTTP (GET, POST, PUT, DELETE, etc.)
                          #el archivo name, le indica a flask donde  esta el archivo base para encontrar rutas,plantillas,etc

    # CORS para dev (Vite en 5173)
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}, #Aplica CORS solo a rutas que empiecen con /api/ y la  Lista de orígenes (dominios/puertos) autorizados.
        methods=["GET","POST","PUT","DELETE","OPTIONS"], #Métodos HTTP permitidos 
        allow_headers=["Content-Type","Authorization"], #Qué headers puede enviar el frontend.
        expose_headers=["Authorization"] # Qué headers puede leer el frontend (por ejemplo, el token JWT en “Authorization”).
    )

    '''
    Aplica la extensión Flask-CORS a la aplicación app.

    Permite que los navegadores acepten peticiones desde tu frontend en React (que corre en puerto 5173).

    Se limita a las rutas que comienzan con /api/.
    '''

    # Garantizar CORS también en respuestas de error, ya que no  agrega Headers en las respuestas de error, y por eso se ejecuta despues de cada request
    ALLOWED = {"http://localhost:5173","http://127.0.0.1:5173"}
    @app.after_request
    def add_cors_headers(resp):
        origin = request.headers.get("Origin")
        if origin in ALLOWED and resp is not None:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Access-Control-Expose-Headers"] = "Authorization"
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        return resp

    #endpoint de prueba para ver si el back esta corriendo, devuelve un JSON con el estado ok
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    '''
    Los bluePrints en Flask, son una forma modular de organizar la aplicación
    En lugar de poner todas las rutas (@app.route) en un solo archivo, 
    creás un archivo por módulo (por ejemplo routes/auth.py o routes/salas.py) y dentro de él definís rutas agrupadas a un mismo grupo.
    '''
    # Registrar blueprints
    from .routes import auth, reservas, salas, turnos, reportes
    app.register_blueprint(auth.bp)
    app.register_blueprint(reservas.bp)
    app.register_blueprint(salas.bp)
    app.register_blueprint(turnos.bp)
    app.register_blueprint(reportes.bp)  


    # Lista todas las rutas registradas en tu app (útil para debug o revisar si se registraron los endpoints correctamente).
    @app.get("/api/_routes")
    def routes():
        """Lista todas las rutas disponibles"""
        return jsonify(sorted([str(r) for r in app.url_map.iter_rules()]))
    
    

    return app

#Ejecuta la app
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)