from flask import Flask, send_file
from config import Config
from models import db
import os

app = Flask(__name__)
app.config.from_object(Config)
app.json.sort_keys = False

db.init_app(app)

# Importar y registrar blueprints
from routes_usuarios import usuarios_bp
#from routes_rutinas import rutinas_bp
from routes_ejercicios import ejercicios_bp
#from routes_series import series_bp
#from routes_entrenamientos import entrenamientos_bp
from routes_entrenamientos_realizados import entrenamientos_realizados_bp
#from routes_series_realizadas import series_realizadas_bp
#from routes_nivel_rutinas import nivel_rutinas_bp
from routes_rutinas_completas import rutinas_completas_bp

app.register_blueprint(usuarios_bp)
#app.register_blueprint(rutinas_bp)
app.register_blueprint(ejercicios_bp)
#app.register_blueprint(series_bp)
#app.register_blueprint(entrenamientos_bp)
app.register_blueprint(entrenamientos_realizados_bp)
#app.register_blueprint(series_realizadas_bp)
#app.register_blueprint(nivel_rutinas_bp)
app.register_blueprint(rutinas_completas_bp)

if __name__ == '__main__':

    app.run(debug=True)