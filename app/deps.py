from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('user.calendar'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Obtiene el usuario actual de la sesión"""
    from app.repositories.supabase.user_repo import UserRepository
    if 'user_id' in session:
        user_repo = UserRepository()
        return user_repo.get_user_by_id(session['user_id'])
    return None
