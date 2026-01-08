from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.services.admin_service import AdminService
from app.services.reservation_service import ReservationService
from app.services.auth_service import AuthService
from app.deps import admin_required

admin_bp = Blueprint('admin', __name__)
admin_service = AdminService()
reservation_service = ReservationService()
auth_service = AuthService()

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Dashboard del administrador"""
    try:
        stats = admin_service.get_dashboard_stats()
        pending_reservations = admin_service.get_pending_reservations()
        
        # Asegurar que es una lista
        if not isinstance(pending_reservations, list):
            pending_reservations = []
        
        # Limitar a las últimas 5
        pending_reservations = pending_reservations[:5]
        
    except Exception as e:
        print(f"Error cargando dashboard: {e}")
        import traceback
        traceback.print_exc()
        stats = {
            'total_reservations': 0,
            'pending_reservations': 0,
            'approved_reservations': 0,
            'rejected_reservations': 0,
            'total_spaces': 0,
            'total_users': 0
        }
        pending_reservations = []
        flash('Error al cargar el dashboard', 'error')
    
    return render_template('admin/dashboard.html', stats=stats, pending_reservations=pending_reservations)

@admin_bp.route('/reservations')
@admin_required
def reservations():
    """Vista de todas las reservas"""
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'pending':
        reservations = reservation_service.get_pending_reservations()
    elif status_filter == 'approved':
        all_reservations = reservation_service.get_all_reservations()
        reservations = [r for r in all_reservations if r.get('status') == 'approved']
    elif status_filter == 'rejected':
        all_reservations = reservation_service.get_all_reservations()
        reservations = [r for r in all_reservations if r.get('status') == 'rejected']
    else:
        reservations = reservation_service.get_all_reservations()
    
    return render_template('admin/reservations.html', reservations=reservations, status_filter=status_filter)

@admin_bp.route('/reservations/<reservation_id>')
@admin_required
def reservation_detail(reservation_id):
    """Detalle de una reserva para el admin"""
    import uuid
    try:
        # Validar que el ID es un UUID válido
        uuid.UUID(reservation_id)
    except ValueError:
        flash('ID de reserva inválido', 'error')
        return redirect(url_for('admin.reservations'))
    
    reservation = reservation_service.get_reservation_by_id(reservation_id)
    if not reservation:
        flash(f'Reserva no encontrada (ID: {reservation_id})', 'error')
        return redirect(url_for('admin.reservations'))
    
    return render_template('admin/reservation_detail.html', reservation=reservation)

@admin_bp.route('/reservations/<reservation_id>/approve', methods=['POST'])
@admin_required
def approve_reservation(reservation_id):
    """Aprueba una reserva"""
    success, message = reservation_service.approve_reservation(reservation_id, session['user_id'])
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.reservation_detail', reservation_id=reservation_id))

@admin_bp.route('/reservations/<reservation_id>/reject', methods=['POST'])
@admin_required
def reject_reservation(reservation_id):
    """Rechaza una reserva"""
    success, message = reservation_service.reject_reservation(reservation_id, session['user_id'])
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.reservation_detail', reservation_id=reservation_id))

@admin_bp.route('/create_admin', methods=['GET', 'POST'])
@admin_required
def create_admin():
    """Crear un nuevo administrador"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        
        # Validaciones
        if not all([email, password, confirm_password, name, student_id]):
            flash('Por favor completa todos los campos', 'error')
            return render_template('admin/create_admin.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('admin/create_admin.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('admin/create_admin.html')
        
        # Crear admin usando el servicio de autenticación
        from werkzeug.security import generate_password_hash
        from app.repositories.supabase.user_repo import UserRepository
        
        user_repo = UserRepository()
        
        # Verificar si el usuario ya existe
        existing_user = user_repo.get_user_by_email(email)
        if existing_user:
            flash('El email ya está registrado', 'error')
            return render_template('admin/create_admin.html')
        
        # Hashear la contraseña
        password_hash = generate_password_hash(password)
        
        # Crear usuario como admin
        user = user_repo.create_user(email, password_hash, name, student_id, role='admin')
        
        if user:
            flash(f'Administrador {name} creado exitosamente', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Error al crear el administrador', 'error')
    
    return render_template('admin/create_admin.html')
