from app.repositories.supabase.reservation_repo import ReservationRepository
from app.repositories.supabase.space_repo import SpaceRepository
from app.repositories.supabase.user_repo import UserRepository
from typing import Dict, Any

class AdminService:
    """Servicio para operaciones de administración"""
    
    def __init__(self):
        self.reservation_repo = ReservationRepository()
        self.space_repo = SpaceRepository()
        self.user_repo = UserRepository()
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas para el dashboard"""
        all_reservations = self.reservation_repo.get_all_reservations()
        pending = [r for r in all_reservations if r.get('status') == 'pending']
        approved = [r for r in all_reservations if r.get('status') == 'approved']
        rejected = [r for r in all_reservations if r.get('status') == 'rejected']
        
        all_spaces = self.space_repo.get_all_spaces()
        all_users = self.user_repo.get_all_users()
        
        return {
            'total_reservations': len(all_reservations),
            'pending_reservations': len(pending),
            'approved_reservations': len(approved),
            'rejected_reservations': len(rejected),
            'total_spaces': len(all_spaces),
            'total_users': len(all_users)
        }
    
    def get_pending_reservations(self) -> list:
        """Obtiene las reservas pendientes"""
        return self.reservation_repo.get_pending_reservations()
    
    def get_all_reservations(self) -> list:
        """Obtiene todas las reservas"""
        return self.reservation_repo.get_all_reservations()
