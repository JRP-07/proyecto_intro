import json
import os

class UserDatabase:
    def __init__(self, filename='usuarios.json'):
        self.filename = filename
        # Estructura inicial de la base de datos
        self.default_data = {
            "user": {},      # Candidatos
            "business": {}   # Empresas/Reclutadores
        }
        self._load_data()

    def _load_data(self):
        """Carga los datos desde el archivo JSON o crea uno nuevo si no existe."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = self.default_data
        else:
            self.data = self.default_data
            self._save_to_disk()

    def _save_to_disk(self):
        """Escribe los datos actuales en el archivo físico."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error guardando en base de datos: {e}")
            return False

    def add_user(self, account_type, email, password, name):
        """Registra un nuevo usuario y lo guarda en el disco."""
        # Validar que el tipo sea correcto
        if account_type not in self.data:
            account_type = 'user' # Por defecto candidato
            
        # Verificar si ya existe
        if email in self.data[account_type]:
            return False
        
        # Agregar a la memoria
        self.data[account_type][email] = {
            "password": password,
            "name": name,
            "perfil_completado": False
        }
        
        # Guardar en el archivo físico
        return self._save_to_disk()

    def get_user(self, account_type, email):
        """Busca un usuario por email y tipo."""
        if account_type not in self.data:
            return None
        return self.data[account_type].get(email)

# Instancia única para ser usada en app.py
db = UserDatabase()