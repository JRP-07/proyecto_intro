import json
import os

class UserDatabase:
    def __init__(self, file_path='usuarios.json'):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        """Carga los datos desde el archivo JSON local"""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {"user": {}, "business": {}}

    def _save_data(self):
        """Guarda los datos actuales en el archivo JSON"""
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get_user(self, account_type, email):
        return self.data.get(account_type, {}).get(email)

    def add_user(self, account_type, email, password, name):
        if email in self.data[account_type]:
            return False  # Ya existe
        
        self.data[account_type][email] = {
            "name": name,
            "password": password,
            "email": email
        }
        self._save_data() # Guardamos en el archivo local inmediatamente
        return True

# Instancia única para usar en app.py
db = UserDatabase()