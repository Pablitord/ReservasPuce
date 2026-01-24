from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import AuthService
from app.deps import login_required

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de inicio de sesión"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Por favor completa todos los campos', 'error')
            return render_template('auth/login.html')
        
        success, message, user = auth_service.login_user(email, password)
        
        if success:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['name'] = user['name']
            session['role'] = user.get('role', 'user')
            flash(message, 'success')
            
            if user.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.calendar'))
        else:
            flash(message, 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta de registro"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        
        # Validaciones
        if not all([email, password, confirm_password, name, student_id]):
            flash('Por favor completa todos los campos', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('auth/register.html')
        
        success, message, user = auth_service.register_user(email, password, name, student_id)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.verify_email', email=email))
        else:
            flash(message, 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Ruta de cierre de sesión"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify_email():
    """Verificación de cuenta por código"""
    email = request.args.get('email') or request.form.get('email') or ''
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        success, message = auth_service.verify_email(email, code)
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        flash(message, 'error')
    return render_template('auth/verify.html', email=email)


@auth_bp.route('/verify/resend', methods=['POST'])
def resend_verification():
    """Reenvía el código de verificación"""
    email = request.form.get('email', '').strip()
    success, message = auth_service.resend_verification_code(email)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('auth.verify_email', email=email))
