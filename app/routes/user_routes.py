from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.services.reservation_service import ReservationService
from app.services.space_service import SpaceService
from app.deps import login_required

user_bp = Blueprint('user', __name__)
reservation_service = ReservationService()
space_service = SpaceService()

@user_bp.route('/calendar')
@login_required
def calendar():
    """Vista del calendario de reservas"""
    spaces = space_service.get_all_spaces()
    return render_template('user/calendar.html', spaces=spaces)

@user_bp.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    """Formulario y creación de reserva"""
    from datetime import date
    if request.method == 'POST':
        space_id = request.form.get('space_id')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        justification = request.form.get('justification')
        
        if not all([space_id, date, start_time, end_time, justification]):
            flash('Por favor completa todos los campos', 'error')
            spaces = space_service.get_all_spaces()
            return render_template('user/reserve_form.html', spaces=spaces)
        
        # Validar que end_time sea mayor que start_time
        if end_time <= start_time:
            flash('La hora de finalización debe ser mayor que la hora de inicio', 'error')
            spaces = space_service.get_all_spaces()
            return render_template('user/reserve_form.html', spaces=spaces)
        
        success, message, reservation = reservation_service.create_reservation(
            user_id=session['user_id'],
            space_id=space_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            justification=justification
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('user.my_reservations'))
        else:
            flash(message, 'error')
    
    spaces = space_service.get_all_spaces()
    min_date = date.today().isoformat()
    return render_template('user/reserve_form.html', spaces=spaces, min_date=min_date)

@user_bp.route('/my_reservations')
@login_required
def my_reservations():
    """Vista de mis reservas"""
    reservations = reservation_service.get_user_reservations(session['user_id'])
    return render_template('user/my_reservations.html', reservations=reservations)

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
    
    # Obtener TODAS las reservas aprobadas para el calendario general
    all_reservations = reservation_service.get_all_reservations()
    
    # Filtrar solo las aprobadas y pendientes para mostrar en el calendario
    visible_reservations = [r for r in all_reservations if r.get('status') in ['approved', 'pending']]
    
    # Si se especifica un espacio, filtrar por espacio
    if space_id:
        visible_reservations = [r for r in visible_reservations if r.get('space_id') == space_id]
    
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
        
        events.append({
            'id': res['id'],
            'title': space_name,
            'start': f"{res['date']}T{res['start_time']}",
            'end': f"{res['date']}T{res['end_time']}",
            'status': status,
            'statusText': status_text,
            'spaceName': space_name,
            'userName': user_name,
            'startTime': res['start_time'],
            'endTime': res['end_time'],
            'color': '#dc3545' if status == 'approved' else '#ffc107',  # Rojo para aprobadas, amarillo para pendientes
            'backgroundColor': '#dc3545' if status == 'approved' else '#ffc107',
            'borderColor': '#c82333' if status == 'approved' else '#e0a800',
            'extendedProps': {
                'status': status,
                'spaceName': space_name,
                'userName': user_name,
                'justification': res.get('justification', '')
            }
        })
    
    return jsonify(events)
