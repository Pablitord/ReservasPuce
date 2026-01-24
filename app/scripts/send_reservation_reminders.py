"""
Script para enviar recordatorios de reservas aprobadas del día.
Uso:
  python app/scripts/send_reservation_reminders.py
"""

import sys
from datetime import date as date_module

sys.path.insert(0, '.')

from app.services.reservation_service import ReservationService


def main():
    service = ReservationService()
    result = service.send_reservation_reminders(date_module.today().isoformat())
    print(f"Recordatorios enviados: {result.get('sent', 0)} / {result.get('total', 0)}")


if __name__ == '__main__':
    main()
