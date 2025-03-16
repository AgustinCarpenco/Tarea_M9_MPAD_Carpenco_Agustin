import flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Inicializar Flask y Flask-Login
server = flask.Flask(__name__)
server.secret_key = 'mi_secreto'  # Cambiar por clave segura en producción
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# Clase Usuario simple
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "admin"
        self.password = "admin"

    def __repr__(self):
        return f"{self.name}/{self.password}"

# Crear un usuario único (admin)
user = User(id=1)

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return user
    return None

# Ruta para login
@server.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        if username == user.name and password == user.password:
            login_user(user)
            return flask.redirect('/')
        else:
            return flask.abort(401)
    return '''
    <form action='' method='post'>
        <input type='text' name='username' placeholder='usuario'/>
        <input type='password' name='password' placeholder='contraseña'/>
        <input type='submit' value='Login'/>
    </form>
    '''

# Ruta para logout
@server.route("/logout")
@login_required
def logout():
    logout_user()
    return flask.redirect('/login')
