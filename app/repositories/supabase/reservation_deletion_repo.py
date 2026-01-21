from typing import Optional, Dict, Any
from app.repositories.supabase.client import get_supabase_client


class ReservationDeletionRepository:
    """Repositorio para bitácora de eliminaciones de reservas."""

    def __init__(self):
        self.client = get_supabase_client()
        self.table = "reservation_deletions"

    def log_deletion(
        self,
        reservation: Dict[str, Any],
        admin_id: Optional[str],
        reason: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            data = {
                "reservation_id": reservation.get("id"),
                "user_id": reservation.get("user_id"),
                "space_id": reservation.get("space_id"),
                "date": reservation.get("date"),
                "start_time": reservation.get("start_time"),
                "end_time": reservation.get("end_time"),
                "admin_id": admin_id,
                "reason": reason,
            }
            resp = self.client.table(self.table).insert(data).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            print(f"Error registrando eliminación de reserva: {e}")
            return None

    def get_logs(self, limit: int = 100) -> list[Dict[str, Any]]:
        """Obtiene registros de eliminaciones para auditoría."""
        try:
            resp = (
                self.client.table(self.table)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return resp.data or []
        except Exception as e:
            print(f"Error obteniendo bitácora de eliminaciones: {e}")
            return []
