# CONTEXTO COMPLETO DEL PROYECTO - ReservasPuce

**Fecha de última actualización:** Enero 2026  
**Estado:** En desarrollo activo  
**Próxima funcionalidad:** Implementación de Chatbot con procesamiento de lenguaje natural

---

## 📋 ÍNDICE

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Base de Datos](#base-de-datos)
6. [Configuración y Variables de Entorno](#configuración-y-variables-de-entorno)
7. [Rutas y Endpoints](#rutas-y-endpoints)
8. [Servicios y Lógica de Negocio](#servicios-y-lógica-de-negocio)
9. [Repositorios (Capa de Datos)](#repositorios-capa-de-datos)
10. [Frontend y Templates](#frontend-y-templates)
11. [Flujos Principales del Sistema](#flujos-principales-del-sistema)
12. [Funcionalidades Implementadas](#funcionalidades-implementadas)
13. [Problemas Resueltos y Notas Técnicas](#problemas-resueltos-y-notas-técnicas)
14. [Próximas Mejoras](#próximas-mejoras)

---

## 📖 DESCRIPCIÓN GENERAL

Sistema web para la gestión de reservas de espacios universitarios (aulas, laboratorios y auditorio) de la PUCE. Permite a los estudiantes solicitar reservas de espacios, visualizar disponibilidad mediante un calendario interactivo, y permite a los administradores gestionar y aprobar/rechazar las solicitudes.

### Funcionalidades Principales

- ✅ Autenticación de usuarios (login/registro) con roles (user/admin)
- ✅ Calendario visual interactivo con FullCalendar.js para ver disponibilidad
- ✅ Solicitud de reservas con justificación
- ✅ Sistema de notificaciones en tiempo real (actualización cada 30s)
- ✅ Panel de administración con dashboard y estadísticas
- ✅ Aprobación/rechazo de reservas con razón de rechazo obligatoria
- ✅ Creación de administradores desde el panel admin
- ✅ Validación de conflictos de horario
- ✅ Tooltips en calendario con detalles de reservas

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Patrón Arquitectónico

**Arquitectura en Capas (Layered Architecture):**

```
Frontend (Templates + JS + CSS)
    ↕
Routes (Blueprints de Flask)
    ↕
Services (Lógica de Negocio)
    ↕
Repositories (Acceso a Datos)
    ↕
Supabase (PostgreSQL)
```

### Componentes Principales

1. **Routes (app/routes/)**: Endpoints HTTP, manejan requests/responses
2. **Services (app/services/)**: Lógica de negocio, validaciones, orquestación
3. **Repositories (app/repositories/)**: Abstracción de acceso a datos (Supabase)
4. **Templates (app/templates/)**: Vistas HTML con Jinja2
5. **Static (app/static/)**: CSS, JavaScript, assets estáticos

---

## 🛠️ STACK TECNOLÓGICO

### Backend
- **Flask 3.0.0**: Framework web Python
- **Python 3.8+**: Lenguaje de programación
- **Werkzeug 3.0.1**: Utilidades para seguridad (hashing de contraseñas)
- **python-dotenv 1.0.0**: Gestión de variables de entorno
- **python-dateutil 2.8.2**: Manipulación de fechas

### Base de Datos
- **Supabase 2.0.0**: Backend-as-a-Service (BaaS)
- **PostgreSQL**: Base de datos relacional (manejada por Supabase)

### Frontend
- **HTML5 + Jinja2**: Templates dinámicos
- **Bootstrap 5**: Framework CSS para UI responsive
- **JavaScript (Vanilla)**: Lógica del frontend
- **FullCalendar.js 6.1.10**: Biblioteca para calendario interactivo

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ReservasPuce/
├── app/
│   ├── __init__.py                 # Factory de Flask, registro de blueprints
│   ├── config.py                   # Configuración (env vars, Supabase)
│   ├── run.py                      # Punto de entrada de la aplicación
│   ├── deps.py                     # Decoradores (login_required, admin_required)
│   │
│   ├── routes/                     # Blueprints de Flask
│   │   ├── __init__.py
│   │   ├── auth_routes.py          # /auth/* (login, register, logout)
│   │   ├── user_routes.py          # /user/* (calendar, reserve, my_reservations)
│   │   ├── admin_routes.py         # /admin/* (dashboard, reservations, create_admin)
│   │   └── notification_routes.py  # /notifications/* (API endpoints)
│   │
│   ├── services/                   # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Registro, login, autenticación
│   │   ├── reservation_service.py  # CRUD reservas, aprobar/rechazar
│   │   ├── space_service.py        # Gestión de espacios
│   │   ├── notification_service.py # Gestión de notificaciones
│   │   └── admin_service.py        # Estadísticas y operaciones admin
│   │
│   ├── repositories/
│   │   └── supabase/               # Acceso a datos (Supabase)
│   │       ├── __init__.py
│   │       ├── client.py           # Cliente singleton de Supabase
│   │       ├── user_repo.py        # CRUD usuarios
│   │       ├── space_repo.py       # CRUD espacios
│   │       ├── reservation_repo.py # CRUD reservas, validaciones
│   │       └── notification_repo.py # CRUD notificaciones
│   │
│   ├── templates/                  # Templates HTML (Jinja2)
│   │   ├── base.html               # Template base con navbar, flashes
│   │   ├── partials/               # Componentes reutilizables
│   │   │   ├── navbar.html
│   │   │   ├── flashes.html
│   │   │   └── notifications_dropdown.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── user/
│   │   │   ├── calendar.html
│   │   │   ├── reserve_form.html
│   │   │   ├── my_reservations.html
│   │   │   └── reservation_detail.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── reservations.html
│   │       ├── reservation_detail.html
│   │       └── create_admin.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css          # Estilos personalizados
│   │   └── js/
│   │       ├── main.js             # Notificaciones, utilidades generales
│   │       ├── calendar.js         # Lógica de FullCalendar
│   │       └── notifications.js    # Manejo de notificaciones
│   │
│   └── scripts/
│       └── 01_schema.sql           # Schema de base de datos
│
├── api/                            # (Carpeta no utilizada actualmente)
├── venv/                           # Entorno virtual de Python
├── .env                            # Variables de entorno (NO commitear)
├── .gitignore
├── requirements.txt                # Dependencias Python
├── setup_venv.bat                  # Script de configuración Windows
├── SETUP_ENV.md                    # Guía de configuración
├── README.md                       # Documentación básica
└── CONTEXTO_PROYECTO.md            # Este archivo
```

---

## 💾 BASE DE DATOS

### Tablas

#### 1. `users`
```sql
- id (UUID, PK)
- email (VARCHAR(255), UNIQUE, NOT NULL)
- password_hash (VARCHAR(255), NOT NULL)
- name (VARCHAR(255), NOT NULL)
- student_id (VARCHAR(50), UNIQUE, NOT NULL)
- role (VARCHAR(20), DEFAULT 'user', CHECK IN ('user', 'admin'))
- created_at (TIMESTAMP WITH TIME ZONE)
- updated_at (TIMESTAMP WITH TIME ZONE)
```

**Usuario admin por defecto:**
- Email: `admin@puce.edu.ec`
- Password: `admin123` (hash: `$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5KqZz8eHGqR1q`)

#### 2. `spaces`
```sql
- id (UUID, PK)
- name (VARCHAR(255), NOT NULL)
- type (VARCHAR(50), NOT NULL, CHECK IN ('aula', 'laboratorio', 'auditorio'))
- floor (VARCHAR(20), NOT NULL, CHECK IN ('planta_baja', 'piso_1', 'piso_2'))
- capacity (INTEGER, NOT NULL)
- description (TEXT)
- created_at (TIMESTAMP WITH TIME ZONE)
- updated_at (TIMESTAMP WITH TIME ZONE)
```

**Espacios por defecto:**
- Aula 101, 102, 201
- Laboratorio de Computación 1 y 2
- Laboratorio de Física, Química
- Auditorio Principal (200), Auditorio Menor (100)
- A-001 ... A-014 (planta baja, nombres reales por foto)
- A-101 ... A-114 (piso 1)
- A-201 ... A-213 (piso 2)

#### 3. `reservations`
```sql
- id (UUID, PK)
- user_id (UUID, FK -> users.id, ON DELETE CASCADE)
- space_id (UUID, FK -> spaces.id, ON DELETE CASCADE)
- date (DATE, NOT NULL)
- start_time (TIME, NOT NULL)
- end_time (TIME, NOT NULL)
- justification (TEXT, NOT NULL)
- status (VARCHAR(20), DEFAULT 'pending', CHECK IN ('pending', 'approved', 'rejected'))
- admin_id (UUID, FK -> users.id, ON DELETE SET NULL)
- reviewed_at (TIMESTAMP WITH TIME ZONE)
- rejection_reason (TEXT)  -- Agregado recientemente
- created_at (TIMESTAMP WITH TIME ZONE)
- updated_at (TIMESTAMP WITH TIME ZONE)
- CONSTRAINT: check_time_order (end_time > start_time)
```

#### 4. `notifications`
```sql
- id (UUID, PK)
- user_id (UUID, FK -> users.id, ON DELETE CASCADE)
- title (VARCHAR(255), NOT NULL)
- message (TEXT, NOT NULL)
- type (VARCHAR(20), DEFAULT 'info', CHECK IN ('info', 'success', 'warning', 'error'))
- link (VARCHAR(500))
- read (BOOLEAN, DEFAULT FALSE)
- created_at (TIMESTAMP WITH TIME ZONE)
```

### Índices
- `idx_reservations_user_id`
- `idx_reservations_space_id`
- `idx_reservations_date`
- `idx_reservations_status`
- `idx_notifications_user_id`
- `idx_notifications_read`
- `idx_users_email`
- `idx_spaces_type`
- `idx_spaces_floor`

### Relaciones
- `reservations.user_id` → `users.id`
- `reservations.space_id` → `spaces.id`
- `reservations.admin_id` → `users.id`
- `notifications.user_id` → `users.id`

**Nota importante:** En las queries de Supabase, cuando hay múltiples relaciones con `users`, se debe especificar explícitamente:
```python
users!reservations_user_id_fkey(*)  # Usuario que hizo la reserva
```

---

## ⚙️ CONFIGURACIÓN Y VARIABLES DE ENTORNO

### Archivo `.env` (en la raíz del proyecto)

```env
SECRET_KEY=tu-clave-secreta-aqui
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-supabase-aqui
FLASK_DEBUG=True
HOST=127.0.0.1
PORT=5000
```

### Configuración en `app/config.py`

- `SECRET_KEY`: Para sesiones de Flask (cambiar en producción)
- `SUPABASE_URL`: URL del proyecto Supabase
- `SUPABASE_KEY`: API Key de Supabase (anon key)
- `FLASK_DEBUG`: Modo debug (True/False)
- `HOST`: Host del servidor (default: 127.0.0.1)
- `PORT`: Puerto del servidor (default: 5000)

**Importante:** El archivo `.env` debe estar en la raíz (`ReservasPuce/.env`), no en `app/.env`.

---

## 🛣️ RUTAS Y ENDPOINTS

### Autenticación (`/auth/*`)

| Ruta | Método | Descripción | Acceso |
|------|--------|-------------|--------|
| `/auth/login` | GET, POST | Login de usuario | Público |
| `/auth/register` | GET, POST | Registro de usuario | Público |
| `/auth/logout` | GET | Cerrar sesión | Login requerido |

### Usuario (`/user/*`)

| Ruta | Método | Descripción | Acceso |
|------|--------|-------------|--------|
| `/user/calendar` | GET | Vista del calendario | Login requerido |
| `/user/reserve` | GET, POST | Formulario de reserva | Login requerido |
| `/user/my_reservations` | GET | Mis reservas | Login requerido |
| `/user/my_reservations/<id>` | GET | Detalle de reserva | Login requerido |
| `/user/api/reservations` | GET | API para calendario (JSON) | Login requerido |

**Query params de `/user/api/reservations`:**
- `space_id` (opcional): Filtrar por espacio específico
- `floor` (opcional): Filtrar por piso (`planta_baja`, `piso_1`, `piso_2`)

### Administrador (`/admin/*`)

| Ruta | Método | Descripción | Acceso |
|------|--------|-------------|--------|
| `/admin/dashboard` | GET | Dashboard con estadísticas | Admin requerido |
| `/admin/reservations` | GET | Lista de todas las reservas | Admin requerido |
| `/admin/reservations/<id>` | GET | Detalle de reserva | Admin requerido |
| `/admin/reservations/<id>/approve` | POST | Aprobar reserva | Admin requerido |
| `/admin/reservations/<id>/reject` | POST | Rechazar reserva (requiere `rejection_reason`) | Admin requerido |
| `/admin/create_admin` | GET, POST | Crear nuevo administrador | Admin requerido |

**Query params de `/admin/reservations`:**
- `status` (opcional): Filtrar por estado (`pending`, `approved`, `rejected`, `all`)

### Notificaciones (`/notifications/*`)

| Ruta | Método | Descripción | Acceso |
|------|--------|-------------|--------|
| `/notifications/api/unread_count` | GET | Conteo de no leídas | Login requerido |
| `/notifications/api/list` | GET | Lista de notificaciones | Login requerido |
| `/notifications/<id>/read` | POST | Marcar como leída | Login requerido |
| `/notifications/mark_all_read` | POST | Marcar todas como leídas | Login requerido |
| `/notifications/<id>` | GET | Ver notificación y redirigir | Login requerido |

**Query params de `/notifications/api/list`:**
- `unread_only` (opcional): `true` para solo no leídas

### Ruta Principal

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/` | GET | Redirige según rol (admin→dashboard, user→calendar, sin login→login) |

---

## 🔧 SERVICIOS Y LÓGICA DE NEGOCIO

### AuthService (`app/services/auth_service.py`)

**Métodos:**
- `register_user(email, password, name, student_id)` → `(success, message, user)`
  - Valida email único
  - Hashea contraseña con `werkzeug.security.generate_password_hash`
  - Crea usuario con rol `user`
- `login_user(email, password)` → `(success, message, user)`
  - Verifica email y contraseña con `check_password_hash`
- `get_user_by_id(user_id)` → `user_dict`

### ReservationService (`app/services/reservation_service.py`)

**Métodos:**
- `create_reservation(user_id, space_id, date, start_time, end_time, justification)` → `(success, message, reservation)`
  - Valida fecha no pasada
  - Verifica conflictos de horario (`check_time_conflict`)
  - Crea reserva con estado `pending`
  - Notifica a todos los admins (`_notify_admins_new_reservation`)
- `approve_reservation(reservation_id, admin_id)` → `(success, message)`
  - Valida que esté `pending`
  - Actualiza a `approved`
  - Notifica al usuario
- `reject_reservation(reservation_id, admin_id, rejection_reason)` → `(success, message)`
  - Valida que esté `pending`
  - Valida `rejection_reason` (mínimo 10 caracteres)
  - Actualiza a `rejected` con razón
  - Notifica al usuario con la razón
- `get_user_reservations(user_id)` → `List[reservations]`
- `get_reservation_by_id(reservation_id)` → `reservation_dict`
- `get_pending_reservations()` → `List[reservations]`
- `get_reservations_by_space_and_date(space_id, date)` → `List[reservations]`
- `get_all_reservations()` → `List[reservations]`

### SpaceService (`app/services/space_service.py`)

**Métodos:**
- `get_all_spaces()` → `List[spaces]`
- `get_space_by_id(space_id)` → `space_dict`
- `get_spaces_by_type(space_type)` → `List[spaces]`
- `get_spaces_grouped_by_floor()` → `List[{key,label,spaces}]` (agrupa para selects)
- `create_space(name, type, capacity, description, floor='planta_baja')` → `space_dict`

### NotificationService (`app/services/notification_service.py`)

**Métodos:**
- `get_user_notifications(user_id, unread_only=False)` → `List[notifications]`
- `get_unread_count(user_id)` → `int`
- `mark_as_read(notification_id)` → `bool`
- `mark_all_as_read(user_id)` → `bool`

### AdminService (`app/services/admin_service.py`)

**Métodos:**
- `get_dashboard_stats()` → `dict` con:
  - `total_reservations`
  - `pending_reservations`
  - `approved_reservations`
  - `rejected_reservations`
  - `total_spaces`
  - `total_users`
- `get_pending_reservations()` → `List[reservations]`
- `get_all_reservations()` → `List[reservations]`

---

## 💽 REPOSITORIOS (CAPA DE DATOS)

### Cliente Supabase (`app/repositories/supabase/client.py`)

**Patrón Singleton:**
- `SupabaseClient`: Asegura una sola instancia del cliente
- `get_supabase_client()`: Función helper para obtener el cliente

### UserRepository (`app/repositories/supabase/user_repo.py`)

**Métodos:**
- `get_user_by_email(email)` → `user_dict`
- `get_user_by_id(user_id)` → `user_dict`
- `create_user(email, password_hash, name, student_id, role='user')` → `user_dict`
- `get_all_users()` → `List[user_dict]`

### SpaceRepository (`app/repositories/supabase/space_repo.py`)

**Métodos:**
- `get_all_spaces()` → `List[space_dict]`
- `get_space_by_id(space_id)` → `space_dict`
- `get_spaces_by_type(space_type)` → `List[space_dict]`
- `create_space(name, type, capacity, description, floor)` → `space_dict`

### ReservationRepository (`app/repositories/supabase/reservation_repo.py`)

**Métodos:**
- `create_reservation(user_id, space_id, date, start_time, end_time, justification, status='pending')` → `reservation_dict`
- `get_reservation_by_id(reservation_id)` → `reservation_dict`
  - **Join:** `spaces(*)`, `users!reservations_user_id_fkey(*)`
- `get_reservations_by_user(user_id)` → `List[reservation_dict]`
- `get_reservations_by_space_and_date(space_id, date)` → `List[reservation_dict]`
- `get_pending_reservations()` → `List[reservation_dict]`
- `update_reservation_status(reservation_id, status, admin_id, rejection_reason=None)` → `reservation_dict`
  - Actualiza `status`, `admin_id`, `reviewed_at`, `rejection_reason`
- `get_all_reservations()` → `List[reservation_dict]`
  - **Join:** `spaces(*)`, `users!reservations_user_id_fkey(*)`
- `check_time_conflict(space_id, date, start_time, end_time, exclude_id=None)` → `bool`
  - Compara horarios con `datetime.time` objects
  - Retorna `True` si hay conflicto

**Nota crítica:** Cuando se hace join con `users`, usar `users!reservations_user_id_fkey(*)` para especificar la relación correcta y evitar errores de ambigüedad.

### NotificationRepository (`app/repositories/supabase/notification_repo.py`)

**Métodos:**
- `create_notification(user_id, title, message, type='info', link=None)` → `notification_dict`
- `get_user_notifications(user_id, unread_only=False)` → `List[notification_dict]`
- `get_unread_count(user_id)` → `int`
- `mark_as_read(notification_id)` → `bool`
- `mark_all_as_read(user_id)` → `bool`

---

## 🎨 FRONTEND Y TEMPLATES

### Templates Base

**`base.html`**
- Incluye Bootstrap 5 CSS/JS
- Navbar (`partials/navbar.html`)
- Flash messages (`partials/flashes.html`)
- Scripts: `main.js`, notificaciones, calendar

**`partials/navbar.html`**
- Links según rol (user/admin)
- Dropdown de notificaciones
- Link "Crear Administrador" (solo admin)

**`partials/flashes.html`**
- Muestra mensajes flash de Flask
- Auto-dismiss después de 5s (8s para errores)
- Bootstrap alerts con clases `auto-dismiss`

**`partials/notifications_dropdown.html`**
- Dropdown con lista de notificaciones
- Contador de no leídas
- Texto con `word-wrap` y `overflow-wrap` para evitar cortes

### Templates de Autenticación

**`auth/login.html`**: Formulario de login
**`auth/register.html`**: Formulario de registro

### Templates de Usuario

**`user/calendar.html`**
- Selector de piso + selector de espacios con `optgroup` por piso
- Contenedor para FullCalendar (`#calendar`)
- Carga FullCalendar desde CDN (`index.global.min.js`)
- Carga `calendar.js` dinámicamente después de FullCalendar

**`user/reserve_form.html`**
- Selector de piso + selector de espacio con `optgroup` por piso
- Input de fecha (min=`date.today()`)
- Inputs de hora (start_time, end_time)
- Textarea de justificación

**`user/my_reservations.html`**
- Tabla con todas las reservas del usuario
- Badges de estado (pending, approved, rejected)

**`user/reservation_detail.html`**
- Detalles completos de la reserva
- Estado y fecha de revisión

### Templates de Admin

**`admin/dashboard.html`**
- Cards con estadísticas (total, pending, approved, rejected, spaces, users)
- Tabla de últimas 5 reservas pendientes
- Botón "Crear Administrador"

**`admin/reservations.html`**
- Filtros por estado (all, pending, approved, rejected)
- Tabla con todas las reservas

**`admin/reservation_detail.html`**
- Detalles completos de la reserva
- Botones "Aprobar" / "Rechazar"
- **Modal Bootstrap para rechazo** con textarea obligatorio para `rejection_reason`

**`admin/create_admin.html`**
- Formulario similar a registro
- Campos: email, password, confirm_password, name, student_id

### JavaScript

**`static/js/main.js`**
- `initializeNotifications()`: Inicializa polling de notificaciones (cada 30s)
- `loadNotifications()`: Carga notificaciones desde API
- `updateNotificationCount()`: Actualiza badge
- `markNotificationAsRead(id)`: Marca como leída
- `markAllNotificationsAsRead()`: Marca todas como leídas
- `getNotificationIcon(type)`: Icono según tipo
- `formatDate(dateString)`: Formatea fechas

**`static/js/calendar.js`**
- `initializeCalendar()`: Configura FullCalendar
  - Vista: `dayGridMonth`
  - Locale: `es`
  - Eventos desde `/user/api/reservations`
  - Tooltips con `tippy.js` (si está disponible)
  - Colores: Verde (#28a745) para aprobadas, Amarillo (#ffc107) para pendientes
- `loadReservations(fetchInfo, successCallback, failureCallback)`: Carga eventos desde API
  - Procesa eventos con `allDay: false`
  - Formato: `YYYY-MM-DDTHH:MM:SS`
  - Incluye `extendedProps` con detalles
  - Filtra por piso cuando se selecciona en el UI

**`static/js/notifications.js`**: Funciones auxiliares de notificaciones

### CSS

**`static/css/styles.css`**
- Estilos para navbar, notificaciones
- Ajustes de texto (`word-wrap`, `overflow-wrap`, `white-space`)
- Estilos de eventos del calendario
- Responsive design

---

## 🔄 FLUJOS PRINCIPALES DEL SISTEMA

### 1. Registro de Usuario

```
Usuario → /auth/register (POST)
  → AuthService.register_user()
    → UserRepository.create_user()
      → Supabase: INSERT INTO users
  → Redirect a /auth/login
```

### 2. Login

```
Usuario → /auth/login (POST)
  → AuthService.login_user()
    → UserRepository.get_user_by_email()
    → check_password_hash()
  → Session: user_id, email, name, role
  → Redirect según rol:
     - admin → /admin/dashboard
     - user → /user/calendar
```

### 3. Crear Reserva (Usuario)

```
Usuario → /user/reserve (POST)
  → ReservationService.create_reservation()
    → Validar fecha (no pasada)
    → ReservationRepository.check_time_conflict()
    → ReservationRepository.create_reservation()
      → Supabase: INSERT INTO reservations (status='pending')
    → ReservationService._notify_admins_new_reservation()
      → NotificationRepository.create_notification() para cada admin
        → Supabase: INSERT INTO notifications
  → Redirect a /user/my_reservations
```

### 4. Visualizar Calendario

```
Usuario → /user/calendar (GET)
  → Render template con spaces
  → JavaScript: initializeCalendar()
    → FullCalendar carga
    → Fetch a /user/api/reservations
      → ReservationService.get_all_reservations()
        → Filtrar aprobadas y pendientes
        → Formatear para FullCalendar
    → Mostrar eventos en calendario
```

### 5. Admin Revisa Reserva

```
Admin → /admin/dashboard
  → Ver notificación (si hay nueva reserva)
  → Click en notificación
    → Redirect a /admin/reservations/<id>
      → ReservationService.get_reservation_by_id()
        → Render template con detalles
```

### 6. Admin Aprueba Reserva

```
Admin → /admin/reservations/<id>/approve (POST)
  → ReservationService.approve_reservation()
    → Validar status='pending'
    → ReservationRepository.update_reservation_status('approved')
      → Supabase: UPDATE reservations
    → NotificationRepository.create_notification() para el usuario
      → Supabase: INSERT INTO notifications
  → Redirect a /admin/reservations/<id>
```

### 7. Admin Rechaza Reserva

```
Admin → /admin/reservations/<id>/reject (POST)
  → Validar rejection_reason (mínimo 10 caracteres)
  → ReservationService.reject_reservation()
    → Validar status='pending'
    → ReservationRepository.update_reservation_status('rejected', rejection_reason)
      → Supabase: UPDATE reservations (incluye rejection_reason)
    → NotificationRepository.create_notification() con la razón
      → Supabase: INSERT INTO notifications
  → Redirect a /admin/reservations/<id>
```

### 8. Sistema de Notificaciones

```
Polling cada 30s (main.js)
  → GET /notifications/api/unread_count
    → NotificationService.get_unread_count()
  → GET /notifications/api/list?unread_only=true
    → NotificationService.get_user_notifications(unread_only=True)
  → Actualizar badge y dropdown
```

---

## ✅ FUNCIONALIDADES IMPLEMENTADAS

### Usuario

- [x] Registro e inicio de sesión
- [x] Calendario visual con FullCalendar.js
  - [x] Vista mensual
  - [x] Selector de piso + selector de espacios con `optgroup`
  - [x] Filtro por piso en calendario (sin seleccionar espacio)
  - [x] Eventos con colores (verde aprobadas, amarillo pendientes)
  - [x] Tooltips con detalles
  - [x] Eventos solo en días específicos (no todo el mes)
- [x] Solicitud de reserva con formulario
  - [x] Validación de fecha (no pasada)
  - [x] Validación de horarios (end > start)
  - [x] Validación de conflictos de horario
  - [x] Filtro por piso en formulario de reserva
- [x] Ver mis reservas
- [x] Ver detalle de reserva
- [x] Recibir notificaciones de aprobación/rechazo
- [x] Sistema de notificaciones en tiempo real (polling)

### Administrador

- [x] Dashboard con estadísticas
  - [x] Total de reservas
  - [x] Reservas pendientes/aprobadas/rechazadas
  - [x] Total de espacios y usuarios
- [x] Ver todas las reservas (con filtros por estado)
- [x] Ver detalle de reserva
- [x] Aprobar reservas
- [x] Rechazar reservas
  - [x] Modal Bootstrap personalizado
  - [x] Razón de rechazo obligatoria (mínimo 10 caracteres)
- [x] Recibir notificaciones de nuevas solicitudes
- [x] Crear nuevos administradores desde el panel

### Sistema

- [x] Autenticación con sesiones Flask
- [x] Decoradores `@login_required` y `@admin_required`
- [x] Flash messages con auto-dismiss
- [x] Validación de conflictos de horario
- [x] Notificaciones en tiempo real (polling cada 30s)
- [x] Manejo de errores y validaciones
- [x] Clasificación de espacios por piso (planta baja, piso 1, piso 2)

---

## 🐛 PROBLEMAS RESUELTOS Y NOTAS TÉCNICAS

### 1. Error: `AttributeError: 'str' object has no attribute 'today'`

**Problema:** Conflicto de nombres al importar `datetime.date` y usar variable `date` del formulario.

**Solución:** Renombrar variable `date` → `reservation_date` en `app/routes/user_routes.py`:
```python
from datetime import date as date_module
reservation_date = request.form.get('date')
min_date = date_module.today().isoformat()
```

### 2. Error: `postgrest.exceptions.APIError: Could not embed because more than one relationship was found`

**Problema:** Supabase no sabía qué relación usar cuando había múltiples FKs a `users`.

**Solución:** Especificar la relación explícitamente:
```python
users!reservations_user_id_fkey(*)  # En lugar de users(*)
```

### 3. Calendario mostraba eventos en todo el mes en lugar de días específicos

**Problema:** FullCalendar interpretaba eventos como `allDay: true`.

**Solución:**
- En `user_routes.py`: Asegurar `allDay: False` y formato correcto `YYYY-MM-DDTHH:MM:SS`
- En `calendar.js`: Procesar eventos con `allDay: false` y `start`/`end` completos

### 4. Error de sintaxis en `calendar.js` (comentario con `#`)

**Problema:** Se usó `#` para comentario en JavaScript (es Python).

**Solución:** Cambiar a `//`.

### 5. FullCalendar no cargaba

**Problema:** Orden de carga de scripts incorrecto.

**Solución:** Cargar `index.global.min.js` de FullCalendar directamente en `calendar.html`, luego cargar `calendar.js` dinámicamente después de verificar que FullCalendar está disponible.

### 6. Texto de notificaciones se cortaba

**Problema:** CSS no permitía wrap del texto.

**Solución:** Agregar `word-wrap: break-word`, `overflow-wrap: break-word`, `white-space: normal` y ajustar estructura HTML con `d-flex` y `flex-grow-1`.

### 7. Validación de conflictos de horario

**Nota técnica:** `check_time_conflict` convierte strings de tiempo a objetos `datetime.time` para comparación precisa:
```python
new_start_time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
# Compara con horarios de reservas existentes
```

### 8. Migración de columna `floor` en `spaces`

**Problema:** El filtro por piso requiere la columna `floor` en la tabla `spaces`.

**Solución:** Agregar columna y luego poblar por prefijo:
```sql
ALTER TABLE spaces
ADD COLUMN IF NOT EXISTS floor VARCHAR(20) NOT NULL DEFAULT 'planta_baja'
CHECK (floor IN ('planta_baja','piso_1','piso_2'));

UPDATE spaces
SET floor = CASE
  WHEN name LIKE 'A-0%' THEN 'planta_baja'
  WHEN name LIKE 'A-1%' THEN 'piso_1'
  WHEN name LIKE 'A-2%' THEN 'piso_2'
  ELSE floor
END;
```

---

## 🚀 PRÓXIMAS MEJORAS

### En Desarrollo

- [ ] **Chatbot con procesamiento de lenguaje natural**
  - Consultar disponibilidad de espacios
  - Consultar capacidad de espacios
  - Listar espacios disponibles
  - Consultar reservas del usuario
  - Interfaz de chat con sugerencias

### Pendientes

- [ ] Edición de reservas
- [ ] Cancelación de reservas
- [ ] Filtros avanzados en el calendario
- [ ] Exportar calendario (iCal)
- [ ] Notificaciones por email
- [ ] Historial de cambios de reservas
- [ ] Búsqueda de espacios
- [ ] Vista de calendario semanal/diaria
- [ ] Validación de disponibilidad en tiempo real
- [ ] Reportes y estadísticas avanzadas

---

## 🆕 ACTUALIZACIONES RECIENTES (Ene 2026)

- Horarios de clases por aula (`class_schedules`): bloquean reservas, se muestran en el formulario; admin CRUD en “Horarios aulas”.
- Reservas del día: al elegir aula/fecha en el formulario se listan reservas pendientes/aprobadas de ese día.
- Categoría de laboratorio: se muestra como “Laboratorio (Computación/Medicina)” en selects y listados.
- Edición de reservas pendientes por el usuario: vista de edición con mismas validaciones (clases, solapes, fecha futura).
- Cancelación por el usuario (pendientes): requiere motivo; registra bitácora de eliminación con admin_id NULL; notificación al usuario.
- Eliminación por admin: requiere justificación en modal; notifica al usuario con motivo; registra en bitácora.
- Bitácora de eliminaciones (`reservation_deletions`): vista “Bitácora eliminaciones” con filtros por espacio, usuario, admin, rango de fechas.
- UX formulario: botón Enviar se deshabilita si hay solape con clases/otras reservas o fin<=inicio; se muestra nota indicando el motivo.

---

## 📝 NOTAS IMPORTANTES PARA DESARROLLO

### Variables de Entorno

- El archivo `.env` debe estar en la raíz (`ReservasPuce/.env`)
- Nunca commitear el `.env` (debe estar en `.gitignore`)

### Sesiones Flask

- Las sesiones se almacenan en el servidor (default: cookies firmadas)
- `SECRET_KEY` debe ser segura en producción

### Supabase

- Usar `anon key` en `SUPABASE_KEY`
- Las relaciones deben especificarse explícitamente cuando hay ambigüedad
- Los joins se hacen con sintaxis `table!foreign_key_name(*)`
- La tabla `spaces` incluye `floor` y se recomienda poblarla desde el prefijo `A-0/A-1/A-2`

### FullCalendar

- Usar `index.global.min.js` desde CDN
- Eventos con hora deben tener `allDay: false`
- Formato de fecha/hora: `YYYY-MM-DDTHH:MM:SS`
- El API `/user/api/reservations` acepta `floor` para filtrar eventos por piso

### Notificaciones

- Polling cada 30 segundos (configurable en `main.js`)
- Las notificaciones se crean automáticamente al aprobar/rechazar

### Validaciones

- Fecha no puede ser pasada
- Hora de fin debe ser mayor que hora de inicio
- Rechazo requiere razón de al menos 10 caracteres
- Conflictos de horario se verifican antes de crear reserva

---

## 🎯 ESTADO ACTUAL DEL PROYECTO

**Versión:** 1.0 (Funcional, con mejoras pendientes)  
**Última actualización:** Enero 2026

### Funcionalidades Completas
- ✅ Autenticación completa
- ✅ CRUD de reservas
- ✅ Sistema de notificaciones
- ✅ Panel de administración
- ✅ Calendario interactivo
- ✅ Validaciones y conflictos

### Próximo Paso
- 🔄 Implementar Chatbot con NLP básico para aumentar complejidad del proyecto

---

## 📞 REFERENCIAS Y DOCUMENTACIÓN

- **Flask:** https://flask.palletsprojects.com/
- **Supabase:** https://supabase.com/docs
- **FullCalendar:** https://fullcalendar.io/docs
- **Bootstrap 5:** https://getbootstrap.com/docs/5.0/

---

**Documento creado para facilitar la continuación del desarrollo desde cualquier ubicación.**  
**Última actualización:** Enero 2026
