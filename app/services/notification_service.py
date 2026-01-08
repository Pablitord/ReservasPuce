from app.repositories.supabase.notification_repo import NotificationRepository
from typing import List, Dict, Any

class NotificationService:
    """Servicio para operaciones de notificaciones"""
    
    def __init__(self):
        self.notification_repo = NotificationRepository()
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Obtiene las notificaciones de un usuario"""
        return self.notification_repo.get_user_notifications(user_id, unread_only)
    
    def get_unread_count(self, user_id: str) -> int:
        """Obtiene el conteo de notificaciones no leídas"""
        return self.notification_repo.get_unread_count(user_id)
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Marca una notificación como leída"""
        result = self.notification_repo.mark_as_read(notification_id)
        return result is not None
    
    def mark_all_as_read(self, user_id: str) -> bool:
        """Marca todas las notificaciones como leídas"""
        return self.notification_repo.mark_all_as_read(user_id)
