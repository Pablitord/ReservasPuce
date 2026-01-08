"""
Script para crear usuarios administradores
Uso: python create_admin.py
"""

import sys
from werkzeug.security import generate_password_hash

# Agregar el directorio app al path
sys.path.insert(0, '.')

from app.repositories.supabase.user_repo import UserRepository

def create_admin():
    """Función para crear un administrador"""
    print("=" * 50)
    print("  Crear Usuario Administrador")
    print("=" * 50)
    print()
    
    # Obtener datos del usuario
    email = input("Email del administrador: ").strip()
    if not email:
        print("❌ El email es obligatorio")
        return
    
    password = input("Contraseña: ").strip()
    if not password or len(password) < 6:
        print("❌ La contraseña debe tener al menos 6 caracteres")
        return
    
    name = input("Nombre completo: ").strip()
    if not name:
        print("❌ El nombre es obligatorio")
        return
    
    student_id = input("ID de estudiante (opcional, presiona Enter para usar email): ").strip()
    if not student_id:
        student_id = f"ADMIN_{email.split('@')[0].upper()}"
    
    # Confirmar
    print()
    print("Datos del administrador:")
    print(f"  Email: {email}")
    print(f"  Nombre: {name}")
    print(f"  ID: {student_id}")
    print()
    confirm = input("¿Crear este administrador? (s/n): ").strip().lower()
    
    if confirm != 's':
        print("❌ Operación cancelada")
        return
    
    # Crear el usuario
    try:
        user_repo = UserRepository()
        
        # Verificar si el usuario ya existe
        existing = user_repo.get_user_by_email(email)
        if existing:
            print(f"❌ Ya existe un usuario con el email: {email}")
            return
        
        # Hashear la contraseña
        password_hash = generate_password_hash(password)
        
        # Crear usuario como admin
        user = user_repo.create_user(
            email=email,
            password_hash=password_hash,
            name=name,
            student_id=student_id,
            role='admin'
        )
        
        if user:
            print()
            print("✅ Administrador creado exitosamente!")
            print(f"   ID: {user['id']}")
            print(f"   Email: {user['email']}")
            print(f"   Nombre: {user['name']}")
            print(f"   Rol: {user['role']}")
        else:
            print("❌ Error al crear el administrador")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
