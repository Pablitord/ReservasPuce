from app.repositories.supabase.client import get_supabase_client
from typing import Optional, Dict, Any

class UserRepository:
    """Repositorio para operaciones de usuarios"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = 'users'
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por email"""
        try:
            response = self.client.table(self.table).select('*').eq('email', email).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error obteniendo usuario por email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por ID"""
        try:
            response = self.client.table(self.table).select('*').eq('id', user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error obteniendo usuario por ID: {e}")
            return None
    
    def create_user(self, email: str, password_hash: str, name: str, student_id: str, role: str = 'user') -> Optional[Dict[str, Any]]:
        """Crea un nuevo usuario"""
        try:
            data = {
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'student_id': student_id,
                'role': role
            }
            response = self.client.table(self.table).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return None
    
    def get_all_users(self) -> list:
        """Obtiene todos los usuarios"""
        try:
            response = self.client.table(self.table).select('id, email, name, student_id, role, created_at').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
            return []
