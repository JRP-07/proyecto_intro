from flask import Flask, render_template, request, jsonify
from models import db  # Asegúrate de que models.py esté en la misma carpeta que app.py

# Configuramos Flask para que busque los HTML en la carpeta 'paginas' en lugar de 'templates'
app = Flask(__name__, template_folder='paginas')

# --- RUTAS DE NAVEGACIÓN (Vistas) ---

@app.route('/')
def home():
    # Según tu imagen, tu archivo principal se llama inicio.html
    return render_template('inicio.html')

@app.route('/login')
def login_view():
    # Según tu imagen, tu login se llama inicio_sesion.html
    return render_template('inicio_sesion.html')

@app.route('/dashboard')
def dashboard():
    return "<h1>Bienvenido al Dashboard</h1><p>Autenticación exitosa.</p>"

# --- RUTAS DE API (Lógica de Negocio) ---

@app.route('/api/auth/login', methods=['POST'])
def handle_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    account_type = data.get('type')

    user = db.get_user(account_type, email)

    if user and user['password'] == password:
        return jsonify({
            "status": "success",
            "redirect_url": "/dashboard"
        }), 200
    
    return jsonify({"status": "error", "message": "Credenciales incorrectas"}), 401

@app.route('/api/auth/register', methods=['POST'])
def handle_register():
    data = request.json
    # Intentamos registrar al usuario usando el método de models.py
    success = db.add_user(
        data.get('type'),
        data.get('email'),
        data.get('password'),
        data.get('name')
    )

    if success:
        return jsonify({"status": "success", "redirect_url": "/login"}), 201
    
    return jsonify({"status": "error", "message": "El usuario ya existe"}), 409

if __name__ == '__main__':
    # El puerto por defecto es 5000
    app.run(debug=True, port=5000)