from app.repositories.supabase.reservation_repo import ReservationRepository
from app.repositories.supabase.notification_repo import NotificationRepository
from app.repositories.supabase.user_repo import UserRepository
from app.repositories.supabase.reservation_deletion_repo import ReservationDeletionRepository
from app.services.class_schedule_service import ClassScheduleService
from typing import Optional, Dict, Any, List
from datetime import datetime, date as date_module

class ReservationService:
    """Servicio para operaciones de reservas"""
    
    def __init__(self):
        self.reservation_repo = ReservationRepository()
        self.notification_repo = NotificationRepository()
        self.user_repo = UserRepository()
        self.class_schedule_service = ClassScheduleService()
        self.reservation_deletion_repo = ReservationDeletionRepository()
    
    def create_reservation(self, user_id: str, space_id: str, date: str, start_time: str, 
                          end_time: str, justification: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """Crea una nueva reserva"""
        # Validar fecha
        try:
            reservation_date = datetime.strptime(date, '%Y-%m-%d').date()
            if reservation_date < date_module.today():
                return False, "No puedes reservar fechas pasadas", None
        except ValueError:
            return False, "Fecha inválida", None
        
        # Verificar conflicto con horario de clases fijo
        class_conflict = self.class_schedule_service.find_conflict_with_class(
            space_id, date, start_time, end_time
        )
        if class_conflict:
            conflict_start = str(class_conflict.get('start_time'))[:5]
            conflict_end = str(class_conflict.get('end_time'))[:5]
            return (
                False,
                f"El aula está ocupada por clases de {conflict_start} a {conflict_end}.",
                None,
            )
        
        # Verificar conflicto de horario
        if self.reservation_repo.check_time_conflict(space_id, date, start_time, end_time):
            return False, "Ya existe una reserva en ese horario para este espacio", None
        
        # Crear reserva
        reservation = self.reservation_repo.create_reservation(
            user_id, space_id, date, start_time, end_time, justification, status='pending'
        )
        
        if not reservation:
            return False, "Error al crear la reserva", None
        
        # Notificar a los administradores
        self._notify_admins_new_reservation(reservation)
        
        return True, "Reserva creada exitosamente. Esperando aprobación del administrador.", reservation
    
    def _notify_admins_new_reservation(self, reservation: Dict[str, Any]):
        """Notifica a los administradores sobre una nueva reserva"""
        from app.services.space_service import SpaceService
        
        admins = self.user_repo.get_all_users()
        admins = [admin for admin in admins if admin.get('role') == 'admin']
        
        # Obtener el ID de la reserva
        reservation_id = reservation.get('id') if reservation else None
        if not reservation_id:
            print("Error: No se pudo obtener el ID de la reserva para la notificación")
            return
        
        # Obtener el nombre del espacio
        space_service = SpaceService()
        space = space_service.get_space_by_id(reservation.get('space_id', ''))
        space_name = space.get('name', 'un espacio') if space else 'un espacio'
        
        for admin in admins:
            self.notification_repo.create_notification(
                user_id=admin['id'],
                title='Nueva solicitud de reserva',
                message=f'Se ha recibido una nueva solicitud de reserva para {space_name}',
                type='info',
                link=f'/admin/reservations/{reservation_id}'
            )
    
    def approve_reservation(self, reservation_id: str, admin_id: str) -> tuple[bool, str]:
        """Aprueba una reserva"""
        reservation = self.reservation_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            return False, "Reserva no encontrada"
        
        if reservation['status'] != 'pending':
            return False, "Esta reserva ya fue procesada"
        
        # Actualizar estado
        updated = self.reservation_repo.update_reservation_status(reservation_id, 'approved', admin_id)
        if not updated:
            return False, "Error al aprobar la reserva"
        
        # Notificar al usuario
        self.notification_repo.create_notification(
            user_id=reservation['user_id'],
            title='Reserva aprobada',
            message=f'Tu reserva para {reservation.get("spaces", {}).get("name", "el espacio")} ha sido aprobada',
            type='success',
            link=f'/user/my_reservations/{reservation_id}'
        )
        
        return True, "Reserva aprobada exitosamente"
    
    def reject_reservation(self, reservation_id: str, admin_id: str, rejection_reason: str = None) -> tuple[bool, str]:
        """Rechaza una reserva"""
        reservation = self.reservation_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            return False, "Reserva no encontrada"
        
        if reservation['status'] != 'pending':
            return False, "Esta reserva ya fue procesada"
        
        # Validar razón de rechazo
        if not rejection_reason or len(rejection_reason.strip()) < 10:
            return False, "Debes proporcionar una razón del rechazo de al menos 10 caracteres"
        
        # Actualizar estado
        updated = self.reservation_repo.update_reservation_status(reservation_id, 'rejected', admin_id)
        if not updated:
            return False, "Error al rechazar la reserva"
        
        # Obtener el nombre del espacio
        space_name = 'el espacio'
        if reservation.get('spaces'):
            if isinstance(reservation.get('spaces'), dict):
                space_name = reservation.get('spaces', {}).get('name', 'el espacio')
            elif isinstance(reservation.get('spaces'), list) and len(reservation.get('spaces', [])) > 0:
                space_name = reservation.get('spaces')[0].get('name', 'el espacio')
        
        # Crear mensaje con la razón
        notification_message = f'Tu reserva para {space_name} ha sido rechazada.\n\nRazón: {rejection_reason.strip()}'
        
        # Notificar al usuario con la razón
        self.notification_repo.create_notification(
            user_id=reservation['user_id'],
            title='Reserva rechazada',
            message=notification_message,
            type='error',
            link=f'/user/my_reservations/{reservation_id}'
        )
        
        return True, "Reserva rechazada exitosamente"
    
    def get_user_reservations(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtiene las reservas de un usuario"""
        return self.reservation_repo.get_reservations_by_user(user_id)
    
    def get_reservation_by_id(self, reservation_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva por ID"""
        return self.reservation_repo.get_reservation_by_id(reservation_id)
    
    def get_pending_reservations(self) -> List[Dict[str, Any]]:
        """Obtiene todas las reservas pendientes"""
        return self.reservation_repo.get_pending_reservations()
    
    def get_reservations_by_space_and_date(self, space_id: str, date: str) -> List[Dict[str, Any]]:
        """Obtiene reservas de un espacio en una fecha específica"""
        return self.reservation_repo.get_reservations_by_space_and_date(space_id, date)
    
    def get_all_reservations(self) -> List[Dict[str, Any]]:
        """Obtiene todas las reservas"""
        return self.reservation_repo.get_all_reservations()

    def update_reservation(
        self,
        reservation_id: str,
        user_id: str,
        space_id: str,
        date: str,
        start_time: str,
        end_time: str,
        justification: str
    ) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """Permite editar una reserva pendiente del propio usuario"""
        # Obtener la reserva y validar propietario/estado
        reservation = self.reservation_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            return False, "Reserva no encontrada", None
        if reservation.get('user_id') != user_id:
            return False, "No tienes permisos para editar esta reserva", None
        if reservation.get('status') != 'pending':
            return False, "Solo puedes editar reservas pendientes", None

        # Validar fecha futura
        try:
            reservation_date = datetime.strptime(date, '%Y-%m-%d').date()
            if reservation_date < date_module.today():
                return False, "No puedes reservar fechas pasadas", None
        except ValueError:
            return False, "Fecha inválida", None

        # Validar clase
        class_conflict = self.class_schedule_service.find_conflict_with_class(
            space_id, date, start_time, end_time
        )
        if class_conflict:
            conflict_start = str(class_conflict.get('start_time'))[:5]
            conflict_end = str(class_conflict.get('end_time'))[:5]
            return (
                False,
                f"El aula está ocupada por clases de {conflict_start} a {conflict_end}.",
                None,
            )

        # Validar conflicto con otras reservas (excluyendo la propia)
        if self.reservation_repo.check_time_conflict(space_id, date, start_time, end_time, exclude_id=reservation_id):
            return False, "Ya existe una reserva en ese horario para este espacio", None

        updated = self.reservation_repo.update_reservation(
            reservation_id, user_id, space_id, date, start_time, end_time, justification
        )
        if not updated:
            return False, "No se pudo actualizar la reserva", None

        return True, "Reserva actualizada", updated

    def delete_reservation_admin(self, reservation_id: str, admin_id: str, reason: str) -> tuple[bool, str]:
        """Elimina una reserva (solo admin), registra bitácora y notifica al usuario."""
        reservation = self.reservation_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            return False, "Reserva no encontrada"

        # Registrar en bitácora
        self.reservation_deletion_repo.log_deletion(reservation, admin_id, reason)

        # Notificar al usuario
        try:
            space_name = "el espacio"
            if reservation.get("spaces"):
                if isinstance(reservation.get("spaces"), dict):
                    space_name = reservation.get("spaces", {}).get("name", "el espacio")
                elif isinstance(reservation.get("spaces"), list) and reservation.get("spaces"):
                    space_name = reservation.get("spaces")[0].get("name", "el espacio")
            message = f"Tu reserva para {space_name} fue eliminada por un administrador.\n\nMotivo: {reason}"
            self.notification_repo.create_notification(
                user_id=reservation.get("user_id"),
                title="Reserva eliminada",
                message=message,
                type="warning",
                link="/user/my_reservations"
            )
        except Exception as e:
            print(f"Error notificando eliminación: {e}")

        deleted = self.reservation_repo.delete_reservation(reservation_id)
        if not deleted:
            return False, "No se pudo eliminar la reserva"
        return True, "Reserva eliminada"
