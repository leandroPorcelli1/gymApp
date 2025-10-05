from flask import Flask
from app.config import Config
from modelos.models import db

app = Flask(__name__)
app.config.from_object(Config)
app.json.sort_keys = False

db.init_app(app)

# Importar y registrar blueprints
from rutas.routes_usuarios import usuarios_bp
from rutas.routes_ejercicios import ejercicios_bp
from rutas.routes_entrenamientos_realizados import entrenamientos_realizados_bp
from rutas.routes_rutinas_completas import rutinas_completas_bp

app.register_blueprint(usuarios_bp)
app.register_blueprint(ejercicios_bp)
app.register_blueprint(entrenamientos_realizados_bp)
app.register_blueprint(rutinas_completas_bp)

if __name__ == '__main__':

    app.run(debug=True)