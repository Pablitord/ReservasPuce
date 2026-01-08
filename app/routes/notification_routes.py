from flask import Blueprint, jsonify, request, session, redirect, url_for
from app.services.notification_service import NotificationService
from app.deps import login_required

notification_bp = Blueprint('notification', __name__)
notification_service = NotificationService()

@notification_bp.route('/api/unread_count')
@login_required
def get_unread_count():
    """API endpoint para obtener el conteo de notificaciones no leídas"""
    count = notification_service.get_unread_count(session['user_id'])
    return jsonify({'count': count})

@notification_bp.route('/api/list')
@login_required
def get_notifications():
    """API endpoint para obtener las notificaciones del usuario"""
    unread_only = request.args.get('unread_only', 'false') == 'true'
    notifications = notification_service.get_user_notifications(session['user_id'], unread_only)
    return jsonify(notifications)

@notification_bp.route('/<notification_id>/read', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    """Marca una notificación como leída"""
    success = notification_service.mark_as_read(notification_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@notification_bp.route('/mark_all_read', methods=['POST'])
@login_required
def mark_all_as_read():
    """Marca todas las notificaciones como leídas"""
    success = notification_service.mark_all_as_read(session['user_id'])
    if success:
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@notification_bp.route('/<notification_id>')
@login_required
def view_notification(notification_id):
    """Vista de una notificación específica"""
    notifications = notification_service.get_user_notifications(session['user_id'])
    notification = next((n for n in notifications if n['id'] == notification_id), None)
    
    if not notification:
        return redirect(url_for('user.calendar'))
    
    # Marcar como leída
    notification_service.mark_as_read(notification_id)
    
    # Redirigir al link si existe
    if notification.get('link'):
        return redirect(notification['link'])
    
    # Redirigir según el tipo de usuario
    if session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('user.calendar'))
