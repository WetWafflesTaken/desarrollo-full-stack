import json
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
FILE = "usuarios.json"

def leer_usuarios():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_usuarios(usuarios):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=2, ensure_ascii=False)

@app.route('/register', methods=['POST'])
def register():
    usuarios = leer_usuarios()
    data = request.get_json()

    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    if any(u["email"] == data["email"] for u in usuarios):
        return jsonify({"error": "El email ya está registrado"}), 400

    nuevo_usuario = {
        "id": len(usuarios) + 1,
        "name": data["name"],
        "email": data["email"],
        "password": generate_password_hash(data["password"])  # Guardar hash
    }
    usuarios.append(nuevo_usuario)
    guardar_usuarios(usuarios)
    return jsonify({"message": "Usuario registrado correctamente"}), 201

@app.route('/login', methods=['POST'])
def login():
    usuarios = leer_usuarios()
    data = request.get_json()

    for usuario in usuarios:
        if usuario["email"] == data.get("email") and check_password_hash(usuario["password"], data.get("password", "")):
            return jsonify({"message": "Inicio de sesión exitoso", "user": usuario["name"]}), 200

    return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/users', methods=['GET'])
def get_users():
    usuarios = leer_usuarios()
    return jsonify(usuarios), 200

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    usuarios = leer_usuarios()
    for usuario in usuarios:
        if usuario["id"] == user_id:
            data = request.get_json()
            usuario["name"] = data.get("name", usuario["name"])
            usuario["email"] = data.get("email", usuario["email"])
            guardar_usuarios(usuarios)
            return jsonify({"message": "Usuario actualizado correctamente", "user": usuario}), 200
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    usuarios = leer_usuarios()
    for usuario in usuarios:
        if usuario["id"] == user_id:
            usuarios.remove(usuario)
            guardar_usuarios(usuarios)
            return jsonify({"message": "Usuario eliminado correctamente"}), 200
    return jsonify({"error": "Usuario no encontrado"}), 404

@app.errorhandler(404)
def recurso_no_encontrado(error):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def error_interno(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True)
