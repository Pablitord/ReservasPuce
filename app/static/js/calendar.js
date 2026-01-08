// Script para el calendario de reservas

let calendar;
let selectedSpaceId = '';

document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
    
    // Event listener para el selector de espacios
    const spaceSelect = document.getElementById('spaceSelect');
    if (spaceSelect) {
        spaceSelect.addEventListener('change', function() {
            selectedSpaceId = this.value;
            calendar.refetchEvents();
        });
    }
});

/**
 * Inicializa el calendario FullCalendar
 */
function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) return;
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: function(fetchInfo, successCallback, failureCallback) {
            loadReservations(fetchInfo, successCallback, failureCallback);
        },
        eventDisplay: 'block',
        eventMouseEnter: function(info) {
            // Mostrar tooltip al pasar el cursor
            const statusText = info.event.extendedProps.status === 'approved' ? 'Aprobada' : 'Pendiente';
            const tooltip = document.createElement('div');
            tooltip.className = 'fc-event-tooltip';
            tooltip.innerHTML = `
                <strong>${info.event.extendedProps.spaceName}</strong><br>
                Estado: ${statusText}<br>
                Usuario: ${info.event.extendedProps.userName}<br>
                Hora: ${info.event.extendedProps.startTime} - ${info.event.extendedProps.endTime}
            `;
            tooltip.style.cssText = `
                position: absolute;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 10000;
                pointer-events: none;
                white-space: nowrap;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(tooltip);
            
            const updateTooltipPosition = (e) => {
                tooltip.style.left = (e.pageX + 10) + 'px';
                tooltip.style.top = (e.pageY + 10) + 'px';
            };
            
            document.addEventListener('mousemove', updateTooltipPosition);
            info.el.dataset.tooltip = 'true';
            info.el.addEventListener('mouseleave', function() {
                document.removeEventListener('mousemove', updateTooltipPosition);
                if (tooltip.parentNode) {
                    tooltip.parentNode.removeChild(tooltip);
                }
            }, { once: true });
        },
        eventClick: function(info) {
            // Mostrar información del evento al hacer clic
            const statusText = info.event.extendedProps.status === 'approved' ? 'Aprobada' : 'Pendiente';
            const message = `
Reserva: ${info.event.extendedProps.spaceName}
Estado: ${statusText}
Usuario: ${info.event.extendedProps.userName}
Fecha: ${info.event.start.toLocaleDateString('es-ES')}
Hora: ${info.event.extendedProps.startTime} - ${info.event.extendedProps.endTime}
Justificación: ${info.event.extendedProps.justification || 'N/A'}
            `.trim();
            alert(message);
        },
        height: 'auto',
        dayMaxEvents: true,
        moreLinkClick: 'popover',
        dayCellDidMount: function(info) {
            // Agregar estilo a los días sin reservas (disponibles)
            const dateStr = info.date.toISOString().split('T')[0];
            const hasReservations = calendar.getEvents().some(event => {
                const eventDate = event.start.toISOString().split('T')[0];
                return eventDate === dateStr;
            });
            
            if (!hasReservations && info.date >= new Date()) {
                info.el.style.backgroundColor = '#f8f9fa';
                info.el.title = 'Día disponible';
            }
        }
    });
    
    calendar.render();
}

/**
 * Carga las reservas desde el API
 */
function loadReservations(fetchInfo, successCallback, failureCallback) {
    const params = new URLSearchParams();
    
    if (selectedSpaceId) {
        params.append('space_id', selectedSpaceId);
    }
    
    // Obtener reservas para el rango de fechas visible
    const startDate = fetchInfo.startStr.split('T')[0];
    const endDate = fetchInfo.endStr.split('T')[0];
    
    // Por simplicidad, cargamos todas las reservas
    // En producción, podrías optimizar esto para cargar solo el rango visible
    fetch(`/user/api/reservations?${params.toString()}`)
        .then(response => response.json())
        .then(events => {
            // Filtrar eventos por el rango visible
            const filteredEvents = events.filter(event => {
                const eventDate = event.start.split('T')[0];
                return eventDate >= startDate && eventDate <= endDate;
            });
            
            successCallback(filteredEvents);
        })
        .catch(error => {
            console.error('Error cargando reservas:', error);
            failureCallback(error);
        });
}
