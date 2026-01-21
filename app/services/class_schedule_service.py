from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from app.repositories.supabase.class_schedule_repo import ClassScheduleRepository


class ClassScheduleService:
    """Servicio para horarios fijos de aulas (bloqueos por clases)."""

    def __init__(self):
        self.repo = ClassScheduleRepository()

    def _parse_time(self, time_str: str) -> datetime:
        """Convierte HH:MM o HH:MM:SS a datetime base para comparar."""
        parts = str(time_str).strip().split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        second = int(parts[2]) if len(parts) > 2 else 0
        return datetime(2000, 1, 1, hour, minute, second)

    def _validate_times(self, start_time: str, end_time: str) -> Optional[str]:
        try:
            start = self._parse_time(start_time)
            end = self._parse_time(end_time)
        except Exception:
            return "Horas inválidas, usa formato HH:MM"
        if end <= start:
            return "La hora de fin debe ser mayor que la hora de inicio"
        return None

    def _check_overlap(
        self,
        schedules: List[Dict[str, Any]],
        start_time: str,
        end_time: str,
        exclude_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Devuelve el horario con el que se solapa, si existe."""
        new_start = self._parse_time(start_time)
        new_end = self._parse_time(end_time)
        for sch in schedules:
            if exclude_id and sch.get("id") == exclude_id:
                continue
            s_start = self._parse_time(sch.get("start_time"))
            s_end = self._parse_time(sch.get("end_time"))
            if new_start < s_end and s_start < new_end:
                return sch
        return None

    def get_schedules(
        self, space_id: Optional[str] = None, weekday: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        return self.repo.get_schedules(space_id, weekday)

    def get_by_id(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(schedule_id)

    def create_schedule(
        self,
        space_id: str,
        weekday: int,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        if weekday < 0 or weekday > 6:
            return False, "El día debe estar entre lunes (0) y domingo (6)", None
        err = self._validate_times(start_time, end_time)
        if err:
            return False, err, None
        existing = self.repo.get_schedules(space_id, weekday)
        overlap = self._check_overlap(existing, start_time, end_time)
        if overlap:
            return (
                False,
                "Existe un horario de clase que se superpone",
                overlap,
            )
        created = self.repo.create_schedule(
            space_id, weekday, start_time, end_time, description
        )
        if not created:
            return False, "Error al crear el horario", None
        return True, "Horario creado", created

    def update_schedule(
        self,
        schedule_id: str,
        space_id: str,
        weekday: int,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        if weekday < 0 or weekday > 6:
            return False, "El día debe estar entre lunes (0) y domingo (6)", None
        err = self._validate_times(start_time, end_time)
        if err:
            return False, err, None
        existing = self.repo.get_schedules(space_id, weekday)
        overlap = self._check_overlap(existing, start_time, end_time, exclude_id=schedule_id)
        if overlap:
            return False, "Existe un horario de clase que se superpone", overlap
        updated = self.repo.update_schedule(
            schedule_id, space_id, weekday, start_time, end_time, description
        )
        if not updated:
            return False, "Error al actualizar el horario", None
        return True, "Horario actualizado", updated

    def delete_schedule(self, schedule_id: str) -> bool:
        return self.repo.delete_schedule(schedule_id)

    def find_conflict_with_class(
        self,
        space_id: str,
        date_str: str,
        start_time: str,
        end_time: str,
    ) -> Optional[Dict[str, Any]]:
        """Devuelve el horario de clase que se solapa con la reserva, si existe."""
        try:
            weekday = datetime.strptime(date_str, "%Y-%m-%d").weekday()  # 0 lunes
        except Exception:
            return None
        schedules = self.repo.get_schedules(space_id, weekday)
        return self._check_overlap(schedules, start_time, end_time)
