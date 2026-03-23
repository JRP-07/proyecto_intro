# Este archivo se encarga ÚNICAMENTE de la estructura de los datos
# En un futuro, aquí configurarías la conexión a SQL Alchemy o MongoDB

class UserDatabase:
    def __init__(self):
        # Base de datos simulada
        self.data = {
            "user": {
                "talento@ejemplo.com": {
                    "password": "123",
                    "nombre": "Ana García",
                    "rol": "Candidato"
                }
            },
            "business": {
                "empresa@ejemplo.com": {
                    "password": "456",
                    "nombre": "Tech Global Solutions",
                    "rol": "Reclutador"
                }
            }
        }

    def get_user(self, account_type, email):
        """Busca un usuario por tipo y email."""
        return self.data.get(account_type, {}).get(email)

    def add_user(self, account_type, email, password, nombre):
        """Registra un nuevo usuario si no existe."""
        if email in self.data[account_type]:
            return False
        
        self.data[account_type][email] = {
            "password": password,
            "nombre": nombre,
            "rol": "Candidato" if account_type == "user" else "Reclutador"
        }
        return True

# Instancia global para ser usada por la app
db = UserDatabase()