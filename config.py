import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Cargar variables de entorno
load_dotenv()


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True  # Activar el pre-ping en el pool de conexiones
    }
    
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

    
    # Configuración de Turso
    
    #TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
    #TURSO_AUTH_TOKEN = os.environ.get("TURSO_DATABASE_TOKEN")

    # --- NUEVA CONFIGURACIÓN ---
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_POSTGRESQL")
