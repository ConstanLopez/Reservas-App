from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

bp = Blueprint("participantes", __name__, url_prefix="/api/participantes")

@bp.route("/auth/register", methods=["POST","OPTIONS"])
@cross_origin(
    origins=["http://localhost:5173","http://127.0.0.1:5173"],
    methods=["POST","OPTIONS"],
    allow_headers=["Content-Type","Authorization"],
    expose_headers=["Authorization"]
)
def register():
    if request.method == "OPTIONS":
        return ("", 204)  # responde OK al preflight

    data = request.get_json(silent=True) or {}
    if not {"email","password"}.issubset(data):
        return jsonify({"error":"Faltan campos"}), 400
    return jsonify({"message":"Usuario creado"}), 201