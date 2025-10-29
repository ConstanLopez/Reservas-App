from flask import Flask, jsonify, request
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # CORS para dev (Vite en 5173)
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
        methods=["GET","POST","PUT","DELETE","OPTIONS"],
        allow_headers=["Content-Type","Authorization"],
        expose_headers=["Authorization"]
    )

    # Garantizar CORS también en respuestas de error
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

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # Registrar blueprints
    from .routes import auth, reservas, salas, turnos
    app.register_blueprint(auth.bp)
    app.register_blueprint(reservas.bp)
    app.register_blueprint(salas.bp)
    app.register_blueprint(turnos.bp)

    @app.get("/api/_routes")
    def routes():
        return jsonify(sorted([str(r) for r in app.url_map.iter_rules()]))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)