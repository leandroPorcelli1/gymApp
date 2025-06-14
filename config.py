import os
from dotenv import load_dotenv

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
    SQLALCHEMY_DATABASE_URI = f"sqlite+{os.getenv('TURSO_DATABASE_URI')}/?authToken={os.getenv('TURSO_DATABASE_TOKEN')}&secure=true&check_same_thread=false"    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'gymapp.db')
    