from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.services.admin_service import AdminService
from app.services.reservation_service import ReservationService
from app.services.auth_service import AuthService
from app.services.class_schedule_service import ClassScheduleService
from app.services.space_service import SpaceService
from app.repositories.supabase.reservation_deletion_repo import ReservationDeletionRepository
from app.deps import admin_required

admin_bp = Blueprint('admin', __name__)
admin_service = AdminService()
reservation_service = ReservationService()
auth_service = AuthService()
class_schedule_service = ClassScheduleService()
space_service = SpaceService()
reservation_deletion_repo = ReservationDeletionRepository()

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
    rejection_reason = request.form.get('rejection_reason', '').strip()
    
    # Validar que se proporcione una razón
    if not rejection_reason or len(rejection_reason) < 10:
        flash('Debes proporcionar una razón del rechazo de al menos 10 caracteres', 'error')
        return redirect(url_for('admin.reservation_detail', reservation_id=reservation_id))
    
    success, message = reservation_service.reject_reservation(reservation_id, session['user_id'], rejection_reason)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin.reservation_detail', reservation_id=reservation_id))

@admin_bp.route('/reservations/<reservation_id>/delete', methods=['POST'])
@admin_required
def delete_reservation(reservation_id):
    """Elimina una reserva (admin)"""
    reason = request.form.get('delete_reason', '').strip()
    if not reason or len(reason) < 5:
        flash('Proporciona una justificación (mínimo 5 caracteres) para eliminar la reserva.', 'error')
        return redirect(url_for('admin.reservation_detail', reservation_id=reservation_id))
    success, message = reservation_service.delete_reservation_admin(reservation_id, session['user_id'], reason)
    # Podríamos almacenar la razón en logs/notifications si se desea, por ahora solo mensaje.
    if success:
        flash(f'{message}. Motivo: {reason}', 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('admin.reservations'))


@admin_bp.route('/deletions')
@admin_required
def deletions_log():
    """Lista de eliminaciones de reservas (bitácora)"""
    space_id = request.args.get('space_id') or None
    user_id = request.args.get('user_id') or None
    admin_id = request.args.get('admin_id') or None
    date_from = request.args.get('date_from') or None
    date_to = request.args.get('date_to') or None

    logs = reservation_deletion_repo.get_logs(
        limit=200,
        space_id=space_id,
        user_id=user_id,
        admin_id=admin_id,
        date_from=date_from,
        date_to=date_to,
    )
    spaces = {s['id']: s for s in space_service.get_all_spaces()}
    users = {u['id']: u for u in auth_service.user_repo.get_all_users()} if hasattr(auth_service, 'user_repo') else {}
    return render_template(
        'admin/deletions.html',
        logs=logs,
        spaces=spaces,
        users=users,
        space_id=space_id,
        user_id=user_id,
        admin_id=admin_id,
        date_from=date_from,
        date_to=date_to,
    )

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


@admin_bp.route('/schedules', methods=['GET', 'POST'])
@admin_required
def schedules():
    """Gestión de horarios fijos de aulas"""
    spaces = space_service.get_all_spaces()
    spaces_by_id = {s['id']: s for s in spaces}
    selected_space_id = request.args.get('space_id') or None

    if request.method == 'POST':
        space_id = request.form.get('space_id')
        weekday_raw = request.form.get('weekday')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        description = request.form.get('description')

        if not all([space_id, weekday_raw, start_time, end_time]):
            flash('Completa espacio, día y horas.', 'error')
            return redirect(url_for('admin.schedules', space_id=space_id or selected_space_id))

        try:
            weekday = int(weekday_raw)
        except ValueError:
            flash('Día inválido.', 'error')
            return redirect(url_for('admin.schedules', space_id=space_id or selected_space_id))

        success, message, _ = class_schedule_service.create_schedule(
            space_id, weekday, start_time, end_time, description
        )
        flash(message, 'success' if success else 'error')
        return redirect(url_for('admin.schedules', space_id=space_id))

    schedules_list = class_schedule_service.get_schedules(selected_space_id)
    return render_template(
        'admin/schedules.html',
        schedules=schedules_list,
        spaces=spaces,
        spaces_by_id=spaces_by_id,
        selected_space_id=selected_space_id,
    )


@admin_bp.route('/schedules/<schedule_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_schedule(schedule_id):
    schedule = class_schedule_service.get_by_id(schedule_id)
    if not schedule:
        flash('Horario no encontrado', 'error')
        return redirect(url_for('admin.schedules'))

    spaces = space_service.get_all_spaces()

    if request.method == 'POST':
        space_id = request.form.get('space_id')
        weekday_raw = request.form.get('weekday')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        description = request.form.get('description')

        try:
            weekday = int(weekday_raw)
        except ValueError:
            flash('Día inválido.', 'error')
            return redirect(url_for('admin.edit_schedule', schedule_id=schedule_id))

        success, message, _ = class_schedule_service.update_schedule(
            schedule_id, space_id, weekday, start_time, end_time, description
        )
        flash(message, 'success' if success else 'error')
        if success:
            return redirect(url_for('admin.schedules', space_id=space_id))

    return render_template('admin/schedule_edit.html', schedule=schedule, spaces=spaces)


@admin_bp.route('/schedules/<schedule_id>/delete', methods=['POST'])
@admin_required
def delete_schedule(schedule_id):
    deleted = class_schedule_service.delete_schedule(schedule_id)
    flash('Horario eliminado' if deleted else 'No se pudo eliminar el horario', 'success' if deleted else 'error')
    return redirect(url_for('admin.schedules'))
