from flask_login import LoginManager, UserMixin

# Configuración de Flask-Login
login_manager = LoginManager()

# Usuarios válidos (puedes conectar esto a una base de datos)
USERS = {
    "admin": {"password": "admin"}
}

# Clase de Usuario
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario por ID (necesario para Flask-Login)"""
    if user_id in USERS:
        return User(user_id)
    return None
