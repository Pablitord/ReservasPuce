from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.supabase.user_repo import UserRepository
from typing import Optional, Dict, Any

class AuthService:
    """Servicio para operaciones de autenticación"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def register_user(self, email: str, password: str, name: str, student_id: str) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Registra un nuevo usuario"""
        # Verificar si el usuario ya existe
        existing_user = self.user_repo.get_user_by_email(email)
        if existing_user:
            return False, "El email ya está registrado", None
        
        # Hashear la contraseña
        password_hash = generate_password_hash(password)
        
        # Crear usuario
        user = self.user_repo.create_user(email, password_hash, name, student_id, role='user')
        if user:
            return True, "Usuario registrado exitosamente", user
        return False, "Error al registrar usuario", None
    
    def login_user(self, email: str, password: str) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Autentica un usuario"""
        user = self.user_repo.get_user_by_email(email)
        if not user:
            return False, "Email o contraseña incorrectos", None
        
        # Verificar contraseña
        if not check_password_hash(user['password_hash'], password):
            return False, "Email o contraseña incorrectos", None
        
        return True, "Inicio de sesión exitoso", user
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por ID"""
        return self.user_repo.get_user_by_id(user_id)
