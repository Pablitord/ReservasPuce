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
    
    # Configuración de correo (SMTP)
    SMTP_HOST = os.environ.get('SMTP_HOST') or ''
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USER = os.environ.get('SMTP_USER') or ''
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or ''
    SMTP_FROM = os.environ.get('SMTP_FROM') or ''
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'True') == 'True'
    SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', 'False') == 'True'
    

    # Chatbot híbrido: DeepSeek solo interpreta (intent + slots). Respuesta final siempre desde Supabase.
    # Si DeepSeek falla (créditos, red, etc.) el bot sigue con rule-based.
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or ''
    DEEPSEEK_API_URL = os.environ.get('DEEPSEEK_API_URL') or 'https://api.deepseek.com/v1/chat/completions'
    DEEPSEEK_CHATBOT_CONFIDENCE_THRESHOLD = float(os.environ.get('DEEPSEEK_CHATBOT_CONFIDENCE_THRESHOLD', '0.6'))