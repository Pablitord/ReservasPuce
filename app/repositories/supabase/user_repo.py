from app.repositories.supabase.client import get_supabase_client
from typing import Optional, Dict, Any

class UserRepository:
    """Repositorio para operaciones de usuarios"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = 'users'
        self.last_error = None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por email"""
        try:
            response = self.client.table(self.table).select('*').eq('email', email).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            self.last_error = str(e)
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
            self.last_error = str(e)
            print(f"Error obteniendo usuario por ID: {e}")
            return None
    
    def create_user(
        self,
        email: str,
        password_hash: str,
        name: str,
        student_id: str,
        role: str = 'user',
        email_verified: bool = False,
        verification_code: Optional[str] = None,
        verification_expires_at: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Crea un nuevo usuario"""
        try:
            self.last_error = None
            data = {
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'student_id': student_id,
                'role': role,
                'email_verified': email_verified,
                'verification_code': verification_code,
                'verification_expires_at': verification_expires_at
            }
            response = self.client.table(self.table).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            self.last_error = str(e)
            print(f"Error creando usuario: {e}")
            return None

    def update_verification_code(self, user_id: str, code: str, expires_at: str) -> bool:
        """Actualiza el código y expiración de verificación"""
        try:
            data = {
                'verification_code': code,
                'verification_expires_at': expires_at
            }
            response = self.client.table(self.table).update(data).eq('id', user_id).execute()
            return bool(response.data)
        except Exception as e:
            self.last_error = str(e)
            print(f"Error actualizando verificación: {e}")
            return False

    def mark_email_verified(self, user_id: str) -> bool:
        """Marca el email como verificado y limpia el código"""
        try:
            data = {
                'email_verified': True,
                'verification_code': None,
                'verification_expires_at': None
            }
            response = self.client.table(self.table).update(data).eq('id', user_id).execute()
            return bool(response.data)
        except Exception as e:
            self.last_error = str(e)
            print(f"Error marcando email como verificado: {e}")
            return False
    
    def get_all_users(self) -> list:
        """Obtiene todos los usuarios"""
        try:
            response = self.client.table(self.table).select('id, email, name, student_id, role, created_at').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
            return []
