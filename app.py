import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx, no_update, callback
from flask import Flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

# 📌 Inicializar Flask
server = Flask(__name__)
server.secret_key = 'tu_clave_secreta'

# 📌 Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"

# 📌 Simulación de Base de Datos de Usuarios
USERS = {"admin": {"password": "admin"}}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in USERS else None

# 📌 Inicializar Dash con FontAwesome para iconos
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css"  # FontAwesome para iconos
    ],
    use_pages=True,  # Activar el sistema de páginas
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

# Ahora importamos las páginas después de instanciar la app
from pages import home, performance, gps

# 📌 Layout de Login Mejorado
def get_login_layout():
    return html.Div([
        dcc.Location(id='url-login', refresh=True),
        html.Div([  # Contenedor principal con fondo de gradiente
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        # Card para el formulario de login con sombra y bordes redondeados
                        dbc.Card([
                            dbc.CardHeader([
                                html.H3("Dashboard Deportivo", className="text-center fw-bold mb-0"),
                                html.Img(src="/assets/logo.png", height="80px", className="mx-auto d-block my-3"),
                                html.H5("Iniciar Sesión", className="text-center")
                            ], className="bg-primary text-white rounded-top", style={"border": "none"}),
                            dbc.CardBody([
                                # Icono de usuario
                                dbc.InputGroup([
                                    dbc.InputGroupText(html.I(className="fas fa-user")),
                                    dbc.Input(
                                        id="username", 
                                        placeholder="Usuario", 
                                        type="text",
                                        className="form-control-lg"
                                    )
                                ], className="mb-4"),
                                
                                # Icono de contraseña
                                dbc.InputGroup([
                                    dbc.InputGroupText(html.I(className="fas fa-lock")),
                                    dbc.Input(
                                        id="password", 
                                        placeholder="Contraseña", 
                                        type="password",
                                        className="form-control-lg"
                                    )
                                ], className="mb-4"),
                                
                                # Botón de login
                                dbc.Button(
                                    "Ingresar", 
                                    id="login-btn", 
                                    color="primary", 
                                    className="w-100 py-2 mb-3 btn-lg",
                                    n_clicks=0,
                                    style={"fontWeight": "bold"}
                                ),
                                
                                # Mensaje de error
                                html.Div(id="login-output", className="text-danger text-center mt-2")
                            ], className="px-4 py-4"),
                        ], className="shadow-lg", style={"borderRadius": "15px"})
                    ], width={"size": 10, "offset": 1, "sm": 6, "offset_sm": 3, "md": 4, "offset_md": 4})
                ], align="center", justify="center", style={"minHeight": "100vh"})
            ], fluid=True)
        ], style={
            "background": "linear-gradient(135deg, #1e3c72, #2a5298)",
            "minHeight": "100vh",
            "display": "flex",
            "alignItems": "center"
        })
    ])

# 📌 Navbar compartido para todas las páginas cuando el usuario está logueado
def crear_navbar():
    return dbc.Navbar(
        dbc.Container([
            # Logo y Brand
            html.A(
                dbc.Row([
                    dbc.Col(html.Img(src="/assets/logo.png", height="30px")),
                    dbc.Col(dbc.NavbarBrand("Dashboard Deportivo", className="ms-2"))
                ], align="center"),
                href="/",
                style={"textDecoration": "none"}
            ),
            
            # Botón toggler para modo responsive
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            
            # Elementos del navbar (colapsables en móvil)
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
                    dbc.NavItem(dbc.NavLink("Performance", href="/performance", active="exact")),
                    dbc.NavItem(dbc.NavLink("GPS", href="/gps", active="exact")),
                    dbc.DropdownMenu(
                        [dbc.DropdownMenuItem("Cerrar Sesión", id="logout-btn")],
                        label=current_user.id if current_user.is_authenticated else "Usuario",
                        nav=True,
                        in_navbar=True,
                        align_end=True,
                    ),
                ], className="ms-auto", navbar=True),
                id="navbar-collapse",
                navbar=True
            ),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    )

# 📌 Layout principal de la aplicación
app.layout = html.Div([
    dcc.Store(id="session-store", storage_type="session"),
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# ✅ Callback para manejar la navegación y autenticación
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('session-store', 'data')]
)
def display_page(pathname, session_data):
    """Carga el layout correcto según la ruta y el estado de sesión."""
    # Para depuración
    print(f"URL: {pathname}, Session data: {session_data}")
    
    if not session_data or not session_data.get("logged_in"):
        return get_login_layout()
    
    # Si el usuario está autenticado, mostrar la página correspondiente
    return html.Div([
        crear_navbar(),
        dash.page_container
    ])

# ✅ Callback para el inicio de sesión
@app.callback(
    [Output('session-store', 'data'),
     Output('login-output', 'children'),
     Output('url', 'pathname')],
    [Input('login-btn', 'n_clicks')],
    [State('username', 'value'),
     State('password', 'value')],
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    """Maneja el inicio de sesión."""
    if n_clicks:
        if username and password and username in USERS and USERS[username]['password'] == password:
            login_user(User(username))
            # Depuración
            print(f"Usuario {username} autenticado correctamente")
            return {"logged_in": True}, "", "/"
        return no_update, "Usuario o contraseña incorrectos", no_update
    return no_update, no_update, no_update

# ✅ Callback para el cierre de sesión
@app.callback(
    [Output('session-store', 'data', allow_duplicate=True),
     Output('url', 'pathname', allow_duplicate=True)],
    [Input('logout-btn', 'n_clicks')],
    prevent_initial_call=True
)
def logout(n_clicks):
    """Maneja el cierre de sesión."""
    if n_clicks:
        logout_user()
        # Depuración
        print("Usuario desconectado")
        return {"logged_in": False}, "/"
    return no_update, no_update

# ✅ Callback para el toggler del navbar en modo responsive
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# 🚀 Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)  # Cambiado de 8050 a 8060