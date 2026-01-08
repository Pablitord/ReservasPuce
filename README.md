# Sistema de Reservas PUCE

Sistema web para la gestión de reservas de espacios universitarios (aulas, laboratorios y auditorio) de la Universidad.

## Características

- 🔐 Autenticación de usuarios (login/registro)
- 📅 Calendario visual para ver disponibilidad de espacios
- 📝 Solicitud de reservas con justificación
- 🔔 Sistema de notificaciones en tiempo real
- 👨‍💼 Panel de administración para aprobar/rechazar reservas
- 📊 Dashboard con estadísticas

## Tecnologías

- **Backend**: Flask (Python)
- **Base de datos**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Calendario**: FullCalendar.js

## Requisitos

- Python 3.8+
- Cuenta de Supabase
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio o navegar al directorio del proyecto

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
cd app
pip install -r requirements.txt
```

4. Configurar variables de entorno:
   - Crear un archivo `.env` en la raíz del proyecto con:
   ```
   SECRET_KEY=tu-clave-secreta-aqui
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-clave-supabase-aqui
   FLASK_DEBUG=True
   ```

5. Configurar la base de datos:
   - Ir a Supabase Dashboard
   - Ejecutar el script SQL en `app/scripts/01_schema.sql` en el SQL Editor

6. Ejecutar la aplicación:
```bash
python run.py
```

7. Acceder a la aplicación:
   - Abrir navegador en `http://127.0.0.1:5000`

## Estructura del Proyecto

```
ReservasPuce/
├── app/
│   ├── __init__.py          # Configuración de Flask
│   ├── config.py            # Configuración de la app
│   ├── run.py               # Punto de entrada
│   ├── deps.py              # Dependencias y decoradores
│   ├── routes/              # Rutas del backend
│   ├── services/            # Lógica de negocio
│   ├── repositories/        # Acceso a datos (Supabase)
│   ├── templates/           # Templates HTML
│   ├── static/              # Archivos estáticos (CSS, JS)
│   └── scripts/             # Scripts SQL
├── api/
└── README.md
```

## Credenciales por Defecto

Después de ejecutar el schema SQL, se crea un usuario administrador:
- Email: `admin@puce.edu.ec`
- Contraseña: `admin123` (¡Cambiar en producción!)

## Funcionalidades

### Para Usuarios
- Registro e inicio de sesión
- Ver calendario de espacios disponibles
- Solicitar reserva de espacios
- Ver estado de sus reservas
- Recibir notificaciones de aprobación/rechazo

### Para Administradores
- Dashboard con estadísticas
- Ver todas las solicitudes de reserva
- Aprobar o rechazar reservas
- Ver detalles completos de cada reserva
- Recibir notificaciones de nuevas solicitudes

## Notas de Desarrollo

- El sistema utiliza sesiones para mantener el estado del usuario
- Las notificaciones se actualizan cada 30 segundos
- El calendario muestra reservas aprobadas y pendientes
- Se valida que no haya conflictos de horario al crear reservas

## Próximas Mejoras

- [ ] Edición de reservas
- [ ] Cancelación de reservas
- [ ] Filtros avanzados en el calendario
- [ ] Exportar calendario
- [ ] Notificaciones por email
- [ ] Historial de cambios

## Licencia

Este proyecto es de uso interno para la Universidad.
