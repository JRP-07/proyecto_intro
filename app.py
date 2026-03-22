from flask import Flask, request, jsonify, render_template
import json
import os
import jinja2

app = Flask(__name__, template_folder='paginas')

mis_carpetas=jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('admin'),
    jinja2.FileSystemLoader('paginas')
])
app.jinja_loader=mis_carpetas

# Configuración del archivo de base de datos
DB_FILE = 'db.json'

def load_db():
    """Carga los datos del archivo JSON. Si no existe, crea uno vacío."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"users": {}}, f)
    
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"users": {}}

def save_db(data):
    """Guarda los datos en el archivo JSON."""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- RUTAS DE NAVEGACIÓN (Renderizan el HTML) ---

@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/login')
def login_page():
    return render_template('inicio_sesion.html')

@app.route('/register')
def register_page():
    return render_template('registro.html')

@app.route('/crear-perfil')
def complete_profile_page():
    return render_template('c_perfil_aspirante.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin-p')
def admin_panel():
    return render_template('panel_admin.html')

# --- RUTAS DE API (Manejan los datos y SIEMPRE devuelven JSON) ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registra a un usuario usando su número de Identidad."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Error en el formato de datos"}), 400
            
        db = load_db()
        identidad = data.get('identidad') # ID Único (Cédula/DNI)
        
        if not identidad:
            return jsonify({"message": "El número de identidad es obligatorio"}), 400
            
        if identidad in db['usuarios']:
            return jsonify({"message": "Esta identidad ya se encuentra registrada"}), 400
        
        # Registro inicial
        db['usuarios'][identidad] = {
            "nombre_completo": data.get('nombre'),
            "password": data.get('password'), 
            "tipo_usuario": data.get('tipo', 'aspirante'),
            "perfil_completo": False,
            "datos_perfil": {}
        }
        
        save_db(db)
        
        # Guardamos en sesión la identidad para el siguiente paso (crear perfil)
        session['user_id'] = identidad
        
        return jsonify({
            "redirect_url": "/crear-perfil", 
            "identidad": identidad
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error servidor: {str(e)}"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Acceso al sistema mediante Identidad y Contraseña."""
    try:
        data = request.get_json()
        db = load_db()
        identidad = data.get('identidad')
        password = data.get('password')
        
        usuario = db['usuarios'].get(identidad)
        
        if usuario and usuario['password'] == password:
            session['user_id'] = identidad
            # Decidimos a dónde enviar al usuario según si ya completó su perfil
            target = "/dashboard" if usuario['perfil_completo'] else "/crear-perfil"
            
            return jsonify({
                "redirect_url": target, 
                "identidad": identidad,
                "nombre": usuario['nombre_completo']
            }), 200
        
        return jsonify({"message": "Identidad o contraseña incorrectas"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/api/complete-profile', methods=['POST'])
def complete_profile():
    """Guarda la información detallada asociada a la identidad en sesión."""
    try:
        identidad = session.get('user_id')
        if not identidad:
            return jsonify({"message": "Sesión expirada o no válida"}), 401

        data = request.get_json()
        db = load_db()

        if identidad in db['usuarios']:
            # Actualizamos los campos de perfil específicos
            db['usuarios'][identidad]["datos_perfil"] = {
                "biografia": data.get('biografia'),
                "telefono": data.get('telefono'),
                "habilidades": data.get('habilidades'),
                "experiencia": data.get('experiencia')
            }
            db['usuarios'][identidad]["perfil_completo"] = True
            
            save_db(db)
            
            return jsonify({
                "status": "success", 
                "message": "Información de perfil guardada",
                "redirect_url": "/dashboard"
            }), 200
        
        return jsonify({"message": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"message": f"Error al guardar perfil: {str(e)}"}), 500

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({"message": "Sesión finalizada"}), 200

if __name__ == '__main__':
    # Ejecución en modo desarrollo
    app.run(debug=True, port=5000)