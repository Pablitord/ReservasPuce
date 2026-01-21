from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.services.reservation_service import ReservationService
from app.services.space_service import SpaceService
from app.services.class_schedule_service import ClassScheduleService
from app.deps import login_required

user_bp = Blueprint('user', __name__)
reservation_service = ReservationService()
space_service = SpaceService()
class_schedule_service = ClassScheduleService()

@user_bp.route('/calendar')
@login_required
def calendar():
    """Vista del calendario de reservas"""
    spaces_by_floor = space_service.get_spaces_grouped_by_floor()
    return render_template('user/calendar.html', spaces_by_floor=spaces_by_floor)

@user_bp.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    """Formulario y creación de reserva"""
    from datetime import date as date_module

    if request.method == 'POST':
        space_id = request.form.get('space_id')
        reservation_date = request.form.get('date')  # Renombrar para evitar conflicto
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        justification = request.form.get('justification')
        
        if not all([space_id, reservation_date, start_time, end_time, justification]):
            flash('Por favor completa todos los campos', 'error')
            spaces_by_floor = space_service.get_spaces_grouped_by_floor()
            min_date = date_module.today().isoformat()
            return render_template('user/reserve_form.html', spaces_by_floor=spaces_by_floor, min_date=min_date)
        
        # Validar que end_time sea mayor que start_time
        if end_time <= start_time:
            flash('La hora de finalización debe ser mayor que la hora de inicio', 'error')
            spaces_by_floor = space_service.get_spaces_grouped_by_floor()
            min_date = date_module.today().isoformat()
            return render_template('user/reserve_form.html', spaces_by_floor=spaces_by_floor, min_date=min_date)
        
        success, message, reservation = reservation_service.create_reservation(
            user_id=session['user_id'],
            space_id=space_id,
            date=reservation_date,  # Usar la variable renombrada
            start_time=start_time,
            end_time=end_time,
            justification=justification
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('user.my_reservations'))
        else:
            flash(message, 'error')
    
    spaces_by_floor = space_service.get_spaces_grouped_by_floor()
    min_date = date_module.today().isoformat()  # Usar date_module en lugar de date
    return render_template('user/reserve_form.html', spaces_by_floor=spaces_by_floor, min_date=min_date)

@user_bp.route('/my_reservations')
@login_required
def my_reservations():
    """Vista de mis reservas"""
    reservations = reservation_service.get_user_reservations(session['user_id'])
    return render_template('user/my_reservations.html', reservations=reservations)

@user_bp.route('/my_reservations/<reservation_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reservation(reservation_id):
    """Editar una reserva pendiente del usuario"""
    from datetime import date as date_module
    reservation = reservation_service.get_reservation_by_id(reservation_id)
    if not reservation:
        flash('Reserva no encontrada', 'error')
        return redirect(url_for('user.my_reservations'))
    if reservation.get('user_id') != session['user_id']:
        flash('No tienes permisos para editar esta reserva', 'error')
        return redirect(url_for('user.my_reservations'))
    if reservation.get('status') != 'pending':
        flash('Solo puedes editar reservas pendientes', 'error')
        return redirect(url_for('user.reservation_detail', reservation_id=reservation_id))

    if request.method == 'POST':
        space_id = request.form.get('space_id')
        reservation_date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        justification = request.form.get('justification')

        if not all([space_id, reservation_date, start_time, end_time, justification]):
            flash('Por favor completa todos los campos', 'error')
            spaces_by_floor = space_service.get_spaces_grouped_by_floor()
            min_date = date_module.today().isoformat()
            return render_template(
                'user/reserve_edit.html',
                reservation=reservation,
                spaces_by_floor=spaces_by_floor,
                min_date=min_date,
                selected_space_id=space_id,
                selected_date=reservation_date,
                selected_start=start_time,
                selected_end=end_time,
                justification_val=justification
            )

        if end_time <= start_time:
            flash('La hora de finalización debe ser mayor que la hora de inicio', 'error')
            spaces_by_floor = space_service.get_spaces_grouped_by_floor()
            min_date = date_module.today().isoformat()
            return render_template(
                'user/reserve_edit.html',
                reservation=reservation,
                spaces_by_floor=spaces_by_floor,
                min_date=min_date,
                selected_space_id=space_id,
                selected_date=reservation_date,
                selected_start=start_time,
                selected_end=end_time,
                justification_val=justification
            )

        success, message, updated = reservation_service.update_reservation(
            reservation_id=reservation_id,
            user_id=session['user_id'],
            space_id=space_id,
            date=reservation_date,
            start_time=start_time,
            end_time=end_time,
            justification=justification
        )
        flash(message, 'success' if success else 'error')
        if success:
            return redirect(url_for('user.reservation_detail', reservation_id=reservation_id))

    spaces_by_floor = space_service.get_spaces_grouped_by_floor()
    min_date = date_module.today().isoformat()
    return render_template(
        'user/reserve_edit.html',
        reservation=reservation,
        spaces_by_floor=spaces_by_floor,
        min_date=min_date,
        selected_space_id=reservation.get('space_id'),
        selected_date=str(reservation.get('date')),
        selected_start=str(reservation.get('start_time'))[:5] if reservation.get('start_time') else '',
        selected_end=str(reservation.get('end_time'))[:5] if reservation.get('end_time') else '',
        justification_val=reservation.get('justification', '')
    )
@user_bp.route('/my_reservations/<reservation_id>')
@login_required
def reservation_detail(reservation_id):
    """Detalle de una reserva específica"""
    reservation = reservation_service.get_reservation_by_id(reservation_id)
    if not reservation:
        flash('Reserva no encontrada', 'error')
        return redirect(url_for('user.my_reservations'))
    
    # Verificar que la reserva pertenece al usuario
    if reservation['user_id'] != session['user_id'] and session.get('role') != 'admin':
        flash('No tienes permisos para ver esta reserva', 'error')
        return redirect(url_for('user.my_reservations'))
    
    return render_template('user/reservation_detail.html', reservation=reservation)

@user_bp.route('/api/reservations')
@login_required
def get_reservations_api():
    """API endpoint para obtener reservas (para el calendario) - muestra TODAS las reservas aprobadas"""
    space_id = request.args.get('space_id')
    floor = request.args.get('floor')
    date_filter = request.args.get('date')
    
    # Obtener TODAS las reservas aprobadas para el calendario general
    all_reservations = reservation_service.get_all_reservations()
    
    # Filtrar solo las aprobadas y pendientes para mostrar en el calendario
    visible_reservations = [r for r in all_reservations if r.get('status') in ['approved', 'pending']]
    
    # Si se especifica un espacio, filtrar por espacio
    if space_id:
        visible_reservations = [r for r in visible_reservations if r.get('space_id') == space_id]

    # Si se especifica una fecha exacta, filtrar por esa fecha
    if date_filter:
        visible_reservations = [r for r in visible_reservations if str(r.get('date')) == date_filter]
    
    def resolve_floor(reservation):
        spaces = reservation.get('spaces')
        space = None
        if isinstance(spaces, dict):
            space = spaces
        elif isinstance(spaces, list) and spaces:
            space = spaces[0]
        if not space:
            return None
        floor_value = space.get('floor')
        if floor_value:
            return floor_value
        name = (space.get('name') or '').upper()
        if name.startswith('A-0'):
            return 'planta_baja'
        if name.startswith('A-1'):
            return 'piso_1'
        if name.startswith('A-2'):
            return 'piso_2'
        if (space.get('type') or '').lower() == 'auditorio':
            return 'planta_baja'
        return None
    
    if floor:
        visible_reservations = [
            r for r in visible_reservations if resolve_floor(r) == floor
        ]
    
    # Formatear para el calendario
    events = []
    for res in visible_reservations:
        space_name = 'Espacio'
        if res.get('spaces'):
            if isinstance(res.get('spaces'), dict):
                space_name = res.get('spaces', {}).get('name', 'Espacio')
            elif isinstance(res.get('spaces'), list) and len(res.get('spaces', [])) > 0:
                space_name = res.get('spaces')[0].get('name', 'Espacio')
        
        status = res.get('status', 'pending')
        status_text = 'Aprobada' if status == 'approved' else 'Pendiente'
        user_name = 'Usuario'
        if res.get('users'):
            if isinstance(res.get('users'), dict):
                user_name = res.get('users', {}).get('name', 'Usuario')
            elif isinstance(res.get('users'), list) and len(res.get('users', [])) > 0:
                user_name = res.get('users')[0].get('name', 'Usuario')
        
        # Formatear fecha y hora correctamente para FullCalendar
        date_str = str(res['date'])  # Asegurar que sea string
        start_time = str(res['start_time']) if res.get('start_time') else '00:00:00'
        end_time = str(res['end_time']) if res.get('end_time') else '23:59:59'
        
        # Normalizar formato de hora (asegurar HH:MM:SS)
        if ':' in start_time:
            parts = start_time.split(':')
            if len(parts) == 2:
                start_time = f"{parts[0]}:{parts[1]}:00"
            elif len(parts) == 3:
                start_time = f"{parts[0]}:{parts[1]}:{parts[2]}"
        
        if ':' in end_time:
            parts = end_time.split(':')
            if len(parts) == 2:
                end_time = f"{parts[0]}:{parts[1]}:00"
            elif len(parts) == 3:
                end_time = f"{parts[0]}:{parts[1]}:{parts[2]}"
        
        # Crear fecha/hora completa en formato ISO 8601
        # Formato: YYYY-MM-DDTHH:MM:SS
        start_datetime = f"{date_str}T{start_time}"
        end_datetime = f"{date_str}T{end_time}"
        
        # Para la vista de mes, mostrar solo el día (sin hora en el título)
        # La hora se mostrará en tooltips y al hacer clic
        title = f"{space_name}"
        
        events.append({
            'id': res['id'],
            'title': title,
            'start': start_datetime,
            'end': end_datetime,
            'allDay': False,  # NO es evento de todo el día - tiene hora específica
            'display': 'block',
            'status': status,
            'statusText': status_text,
            'spaceName': space_name,
            'userName': user_name,
            'startTime': start_time[:5],  # Solo HH:MM para mostrar
            'endTime': end_time[:5],
            'color': '#28a745' if status == 'approved' else '#ffc107',  # Verde para aprobadas
            'backgroundColor': '#28a745' if status == 'approved' else '#ffc107',  # Verde para aprobadas
            'borderColor': '#218838' if status == 'approved' else '#e0a800',  # Verde oscuro para borde
            'textColor': 'white',
            'extendedProps': {
                'status': status,
                'spaceName': space_name,
                'userName': user_name,
                'justification': res.get('justification', ''),
                'startTime': start_time[:5],
                'endTime': end_time[:5]
            }
        })
    
    return jsonify(events)


@user_bp.route('/api/spaces/<space_id>/schedule')
@login_required
def get_space_schedule(space_id):
    """Devuelve el horario de clases de un espacio. Param weekday opcional (0=lunes..6=domingo)."""
    weekday = request.args.get('weekday')
    weekday_int = None
    if weekday is not None:
        try:
            weekday_int = int(weekday)
            if weekday_int < 0 or weekday_int > 6:
                return jsonify({"error": "weekday debe estar entre 0 y 6"}), 400
        except ValueError:
            return jsonify({"error": "weekday inválido"}), 400
    schedules = class_schedule_service.get_schedules(space_id, weekday_int)
    return jsonify(schedules)
