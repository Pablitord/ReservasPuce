import os
from dotenv import load_dotenv
from pathlib import Path

# Obtener la ruta del directorio raíz del proyecto (ReservasPuce)
# app/config.py -> .parent = app/ -> .parent = ReservasPuce/
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'

# Cargar variables de entorno desde el archivo .env en la raíz
# Primero intenta cargar desde la raíz, si no existe, busca en el directorio actual
load_dotenv(ENV_FILE)  # Intenta cargar desde la raíz del proyecto
load_dotenv()  # También carga desde el directorio actual (por si acaso)

class Config:
    """Configuración de la aplicación"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or ''
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY') or ''
    
    # Configuración de la aplicación
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
