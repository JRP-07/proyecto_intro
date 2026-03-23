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
            fecha_nacimiento DATE,
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
    
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS aplicaciones (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       vacante_id INTEGER,
                       aspirante_id TEXT, 
                       fecha_aplicacion TEXT, 
                       estado TEXT DEFAULT 'Pendiente',
                       FOREIGN KEY (vacante_id) References usuarios(identidad)
                   )
                   ''')
    
    # Migración: Agregar columna fecha_nacimiento a perfiles si no existe
    try:
        cursor.execute("ALTER TABLE perfiles ADD COLUMN fecha_nacimiento TEXT")
    except sqlite3.OperationalError:
        # La columna ya existe, ignorar el error
        pass
    
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
    
    # Obtener los datos del usuario registrado
    identidad = session['user_id']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT identidad, nombre_completo FROM usuarios WHERE identidad = ?', (identidad,))
    usuario = cursor.fetchone()
    conn.close()
    
    if not usuario:
        return redirect(url_for('login_page'))
    
    usuario_data = dict(usuario)
    
    """Ruta para completar los datos."""
    return render_template('c_perfil_aspirante.html', identidad=usuario_data['identidad'], nombre=usuario_data['nombre_completo'])

@app.route('/mi-perfil')
def mi_perfil():
    """Ruta para editar el perfil existente del aspirante."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    identidad = session['user_id']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener datos del usuario
    cursor.execute('SELECT identidad, nombre_completo FROM usuarios WHERE identidad = ?', (identidad,))
    usuario = cursor.fetchone()
    
    if not usuario:
        conn.close()
        return redirect(url_for('login_page'))
    
    # Obtener datos del perfil si existe
    cursor.execute('SELECT * FROM perfiles WHERE identidad = ?', (identidad,))
    perfil = cursor.fetchone()
    
    conn.close()
    
    usuario_data = dict(usuario)
    perfil_data = dict(perfil) if perfil else {}
    
    # Combinar datos del usuario y perfil para pasar al template
    template_data = {
        'identidad': usuario_data['identidad'],
        'nombre': usuario_data['nombre_completo'],
        'email': perfil_data.get('email', ''),
        'fecha_nacimiento': perfil_data.get('fecha_nacimiento', ''),
        'edad': perfil_data.get('edad', ''),
        'telefono': perfil_data.get('telefono', ''),
        'residencia': perfil_data.get('residencia', ''),
        'estudios': perfil_data.get('estudios', ''),
        'estudia': perfil_data.get('estudia', ''),
        'archivo_adjunto': perfil_data.get('archivo_adjunto', ''),
        'horario': perfil_data.get('horario', ''),
        'experiencia': perfil_data.get('experiencia', ''),
        'anios_exp': perfil_data.get('anios_exp', ''),
        'modalidad': perfil_data.get('modalidad', ''),
        'jornada': perfil_data.get('jornada', ''),
        'habilidades': perfil_data.get('habilidades', '')
    }
    
    return render_template('c_perfil_aspirante.html', **template_data)

@app.route('/crear-perfil-empresa')
def complete_profile_b_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # Obtener el nombre de la empresa registrada
    identidad = session['user_id']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT nombre_completo FROM usuarios WHERE identidad = ?', (identidad,))
    usuario = cursor.fetchone()
    conn.close()
    
    nombre_empresa = dict(usuario)['nombre_completo'] if usuario else ''
    
    """Ruta para completar los datos."""
    return render_template('c_perfil_empresa.html', nombre_empresa=nombre_empresa)
    
#Dashboard de aspirantes    
@app.route('/dashboard-aspirantes')
def dashboard():
    """Panel principal del usuario."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    identidad = session['user_id']
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Verificar si el perfil está completado
    cursor.execute('SELECT perfil_completo FROM usuarios WHERE identidad = ?', (identidad,))
    usuario_check = cursor.fetchone()
    if not usuario_check or not usuario_check['perfil_completo']:
        conn.close()
        return redirect(url_for('/crear-perfil'))
    
    cursor.execute('SELECT * FROM perfiles WHERE identidad = ?', (identidad,))
    aspirantes=cursor.fetchone()
    
    if not aspirantes:
        # Si no tiene perfil, lo mandamos a crearlo
        conn.close()
        return redirect(url_for('/register'))
    aspirante_dict = dict(aspirantes)

    
    cursor.execute('SELECT * FROM usuarios WHERE identidad = ?', (identidad,))
    usuario=cursor.fetchone()
    usuario_dict=dict(usuario) if usuario else {}
    
    cursor.execute('''
        SELECT a.id as app_id, a.fecha_aplicacion, a.estado, 
               v.*, e.nombre_empresa
        FROM aplicaciones a
        JOIN vacantes v ON a.vacante_id = v.id
        JOIN perfiles_empresas e ON v.empresa_id = e.RTN
        WHERE a.aspirante_id = ?
        ORDER BY a.id DESC
    ''', (identidad,))
    mis_aplicaciones = [dict(row) for row in cursor.fetchall()]
    
    # Obtener todas las vacantes activas que no ha solicitado
    cursor.execute('''
        SELECT v.*, e.nombre_empresa 
        FROM vacantes v
        JOIN perfiles_empresas e ON v.empresa_id = e.RTN
        WHERE v.estado = 'activa' 
        AND v.id NOT IN (SELECT vacante_id FROM aplicaciones WHERE aspirante_id = ?)
        ORDER BY v.id DESC
    ''', (identidad,))
    todas_vacantes = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Normalizar jornada
    jornada_map = {'full': 'tiempo completo', 'medio': 'medio tiempo', 'tiempo completo': 'tiempo completo', 'medio tiempo': 'medio tiempo'}
    
    # Filtrar vacantes que coincidan con los requisitos del aspirante
    def norm(val):
        return (val or '').lower()
    
    jornada_asp = jornada_map.get(norm(aspirante_dict.get('jornada')), norm(aspirante_dict.get('jornada')))
    
    ofertas = [v for v in todas_vacantes if (
        (norm(v.get('ubicacion')) == norm(aspirante_dict.get('residencia')) or norm(v.get('ubicacion')) == 'remoto') and
        (v.get('c_experiencia') or 0) <= (aspirante_dict.get('anios_exp') or 0) and
        jornada_map.get(norm(v.get('jornada')), norm(v.get('jornada'))) == jornada_asp and
        norm(v.get('horario')) == norm(aspirante_dict.get('horario')) and
        norm(v.get('modalidad')) == norm(aspirante_dict.get('modalidad'))
    )]
    
    return render_template('dashboard_a.html', perfil=aspirante_dict, usuario=usuario_dict, aplicaciones=mis_aplicaciones, ofertas=ofertas)


#aplicar para vacante
@app.route('/api/vacantes/aplicar', methods=['POST'])
def aplicar_vacante():
    """Registra la postulación de un aspirante a una vacante."""
    if 'user_id' not in session:
        return jsonify({"message": "Inicie sesión para aplicar"}), 401
    
    data = request.get_json()
    vacante_id = data.get('vacante_id')
    aspirante_id = session['user_id']
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    if not vacante_id:
        return jsonify({"message": "ID de vacante no proporcionado"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar si ya aplicó
        cursor.execute('SELECT id FROM aplicaciones WHERE vacante_id = ? AND aspirante_id = ?', 
                       (vacante_id, aspirante_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({"message": "Ya te has postulado a esta vacante"}), 400

        # Insertar aplicación
        cursor.execute('''
            INSERT INTO aplicaciones (vacante_id, aspirante_id, fecha_aplicacion, estado)
            VALUES (?, ?, ?, 'Pendiente')
        ''', (vacante_id, aspirante_id, fecha))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "¡Postulación enviada con éxito!"}), 200

    except Exception as e:
        return jsonify({"message": f"Error al procesar: {str(e)}"}), 500

#eliminar postulacion de vacante
@app.route('/api/aplicaciones/eliminar', methods=['POST'])
def eliminar_aplicacion():
    """Permite al aspirante retirar su postulación."""
    if 'user_id' not in session:
        return jsonify({"message": "No autorizado"}), 401
    
    data = request.get_json()
    app_id = data.get('app_id')
    aspirante_id = session['user_id']

    if not app_id:
        return jsonify({"message": "ID de aplicación requerido"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar que la aplicación pertenezca al usuario
        cursor.execute('DELETE FROM aplicaciones WHERE id = ? AND aspirante_id = ?', (app_id, aspirante_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"message": "No se encontró la aplicación o no tienes permiso"}), 404
            
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Postulación eliminada con éxito"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

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
    
    
    # Verificar si el perfil está completado
    cursor.execute('SELECT perfil_completo FROM usuarios WHERE identidad = ?', (identidad,))
    usuario_check = cursor.fetchone()
    if not usuario_check or not usuario_check['perfil_completo']:
        conn.close()
        return redirect(url_for('complete_profile_b_page'))
    
    # Datos de la empresa
    cursor.execute('SELECT * FROM perfiles_empresas WHERE RTN = ?', (identidad,))
    empresa = cursor.fetchone()
    
    empresa_dict=dict(empresa) if empresa else {}
    
    # Sus vacantes publicadas
    cursor.execute('SELECT * FROM vacantes WHERE empresa_id = ? ORDER BY id DESC', (identidad,))
    vacantes = cursor.fetchall()
    
    vacantes_dict=[dict(v) for v in vacantes]
    
    conn.close()
    return render_template('dashboard_e.html', empresa=empresa_dict, vacantes=vacantes_dict)

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
        user_type = data.get('type')  # 'user' or 'business'

        if not identidad or not password or not user_type:
            return jsonify({"message": "Faltan datos requeridos"}), 400

        # Map type to database type
        db_type = 'empresa' if user_type == 'business' else 'aspirante'

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT password, perfil_completo, tipo_usuario FROM usuarios WHERE identidad = ? AND tipo_usuario = ?', (identidad, db_type))
        user = cursor.fetchone()
        conn.close()

        if user and user[0] == password:
            session['user_id'] = identidad
            session['user_type'] = db_type
            # Redirigir según el tipo y estado del perfil
            if db_type == 'aspirante':
                target = "/dashboard-aspirantes" if user[1] == 1 else "/crear-perfil"
            else:
                target = "/dashboard-empresas"
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
                identidad, email, fecha_nacimiento, edad, telefono, residencia, estudios, estudia,
                archivo_adjunto, horario, experiencia, anios_exp, 
                modalidad, jornada, habilidades
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            identidad,
            request.form.get('email'),
            request.form.get('fecha_nacimiento'),
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
            request.form.get('ubicacion'),
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


@app.route('/api/vacantes/<int:vacante_id>/candidatos', methods=['GET'])
def obtener_candidatos_vacante(vacante_id):
    """Obtiene los candidatos que han aplicado a una vacante específica."""
    if 'user_id' not in session:
        return jsonify({"message": "No autorizado"}), 401
    
    try:
        identidad = session['user_id']
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar que la vacante pertenece a la empresa logueada
        cursor.execute('SELECT empresa_id FROM vacantes WHERE id = ?', (vacante_id,))
        vacante = cursor.fetchone()
        if not vacante or vacante['empresa_id'] != identidad:
            conn.close()
            return jsonify({"message": "No tiene permiso para ver estos candidatos"}), 403
        
        # Obtener candidatos que han aplicado a esta vacante
        cursor.execute('''
            SELECT DISTINCT a.aspirante_id, a.fecha_aplicacion, a.estado, u.nombre_completo, p.email, p.telefono, p.residencia, p.habilidades, p.experiencia, p.anios_exp
            FROM aplicaciones a
            JOIN usuarios u ON a.aspirante_id = u.identidad
            LEFT JOIN perfiles p ON a.aspirante_id = p.identidad
            WHERE a.vacante_id = ?
            ORDER BY a.fecha_aplicacion DESC
        ''', (vacante_id,))
        
        candidatos = cursor.fetchall()
        candidatos_list = [dict(c) for c in candidatos]
        conn.close()
        
        return jsonify({"candidatos": candidatos_list, "total": len(candidatos_list)}), 200
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