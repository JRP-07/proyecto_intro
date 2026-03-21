from flask import Flask, render_template, request, jsonify, session, redirect, url_status

app = Flask(__name__)
app.secret_key = "secret_talent_key_123" # Necesario para manejar sesiones de usuario

# Simulación de base de datos en memoria
users = []

@app.route('/')
def index():
    # Página de aterrizaje principal
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Página protegida que se muestra tras el login
    if 'user' in session:
        return f"<h1>Bienvenido al Panel de Talento, {session['user']}</h1><p>Aquí definiremos tu rol.</p><a href='/logout'>Cerrar sesión</a>"
    return redirect('/')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Simulación de validación (en producción usar hashing de contraseñas)
    if email == "admin@talentflow.com" and password == "12345":
        session['user'] = email
        return jsonify({"status": "success", "message": "Inicio de sesión exitoso", "redirect": "/dashboard"}), 200
    
    return jsonify({"status": "error", "message": "Credenciales inválidas. Prueba con admin@talentflow.com / 12345"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if name and email and password:
        # Guardamos el usuario en nuestra lista temporal
        users.append({"name": name, "email": email, "password": password})
        session['user'] = email # Iniciamos sesión automáticamente
        return jsonify({"status": "success", "message": "¡Cuenta creada exitosamente!", "redirect": "/dashboard"}), 201
    
    return jsonify({"status": "error", "message": "Por favor, completa todos los campos"}), 400

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5000)