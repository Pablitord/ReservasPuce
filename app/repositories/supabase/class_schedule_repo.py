from app.repositories.supabase.client import get_supabase_client
from typing import Optional, Dict, Any, List


class ClassScheduleRepository:
    """Repositorio para horarios fijos de aulas (bloqueos por clases)."""

    def __init__(self):
        self.client = get_supabase_client()
        self.table = "class_schedules"

    def get_schedules(
        self,
        space_id: Optional[str] = None,
        weekday: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        try:
            query = self.client.table(self.table).select("*")
            if space_id:
                query = query.eq("space_id", space_id)
            if weekday is not None:
                query = query.eq("weekday", weekday)
            response = query.order("weekday").order("start_time").execute()
            return response.data or []
        except Exception as e:
            print(f"Error obteniendo horarios de clase: {e}")
            return []

    def get_by_id(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = (
                self.client.table(self.table)
                .select("*")
                .eq("id", schedule_id)
                .maybe_single()
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error obteniendo horario por id: {e}")
            return None

    def create_schedule(
        self,
        space_id: str,
        weekday: int,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            data = {
                "space_id": space_id,
                "weekday": weekday,
                "start_time": start_time,
                "end_time": end_time,
                "description": description or None,
            }
            response = self.client.table(self.table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creando horario de clase: {e}")
            return None

    def update_schedule(
        self,
        schedule_id: str,
        space_id: str,
        weekday: int,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            data = {
                "space_id": space_id,
                "weekday": weekday,
                "start_time": start_time,
                "end_time": end_time,
                "description": description or None,
            }
            response = (
                self.client.table(self.table)
                .update(data)
                .eq("id", schedule_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error actualizando horario de clase: {e}")
            return None

    def delete_schedule(self, schedule_id: str) -> bool:
        try:
            response = (
                self.client.table(self.table).delete().eq("id", schedule_id).execute()
            )
            return bool(response.data is not None)
        except Exception as e:
            print(f"Error eliminando horario de clase: {e}")
            return False
