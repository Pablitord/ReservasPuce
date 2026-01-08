// Script para el calendario de reservas

let calendar;
let selectedSpaceId = '';

// Inicializar inmediatamente cuando el script se carga (FullCalendar ya está listo)
(function() {
    console.log('Script calendar.js ejecutándose...');
    
    // Esperar a que el DOM esté listo
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(initializeCalendarComplete, 100);
            });
        } else {
            setTimeout(initializeCalendarComplete, 100);
        }
    }
    
    function initializeCalendarComplete() {
        if (typeof FullCalendar === 'undefined') {
            console.error('FullCalendar no está disponible al inicializar');
            const calendarEl = document.getElementById('calendar');
            if (calendarEl) {
                calendarEl.innerHTML = '<div class="alert alert-danger">Error: FullCalendar no está disponible. Recarga la página.</div>';
            }
            return;
        }
        
        console.log('FullCalendar disponible, inicializando calendario...');
        initializeCalendar();
        
        // Event listener para el selector de espacios
        const spaceSelect = document.getElementById('spaceSelect');
        if (spaceSelect) {
            spaceSelect.addEventListener('change', function() {
                selectedSpaceId = this.value;
                if (calendar) {
                    calendar.refetchEvents();
                }
            });
        }
    }
    
    init();
})();

/**
 * Inicializa el calendario FullCalendar
 */
function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) {
        console.error('No se encontró el elemento #calendar');
        return;
    }
    
    console.log('Inicializando calendario...');
    
    try {
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
            // En la vista de mes, no mostrar hora (los eventos son allDay)
            displayEventTime: false,
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
        console.log('Calendario renderizado correctamente');
    } catch (error) {
        console.error('Error inicializando calendario:', error);
        const calendarEl = document.getElementById('calendar');
        if (calendarEl) {
            calendarEl.innerHTML = '<div class="alert alert-danger">Error al inicializar el calendario: ' + error.message + '</div>';
        }
    }
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
    
    console.log('Cargando reservas desde', startDate, 'hasta', endDate);
    
    fetch(`/user/api/reservations?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(events => {
            console.log('Reservas recibidas:', events.length);
            console.log('Eventos recibidos (primeros 3):', events.slice(0, 3));
            
            // Procesar eventos para la vista de mes
            // En la vista de mes, los eventos deben ser "allDay" para aparecer solo en un día
            const processedEvents = events.map(event => {
                if (!event.start) {
                    console.warn('Evento sin start:', event);
                    return null;
                }
                
                // Extraer SOLO la fecha (sin hora) del evento
                let eventDate;
                if (typeof event.start === 'string') {
                    eventDate = event.start.includes('T') 
                        ? event.start.split('T')[0]  // Extraer solo YYYY-MM-DD
                        : event.start;
                } else {
                    eventDate = new Date(event.start).toISOString().split('T')[0];
                }
                
                // Extraer información de hora para el título
                const startTime = event.startTime || event.extendedProps?.startTime || '';
                const endTime = event.endTime || event.extendedProps?.endTime || '';
                const spaceName = event.spaceName || event.extendedProps?.spaceName || 'Espacio';
                
                // Crear título con la hora
                const eventTitle = startTime && endTime 
                    ? `${spaceName} (${startTime}-${endTime})`
                    : spaceName;
                
                // Crear un nuevo evento que sea "allDay" pero SOLO en ese día específico
                // CRÍTICO: NO incluir 'end' y usar solo la fecha para que aparezca SOLO en UN día
                const processedEvent = {
                    id: String(event.id),  // Asegurar que sea string único
                    title: eventTitle,
                    allDay: true,  // CRÍTICO: debe ser allDay para vista de mes
                    start: eventDate,  // SOLO la fecha YYYY-MM-DD (sin hora, sin end)
                    // IMPORTANTE: NO incluir 'end' - esto hace que ocupe solo UN día
                    color: event.color || '#28a745',  // Verde por defecto
                    backgroundColor: event.backgroundColor || '#28a745',  // Verde por defecto
                    borderColor: event.borderColor || '#218838',  // Verde oscuro para borde
                    textColor: event.textColor || 'white',
                    // Mantener toda la información original para tooltips
                    extendedProps: {
                        status: event.status || event.extendedProps?.status,
                        spaceName: spaceName,
                        userName: event.userName || event.extendedProps?.userName || 'Usuario',
                        startTime: startTime,
                        endTime: endTime,
                        justification: event.extendedProps?.justification || '',
                        originalStart: event.start,  // Guardar fecha/hora original completa
                        originalEnd: event.end
                    }
                };
                
                // CRÍTICO: Asegurar que NO tenga 'end' para que ocupe solo UN día
                delete processedEvent.end;  // Eliminar explícitamente si existe
                
                // Verificar formato final
                if (processedEvent.allDay !== true) {
                    console.warn('ADVERTENCIA: Evento no es allDay después de procesar:', processedEvent);
                    processedEvent.allDay = true;
                }
                
                return processedEvent;
            }).filter(e => e !== null);
            
            // Filtrar eventos por el rango visible
            // Ahora los eventos tienen start como solo fecha (YYYY-MM-DD), así que es más simple
            const filteredEvents = processedEvents.filter(event => {
                if (!event.start) {
                    return false;
                }
                
                try {
                    // Como ahora start es solo la fecha (YYYY-MM-DD), comparar directamente
                    const eventDate = event.start;  // Ya es solo la fecha sin hora
                    
                    // El evento solo debe aparecer en su día específico
                    const isInRange = eventDate >= startDate && eventDate <= endDate;
                    
                    return isInRange;
                } catch (error) {
                    console.error('Error procesando evento:', event, error);
                    return false;
                }
            });
            
            console.log('Eventos filtrados:', filteredEvents.length);
            
            // Debug detallado: mostrar información de cada evento
            filteredEvents.forEach((e, index) => {
                console.log(`Evento ${index + 1}:`, {
                    id: e.id,
                    title: e.title,
                    start: e.start,
                    end: e.end,
                    allDay: e.allDay,
                    hasEndProperty: 'end' in e
                });
            });
            
            // Verificar que no haya eventos duplicados o mal formateados
            const eventDates = filteredEvents.map(e => e.start);
            const uniqueDates = new Set(eventDates);
            if (eventDates.length !== uniqueDates.size) {
                console.warn('ADVERTENCIA: Hay eventos con la misma fecha', eventDates);
            }
            
            // Verificar y limpiar eventos antes de enviarlos a FullCalendar
            const finalEvents = filteredEvents.map(e => {
                // Crear un objeto nuevo SIN la propiedad 'end'
                const cleanEvent = {
                    id: e.id,
                    title: e.title,
                    allDay: true,  // Forzar a true
                    start: e.start,  // Solo la fecha
                    color: e.color,
                    backgroundColor: e.backgroundColor,
                    borderColor: e.borderColor,
                    textColor: e.textColor,
                    extendedProps: e.extendedProps || {}
                };
                
                // NO incluir 'end' en ningún caso
                return cleanEvent;
            });
            
            console.log('Eventos finales (sin end):', finalEvents.map(e => ({
                id: e.id,
                title: e.title,
                start: e.start,
                allDay: e.allDay,
                hasEnd: 'end' in e
            })));
            
            successCallback(finalEvents);
        })
        .catch(error => {
            console.error('Error cargando reservas:', error);
            // Llamar con un array vacío para que el calendario se muestre
            successCallback([]);
        });
}
