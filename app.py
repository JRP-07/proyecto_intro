from flask import Flask, render_template, request, jsonify
import os
# Importamos la base de datos desde tu archivo 'datos.py'
try:
    from datos import db 
except ImportError:
    # Fallback por si el archivo no existe aún durante la configuración
    db = None

app = Flask(__name__, template_folder='paginas')

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def home():
    return render_template('inicio.html')

@app.route('/login')
def login_view():
    return render_template('inicio_sesion.html')

@app.route('/register')
def register_view():
    return render_template('registro.html')

@app.route('/crear-perfil')
def create_profile_view():
    return render_template('c_perfil_aspirante.html')

@app.route('/dashboard')
def dashboard():
    # En una app real, aquí verificaríamos la sesión
    return "<h1>Bienvenido al Dashboard</h1><p>Has iniciado sesión correctamente.</p>"

# --- RUTAS DE API ---

@app.route('/api/auth/login', methods=['POST'])
def handle_login():
    if not db:
        return jsonify({"status": "error", "message": "Base de datos no configurada"}), 500
        
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        account_type = data.get('type') # 'user' o 'business'

        # Buscamos en la base de datos local (archivo JSON)
        user = db.get_user(account_type, email)

        if user and user['password'] == password:
            return jsonify({
                "status": "success",
                "message": "Acceso concedido",
                "redirect_url": "/dashboard"
            }), 200
        
        return jsonify({
            "status": "error", 
            "message": "El correo o la contraseña son incorrectos."
        }), 401

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def handle_register():
    if not db:
        return jsonify({"status": "error", "message": "Base de datos no configurada"}), 500

    try:
        data = request.json
        # Intentamos registrar y guardar localmente
        success = db.add_user(
            data.get('type'),
            data.get('email'),
            data.get('password'),
            data.get('name')
        )

        if success:
            return jsonify({"status": "success", "redirect_url": "/login"}), 201
        
        return jsonify({"status": "error", "message": "El usuario ya existe"}), 409
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)