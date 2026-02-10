# Sistema de Reservas de Espacios Universitarios – PUCE

Sistema web para la gestión de reservas de espacios universitarios (aulas, laboratorios y auditorios) de la PUCE. Permite a los usuarios solicitar reservas, ver disponibilidad en un calendario interactivo y recibir notificaciones; los administradores aprueban o rechazan solicitudes, gestionan horarios de clases y consultan estadísticas.

---

## Descripción

El sistema centraliza y automatiza la reserva de espacios: evita conflictos de horarios, da trazabilidad y mejora la comunicación entre usuarios y administración. La base de datos está en la nube (Supabase, PostgreSQL) y la aplicación sigue una arquitectura en capas (frontend → rutas → servicios → repositorios → BD).

---

## Características principales

- **Autenticación:** registro, login y verificación de cuenta por correo (código).
- **Calendario:** vista mensual con FullCalendar, filtros por piso y espacio; reservas aprobadas y pendientes con colores.
- **Reservas:** solicitud con justificación, validación de conflictos de horario y con horarios de clases; edición y cancelación de reservas pendientes.
- **Notificaciones:** en la app (dropdown, actualización cada 30 s) y por correo (confirmación, aprobación/rechazo, aviso a admins, recordatorios del día).
- **Panel de administración:** dashboard, aprobar/rechazar reservas (con razón obligatoria), CRUD de horarios de clases, bitácora de eliminaciones, creación de administradores.
- **Chatbot:** asistente de consultas (capacidad, ocupación, espacios libres) en lenguaje natural o por botones; respuestas con datos reales de la BD (híbrido DeepSeek + reglas).

---

## Tecnologías

| Área        | Tecnología                          |
|------------|--------------------------------------|
| Backend    | Flask 3 (Python)                     |
| Base de datos | Supabase (PostgreSQL en la nube)  |
| Frontend   | HTML, Jinja2, Bootstrap 5, JavaScript |
| Calendario | FullCalendar.js                      |
| Correo     | SMTP (configurable en `.env`)        |
| Chatbot    | Opcional: DeepSeek API; fallback por reglas |

---

## Requisitos

- Python 3.8+
- Cuenta de Supabase (proyecto con URL y API key)
- Opcional: servidor SMTP para correos; API key de DeepSeek para el chatbot

---

## Instalación rápida

1. **Clonar o entrar al proyecto**
   ```bash
   cd ReservasPuce
   ```

2. **Entorno virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   # source venv/bin/activate     # Linux/macOS
   ```

3. **Dependencias**
   ```bash
   cd app
   pip install -r requirements.txt
   cd ..
   ```

4. **Variables de entorno**  
   Crear `.env` en la **raíz** del proyecto:
   ```env
   SECRET_KEY=tu-clave-secreta-segura
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_KEY=tu-anon-key-de-supabase
   FLASK_DEBUG=True
   HOST=127.0.0.1
   PORT=5000
   ```
   Opcional (correos): `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS`.  
   Opcional (chatbot): `DEEPSEEK_API_KEY`.

5. **Base de datos**  
   En el panel de Supabase → SQL Editor, ejecutar el contenido de `app/scripts/01_schema.sql`.

6. **Ejecutar**
   ```bash
   cd app
   python run.py
   ```
   Abrir en el navegador: `http://127.0.0.1:5000`.

---

## Credenciales por defecto

Tras ejecutar el schema SQL se crea un administrador:

- **Email:** `admin@puce.edu.ec`  
- **Contraseña:** `admin123`  

*(Cambiar en producción.)*

---

## Estructura del proyecto

```
ReservasPuce/
├── app/
│   ├── __init__.py          # Factory de Flask, blueprints
│   ├── config.py            # Configuración (env, Supabase, SMTP, DeepSeek)
│   ├── deps.py              # Decoradores @login_required, @admin_required
│   ├── routes/              # Rutas HTTP (auth, user, admin, notifications)
│   ├── services/            # Lógica de negocio (auth, reservas, chatbot, email, etc.)
│   ├── repositories/        # Acceso a datos (Supabase)
│   │   └── supabase/        # Cliente y repos por tabla
│   ├── templates/           # Vistas HTML (Jinja2)
│   ├── static/              # CSS, JavaScript
│   └── scripts/             # 01_schema.sql, send_reservation_reminders.py
├── .env                     # Variables de entorno (no subir a git)
├── requirements.txt
├── README.md                # Este archivo
├── SETUP_ENV.md             # Guía detallada de instalación (venv, .env)
├── CONTEXTO_PROYECTO.md     # Documentación técnica completa
└── DOCUMENTACION_RUBRICA.md # Referencia para rúbricas (BD en la nube, IHC)
```

---

## Funcionalidades por rol

### Usuario
- Registro, verificación por correo e inicio de sesión.
- Calendario con disponibilidad y filtros.
- Solicitar, editar y cancelar reservas pendientes.
- Ver mis reservas y detalle.
- Notificaciones en la app y por correo (confirmación, aprobación/rechazo).
- Chatbot: capacidad, ocupación y espacios libres (escrito o por botones).

### Administrador
- Dashboard con estadísticas (reservas, espacios, usuarios).
- Listar y filtrar reservas; aprobar o rechazar (con razón obligatoria).
- Gestionar horarios de clases por espacio.
- Bitácora de eliminaciones.
- Crear otros administradores.
- Notificaciones de nuevas solicitudes (en app y por correo).

---

## Recordatorios por correo

El script `app/scripts/send_reservation_reminders.py` envía recordatorios a usuarios con reserva **aprobada** para el día. Ejecución manual:

```bash
cd app
python scripts/send_reservation_reminders.py
```

Para envío automático diario, programar con cron (Linux/macOS) o Programador de tareas (Windows).

---

## Documentación adicional

- **SETUP_ENV.md** – Pasos detallados de entorno virtual y `.env` (incl. Windows).
- **CONTEXTO_PROYECTO.md** – Arquitectura, flujos, endpoints, servicios y notas técnicas.
- **DOCUMENTACION_RUBRICA.md** – Contenido alineado con rúbricas de Base de Datos en la Nube e Interacción Humano-Computador.

---

## Licencia

Proyecto de uso interno para la Universidad.
