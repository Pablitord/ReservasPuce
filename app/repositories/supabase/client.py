from supabase import create_client, Client
from app.config import Config

class SupabaseClient:
    """Cliente singleton para Supabase"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
        return cls._instance
    
    def get_client(self) -> Client:
        """Obtiene el cliente de Supabase"""
        if self._client is None:
            self._client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        return self._client

def get_supabase_client() -> Client:
    """Función helper para obtener el cliente de Supabase"""
    client = SupabaseClient()
    return client.get_client()
