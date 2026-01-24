from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.supabase.user_repo import UserRepository
from app.services.email_service import EmailService
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import random

class AuthService:
    """Servicio para operaciones de autenticación"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.email_service = EmailService()

    def _generate_verification_code(self) -> str:
        return f"{random.randint(0, 999999):06d}"

    def _send_verification_email(self, user: Dict[str, Any], code: str) -> bool:
        name = user.get('name', 'Usuario')
        email = user.get('email')
        if not email:
            return False
        subject = "Código de verificación - Reservas PUCE"
        body = (
            f"Hola {name},\n\n"
            f"Tu código de verificación es: {code}\n"
            "Este código expira en 30 minutos.\n\n"
            "Si no solicitaste este registro, puedes ignorar este mensaje.\n"
        )
        return self.email_service.send_email(email, subject, body)

    def _humanize_registration_error(self, error_text: str) -> str:
        if not error_text:
            return "Error al registrar usuario"
        lower = error_text.lower()
        if 'column "email_verified" does not exist' in lower or 'column "verification_code" does not exist' in lower:
            return "La base de datos no está actualizada. Debes agregar las columnas de verificación de email."
        if 'duplicate key value violates unique constraint' in lower:
            if 'users_student_id_key' in lower:
                return "El ID de estudiante ya está registrado"
            if 'users_email_key' in lower or 'users_email_key' in error_text:
                return "El email ya está registrado"
            return "Ya existe un usuario con estos datos"
        return "Error al registrar usuario. Verifica los datos e intenta nuevamente."

    def _humanize_email_error(self) -> str:
        if not self.email_service.last_error:
            return "No se pudo enviar el correo de verificación."
        return f"No se pudo enviar el correo de verificación: {self.email_service.last_error}"
    
    def register_user(self, email: str, password: str, name: str, student_id: str) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Registra un nuevo usuario"""
        # Verificar si el usuario ya existe
        existing_user = self.user_repo.get_user_by_email(email)
        if existing_user:
            return False, "El email ya está registrado", None
        
        # Hashear la contraseña
        password_hash = generate_password_hash(password)

        verification_code = self._generate_verification_code()
        verification_expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        
        # Crear usuario
        user = self.user_repo.create_user(
            email,
            password_hash,
            name,
            student_id,
            role='user',
            email_verified=False,
            verification_code=verification_code,
            verification_expires_at=verification_expires_at
        )
        if not user:
            return False, self._humanize_registration_error(self.user_repo.last_error or ''), None

        email_sent = self._send_verification_email(user, verification_code)
        if email_sent:
            return True, "Usuario registrado. Revisa tu correo para verificar la cuenta.", user
        return True, self._humanize_email_error(), user
    
    def login_user(self, email: str, password: str) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Autentica un usuario"""
        user = self.user_repo.get_user_by_email(email)
        if not user:
            return False, "Email o contraseña incorrectos", None
        
        # Verificar contraseña
        if not check_password_hash(user['password_hash'], password):
            return False, "Email o contraseña incorrectos", None

        if not user.get('email_verified', False) and user.get('role') != 'admin':
            return False, "Tu cuenta no está verificada. Revisa tu correo y confirma el código.", None
        
        return True, "Inicio de sesión exitoso", user
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por ID"""
        return self.user_repo.get_user_by_id(user_id)

    def verify_email(self, email: str, code: str) -> tuple[bool, str]:
        """Verifica el email con código"""
        if not email or not code:
            return False, "Email y código son obligatorios"
        user = self.user_repo.get_user_by_email(email)
        if not user:
            return False, "Usuario no encontrado"
        if user.get('email_verified'):
            return True, "Cuenta ya verificada"
        if str(user.get('verification_code', '')).strip() != code.strip():
            return False, "Código de verificación inválido"

        expires_at = user.get('verification_expires_at')
        if expires_at:
            try:
                expires_dt = datetime.fromisoformat(expires_at)
                if expires_dt.tzinfo is not None:
                    now = datetime.now(timezone.utc)
                else:
                    now = datetime.utcnow()
                if now > expires_dt:
                    return False, "El código ha expirado. Solicita uno nuevo."
            except ValueError:
                pass

        updated = self.user_repo.mark_email_verified(user['id'])
        if updated:
            return True, "Cuenta verificada correctamente"
        return False, "No se pudo verificar la cuenta"

    def resend_verification_code(self, email: str) -> tuple[bool, str]:
        """Reenvía el código de verificación"""
        if not email:
            return False, "Email es obligatorio"
        user = self.user_repo.get_user_by_email(email)
        if not user:
            return False, "Usuario no encontrado"
        if user.get('email_verified'):
            return False, "La cuenta ya está verificada"

        code = self._generate_verification_code()
        expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        if not self.user_repo.update_verification_code(user['id'], code, expires_at):
            return False, "No se pudo generar un nuevo código"

        if self._send_verification_email(user, code):
            return True, "Código de verificación enviado"
        return False, self._humanize_email_error()
