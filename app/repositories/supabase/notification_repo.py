from app.repositories.supabase.client import get_supabase_client
from typing import Optional, Dict, Any, List

class NotificationRepository:
    """Repositorio para operaciones de notificaciones"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = 'notifications'
    
    def create_notification(self, user_id: str, title: str, message: str, 
                           type: str = 'info', link: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Crea una nueva notificación"""
        try:
            data = {
                'user_id': user_id,
                'title': title,
                'message': message,
                'type': type,
                'read': False
            }
            if link:
                data['link'] = link
            
            response = self.client.table(self.table).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creando notificación: {e}")
            return None
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Obtiene las notificaciones de un usuario"""
        try:
            query = self.client.table(self.table).select('*').eq('user_id', user_id)
            if unread_only:
                query = query.eq('read', False)
            response = query.order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo notificaciones: {e}")
            return []
    
    def mark_as_read(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Marca una notificación como leída"""
        try:
            response = self.client.table(self.table).update({'read': True}).eq('id', notification_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error marcando notificación como leída: {e}")
            return None
    
    def mark_all_as_read(self, user_id: str) -> bool:
        """Marca todas las notificaciones de un usuario como leídas"""
        try:
            response = self.client.table(self.table).update({'read': True}).eq('user_id', user_id).eq('read', False).execute()
            return True
        except Exception as e:
            print(f"Error marcando todas las notificaciones como leídas: {e}")
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """Obtiene el conteo de notificaciones no leídas"""
        try:
            response = self.client.table(self.table).select('id', count='exact').eq('user_id', user_id).eq('read', False).execute()
            return response.count if response.count else 0
        except Exception as e:
            print(f"Error obteniendo conteo de notificaciones no leídas: {e}")
            return 0
