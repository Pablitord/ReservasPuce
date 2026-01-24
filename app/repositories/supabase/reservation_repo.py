from app.repositories.supabase.client import get_supabase_client
from typing import Optional, Dict, Any, List
from datetime import datetime, date

class ReservationRepository:
    """Repositorio para operaciones de reservas"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = 'reservations'
    
    def create_reservation(self, user_id: str, space_id: str, date: str, start_time: str, 
                          end_time: str, justification: str, status: str = 'pending') -> Optional[Dict[str, Any]]:
        """Crea una nueva reserva"""
        try:
            data = {
                'user_id': user_id,
                'space_id': space_id,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'justification': justification,
                'status': status
            }
            response = self.client.table(self.table).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creando reserva: {e}")
            return None
    
    def get_reservation_by_id(self, reservation_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva por ID con información relacionada"""
        try:
            # Especificar la relación correcta: users!reservations_user_id_fkey es el usuario que hizo la reserva
            response = self.client.table(self.table).select('*, spaces(*), users!reservations_user_id_fkey(*)').eq('id', reservation_id).execute()
            if response.data and len(response.data) > 0:
                reservation = response.data[0]
                # Agregar el usuario como 'user' para facilitar el acceso en templates
                if reservation.get('users'):
                    reservation['user'] = reservation['users']
                return reservation
            
            # Si no funciona con joins, intentar sin joins
            response = self.client.table(self.table).select('*').eq('id', reservation_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            return None
        except Exception as e:
            print(f"Error obteniendo reserva por ID '{reservation_id}': {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_reservations_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene todas las reservas de un usuario"""
        try:
            response = self.client.table(self.table).select('*, spaces(*)').eq('user_id', user_id).order('date', desc=True).order('start_time').execute()
            reservations = response.data if response.data else []
            # Agregar 'user' para consistencia
            for res in reservations:
                if not res.get('user'):
                    res['user'] = None
            return reservations
        except Exception as e:
            print(f"Error obteniendo reservas por usuario: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_reservations_by_space_and_date(self, space_id: str, date: str) -> List[Dict[str, Any]]:
        """Obtiene reservas de un espacio en una fecha específica"""
        try:
            response = self.client.table(self.table).select('*').eq('space_id', space_id).eq('date', date).execute()
            # Filtrar solo las reservas aprobadas o pendientes
            reservations = response.data if response.data else []
            return [r for r in reservations if r.get('status') in ['pending', 'approved']]
        except Exception as e:
            print(f"Error obteniendo reservas por espacio y fecha: {e}")
            return []
    
    def get_pending_reservations(self) -> List[Dict[str, Any]]:
        """Obtiene todas las reservas pendientes"""
        try:
            # Especificar la relación correcta: users!reservations_user_id_fkey es el usuario que hizo la reserva
            response = self.client.table(self.table).select('*, spaces(*), users!reservations_user_id_fkey(*)').eq('status', 'pending').order('created_at', desc=True).execute()
            reservations = response.data if response.data else []
            # Agregar 'user' para facilitar acceso en templates
            for res in reservations:
                if res.get('users'):
                    res['user'] = res['users']
            return reservations
        except Exception as e:
            print(f"Error obteniendo reservas pendientes: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_reservation_status(self, reservation_id: str, status: str, admin_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Actualiza el estado de una reserva"""
        try:
            data = {'status': status}
            if admin_id:
                data['admin_id'] = admin_id
            if status == 'approved' or status == 'rejected':
                data['reviewed_at'] = datetime.now().isoformat()
            
            response = self.client.table(self.table).update(data).eq('id', reservation_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error actualizando estado de reserva: {e}")
            return None
    
    def get_all_reservations(self) -> List[Dict[str, Any]]:
        """Obtiene todas las reservas"""
        try:
            # Especificar la relación correcta: users!reservations_user_id_fkey es el usuario que hizo la reserva
            response = self.client.table(self.table).select('*, spaces(*), users!reservations_user_id_fkey(*)').order('created_at', desc=True).execute()
            reservations = response.data if response.data else []
            # Agregar 'user' para facilitar acceso en templates
            for res in reservations:
                if res.get('users'):
                    res['user'] = res['users']
            return reservations
        except Exception as e:
            print(f"Error obteniendo todas las reservas: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_approved_reservations_by_date(self, date: str, only_without_reminder: bool = True) -> List[Dict[str, Any]]:
        """Obtiene reservas aprobadas de una fecha específica"""
        try:
            query = (
                self.client.table(self.table)
                .select('*, spaces(*), users!reservations_user_id_fkey(*)')
                .eq('status', 'approved')
                .eq('date', date)
            )
            if only_without_reminder:
                query = query.is_('reminder_sent_at', None)
            response = query.execute()
            reservations = response.data if response.data else []
            for res in reservations:
                if res.get('users'):
                    res['user'] = res['users']
            return reservations
        except Exception as e:
            print(f"Error obteniendo reservas aprobadas por fecha: {e}")
            return []

    def mark_confirmation_sent(self, reservation_id: str) -> bool:
        """Marca la confirmación de correo enviada"""
        try:
            data = {'confirmation_sent_at': datetime.now().isoformat()}
            response = self.client.table(self.table).update(data).eq('id', reservation_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error marcando confirmación enviada: {e}")
            return False

    def mark_reminder_sent(self, reservation_id: str) -> bool:
        """Marca el recordatorio de correo enviado"""
        try:
            data = {'reminder_sent_at': datetime.now().isoformat()}
            response = self.client.table(self.table).update(data).eq('id', reservation_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error marcando recordatorio enviado: {e}")
            return False
    
    def check_time_conflict(self, space_id: str, date: str, start_time: str, end_time: str, exclude_id: Optional[str] = None) -> bool:
        """Verifica si hay conflicto de horario"""
        try:
            # Función auxiliar para convertir tiempo string a datetime para comparación
            def time_to_datetime(time_str: str) -> datetime:
                """Convierte un string de tiempo HH:MM:SS o HH:MM a datetime para comparación"""
                if not time_str:
                    return datetime.min
                # Normalizar formato: puede venir como HH:MM:SS o HH:MM
                parts = str(time_str).strip().split(':')
                if len(parts) >= 2:
                    hour = int(parts[0])
                    minute = int(parts[1])
                    # Crear datetime base para comparación
                    base_date = datetime(2000, 1, 1)  # Fecha dummy para comparar solo horas
                    return base_date.replace(hour=hour, minute=minute)
                return datetime.min
            
            # Obtener todas las reservas para el espacio y fecha
            query = self.client.table(self.table).select('*').eq('space_id', space_id).eq('date', date)
            if exclude_id:
                query = query.neq('id', exclude_id)
            
            response = query.execute()
            if not response.data:
                return False
            
            # Filtrar solo las reservas aprobadas o pendientes
            active_reservations = [r for r in response.data if r.get('status') in ['pending', 'approved']]
            
            if not active_reservations:
                return False
            
            # Convertir los tiempos de la nueva reserva a datetime para comparación
            new_start = time_to_datetime(start_time)
            new_end = time_to_datetime(end_time)
            
            # Verificar conflictos de horario
            for reservation in active_reservations:
                res_start_str = reservation.get('start_time', '')
                res_end_str = reservation.get('end_time', '')
                
                if not res_start_str or not res_end_str:
                    continue
                
                res_start = time_to_datetime(res_start_str)
                res_end = time_to_datetime(res_end_str)
                
                # Verificar solapamiento: hay conflicto si los intervalos se solapan
                # Dos intervalos se solapan si: start1 < end2 AND start2 < end1
                if new_start < res_end and res_start < new_end:
                    return True
            
            return False
        except Exception as e:
            print(f"Error verificando conflicto de horario: {e}")
            import traceback
            traceback.print_exc()
            return True  # En caso de error, asumir conflicto por seguridad

    def update_reservation(
        self,
        reservation_id: str,
        user_id: str,
        space_id: str,
        date: str,
        start_time: str,
        end_time: str,
        justification: str
    ) -> Optional[Dict[str, Any]]:
        """Actualiza una reserva pendiente (solo campos editables)"""
        try:
            data = {
                'space_id': space_id,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'justification': justification,
                'updated_at': datetime.now().isoformat()
            }
            response = (
                self.client.table(self.table)
                .update(data)
                .eq('id', reservation_id)
                .eq('user_id', user_id)
                .eq('status', 'pending')
                .execute()
            )
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error actualizando reserva: {e}")
            return None

    def delete_reservation(self, reservation_id: str) -> bool:
        """Elimina una reserva (admin)"""
        try:
            response = self.client.table(self.table).delete().eq('id', reservation_id).execute()
            return bool(response.data is not None)
        except Exception as e:
            print(f"Error eliminando reserva: {e}")
            return False