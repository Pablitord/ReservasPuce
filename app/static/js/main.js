// Script principal de la aplicación

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar notificaciones si el usuario está autenticado
    if (document.getElementById('notificationsDropdown')) {
        initializeNotifications();
        // Actualizar contador cada 30 segundos
        setInterval(updateNotificationCount, 30000);
    }
});

/**
 * Inicializa el sistema de notificaciones
 */
function initializeNotifications() {
    loadNotifications();
    updateNotificationCount();
    
    // Event listener para marcar todas como leídas
    const markAllReadBtn = document.getElementById('markAllRead');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            markAllNotificationsAsRead();
        });
    }
}

/**
 * Carga las notificaciones en el dropdown
 */
function loadNotifications() {
    fetch('/notifications/api/list?unread_only=true')
        .then(response => response.json())
        .then(notifications => {
            const notificationsList = document.getElementById('notificationsList');
            if (!notificationsList) return;
            
            if (notifications.length === 0) {
                notificationsList.innerHTML = '<div class="text-center p-3 text-muted">No tienes notificaciones nuevas</div>';
                return;
            }
            
            let html = '';
            notifications.slice(0, 10).forEach(notification => {
                const icon = getNotificationIcon(notification.type);
                const link = notification.link || '#';
                html += `
                    <li>
                        <a class="dropdown-item notification-item ${notification.read ? '' : 'fw-bold'}" href="${link}" data-notification-id="${notification.id}">
                            <div class="d-flex align-items-start">
                                <i class="${icon} me-2"></i>
                                <div class="flex-grow-1">
                                    <div class="fw-bold">${notification.title}</div>
                                    <small class="text-muted">${notification.message}</small>
                                    <div class="text-muted" style="font-size: 0.75rem;">${formatDate(notification.created_at)}</div>
                                </div>
                            </div>
                        </a>
                    </li>
                `;
            });
            
            notificationsList.innerHTML = html;
            
            // Agregar event listeners para marcar como leídas al hacer clic
            document.querySelectorAll('.notification-item').forEach(item => {
                item.addEventListener('click', function() {
                    const notificationId = this.getAttribute('data-notification-id');
                    if (notificationId) {
                        markNotificationAsRead(notificationId);
                    }
                });
            });
        })
        .catch(error => {
            console.error('Error cargando notificaciones:', error);
            const notificationsList = document.getElementById('notificationsList');
            if (notificationsList) {
                notificationsList.innerHTML = '<div class="text-center p-3 text-danger">Error al cargar notificaciones</div>';
            }
        });
}

/**
 * Actualiza el contador de notificaciones no leídas
 */
function updateNotificationCount() {
    fetch('/notifications/api/unread_count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notificationBadge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count > 99 ? '99+' : data.count;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error actualizando contador de notificaciones:', error);
        });
}

/**
 * Marca una notificación como leída
 */
function markNotificationAsRead(notificationId) {
    fetch(`/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotificationCount();
                loadNotifications();
            }
        })
        .catch(error => {
            console.error('Error marcando notificación como leída:', error);
        });
}

/**
 * Marca todas las notificaciones como leídas
 */
function markAllNotificationsAsRead() {
    fetch('/notifications/mark_all_read', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotificationCount();
                loadNotifications();
            }
        })
        .catch(error => {
            console.error('Error marcando todas las notificaciones como leídas:', error);
        });
}

/**
 * Obtiene el icono según el tipo de notificación
 */
function getNotificationIcon(type) {
    const icons = {
        'info': 'bi bi-info-circle text-primary',
        'success': 'bi bi-check-circle text-success',
        'warning': 'bi bi-exclamation-triangle text-warning',
        'error': 'bi bi-x-circle text-danger'
    };
    return icons[type] || icons['info'];
}

/**
 * Formatea una fecha para mostrarla
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
        return `Hace ${days} día${days > 1 ? 's' : ''}`;
    } else if (hours > 0) {
        return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
    } else if (minutes > 0) {
        return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    } else {
        return 'Hace unos momentos';
    }
}
