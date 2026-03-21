from flask import Flask, render_template, request, jsonify
# Importamos la base de datos desde tu archivo 'datos.py'
from datos import db 

# Configuramos Flask para usar tu carpeta 'paginas'
app = Flask(__name__, template_folder='paginas')

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def home():
    # Tu archivo principal según la imagen
    return render_template('inicio.html')

@app.route('/login')
def login_view():
    # Tu archivo de login según la imagen
    return render_template('inicio_sesion.html')

@app.route('/register')
def register_view():
    #archivo de registro
    return render_template('registro.html')

# --- RUTAS DE API (Aquí es donde se conectan los datos) ---

@app.route('/api/auth/login', methods=['POST'])
def handle_login():
    """Procesa el inicio de sesión desde inicio_sesion.html"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        account_type = data.get('type') # 'user' o 'business'

        # Buscamos el usuario en el objeto db importado de datos.py
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

@app.route('/dashboard')
def dashboard():
    return "<h1>Bienvenido al Dashboard</h1><p>Has iniciado sesión correctamente.</p>"

if __name__ == '__main__':
    # Ejecuta el servidor en el puerto 5000
    app.run(debug=True, port=5000)