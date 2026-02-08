# Documentación para rúbricas (BD en la Nube + IHC)

Este documento consolida la evidencia del proyecto y completa los apartados
que pide la rúbrica. Está pensado para copiar/pegar en la presentación.

---

## 1) Base de Datos en la Nube

### 1.1 Análisis y selección del modelo cloud
**Modelo elegido:** DBaaS/BaaS (Supabase) sobre PostgreSQL.  
**Justificación:**
- Reduce mantenimiento (backups, parches, upgrades y monitoreo gestionados).
- Escala horizontal y vertical sin migraciones complejas.
- Tiempo de implementación rápido para un proyecto académico.
- Provee API/SDK lista para integración y autenticación segura.
- Permite enfocarse en lógica de negocio y UX.

**Alternativas descartadas:**
- **IaaS:** mayor control pero mayor costo operativo y complejidad.
- **PaaS genérico:** aún requiere administrar y asegurar la BD.
- **SaaS cerrado:** poca flexibilidad para un modelo de datos propio.

---

### 1.2 Arquitectura de la base de datos en la nube
**Arquitectura en capas:**
```
Frontend (Jinja2 + JS)
   ↕
Routes (Flask)
   ↕
Services (lógica)
   ↕
Repositories (Supabase)
   ↕
Supabase (PostgreSQL)
```

**Componentes clave:**
- **Supabase** como DBaaS (PostgreSQL administrado).
- **Backend Flask** consume el SDK de Supabase.
- **Repositorio** centraliza consultas y joins.

**Punto de conexión:** variables `SUPABASE_URL` y `SUPABASE_KEY` en `.env`.

**Nota:** La región física depende de la configuración del proyecto Supabase.
Se recomienda consignarla en la presentación (ej. `sa-east-1`, `us-east-1`, etc.).

---

### 1.3 Modelo de datos
**Tablas principales:**
- `users`
- `spaces`
- `reservations`
- `notifications`
- `class_schedules`
- `reservation_deletions`

**Relaciones clave:**
- `reservations.user_id → users.id`
- `reservations.space_id → spaces.id`
- `reservations.admin_id → users.id`
- `notifications.user_id → users.id`

**Integridad:**
PK/FK, `CHECK` constraints, índices por estado, fecha y relación.

**Evidencia:** `app/scripts/01_schema.sql`.

---

### 1.4 Documentación de seguridad
**Autenticación:**
- Contraseñas hasheadas con `Werkzeug`.
- Verificación de cuenta por correo (código con expiración).

**Control de acceso:**
- Roles `user/admin`.
- Decoradores `@login_required` y `@admin_required`.

**Datos sensibles:**
- `.env` excluido de git.
- `SECRET_KEY` para sesiones.

**Recomendación de mejora:**
- Activar y documentar RLS en Supabase (políticas por rol).
- Usar `service_role` solo en backend privado (nunca en frontend).

---

### 1.5 Gestión de riesgos y amenazas
**Riesgos identificados y mitigación:**
1. **SQL Injection**  
   Mitigación: uso de SDK Supabase y validaciones de entrada.
2. **Filtración de credenciales**  
   Mitigación: `.env` fuera de repositorio, rotación de claves.
3. **Mala configuración de permisos**  
   Mitigación: roles y políticas RLS, revisiones periódicas.
4. **Acceso no autorizado**  
   Mitigación: verificación de cuenta, sesiones, control de rutas.
5. **Pérdida de datos**  
   Mitigación: backups automáticos de Supabase + logs.

---

### 1.6 Implementación de la BD en la nube
**Evidencia técnica:**
- Schema completo con constraints e índices.
- Inserción de datos iniciales.
- Integración directa con repositorios Supabase.

**Resultado:** BD funcional con operaciones CRUD y validaciones.

---

### 1.7 Seguridad técnica de la BD
**Implementado:**
- Hash de contraseñas.
- Validaciones de conflictos y reglas de negocio.

**Pendiente para destacar en presentación:**
- RLS en Supabase.
- Separación de keys (`anon` para cliente, `service_role` solo backend).
- Restricción de IPs/entornos si aplica.

---

### 1.8 Cifrado y protección de datos
**Cifrado en tránsito:** TLS (HTTPS/SSL) en Supabase.  
**Cifrado en reposo:** administrado por Supabase.  
**Protección adicional:** tokens/keys en `.env`, no en código.

---

### 1.9 Integración BD – Aplicación
**Evidencia:**
- Repositorios en `app/repositories/supabase`.
- Servicios en `app/services`.
- Rutas en `app/routes`.

**Resultado:** integración consistente, separando lógica de negocio y acceso a datos.

---

### 1.10 Innovación (BD)
**Aportes diferenciadores:**
- Calendario interactivo con FullCalendar.
- Notificaciones en tiempo real.
- Chatbot híbrido (DeepSeek + rule-based).
- Bitácora de eliminaciones.

---

### 1.11 Calidad y estructura de presentación
**Sugerencia de estructura para slides:**
1. Problema y objetivo.
2. Arquitectura general (diagrama por capas).
3. Modelo de datos (ER simplificado).
4. Flujo completo del sistema (usuario/admin).
5. Seguridad, riesgos y mitigación.
6. Demo visual (capturas).
7. Resultados y mejoras.

---

### 1.12 Habilidades comunicativas (guía)
- Explicar decisiones técnicas con ejemplos simples.
- Mostrar una demo con 2 flujos: reserva y aprobación.
- Responder preguntas desde la evidencia del repo.

---

## 2) Interacción Humano‑Computador (IHC)

### 2.1 Claridad y estructura
**Puntos fuertes:**
- Layout consistente con navbar y secciones.
- Calendario central como punto focal.
- Flujos de usuario y admin diferenciados.

**Recomendación:** mostrar flujo en slides con capturas ordenadas.

---

### 2.2 Habilidades comunicativas
**Guía de exposición:**
- Iniciar con el problema real (gestión de espacios).
- Mostrar “antes/después” respecto a procesos manuales.
- Explicar cómo el calendario reduce errores.

---

### 2.3 Soporte visual
**Pendiente para completar:**
- Capturas de: login, calendario, formulario de reserva, dashboard, detalle de reserva.
- Diagrama simple del flujo (usuario → admin).

---

### 2.4 Innovación
**Elementos innovadores:**
- Chatbot híbrido para consultas rápidas.
- Notificaciones en tiempo real.
- Validación automática de conflictos de horario.

---

### 2.5 Complejidad técnica
**Indicadores:**
- Integración Supabase + Flask + FullCalendar.
- Roles con permisos diferenciados.
- Bitácora de eliminaciones y notificaciones.

---

### 2.6 Valor agregado
**Beneficios:**
- Reduce errores por solape de horarios.
- Automatiza aprobación/rechazo y notifica en segundos.
- Aumenta transparencia y trazabilidad.

---

## 3) Evidencia técnica en el repositorio

**Arquitectura y stack:**
- `README.md`, `CONTEXTO_PROYECTO.md`

**Schema y BD:**
- `app/scripts/01_schema.sql`

**Integración con Supabase:**
- `app/repositories/supabase/*`

**Lógica de negocio:**
- `app/services/*`

**UI y UX:**
- `app/templates/*`
- `app/static/*`

---

## 4) Checklist rápido antes de la entrega

- [ ] Añadir capturas (login, calendario, admin).
- [ ] Añadir diagrama ER (puede ser simple).
- [ ] Indicar región de Supabase en la presentación.
- [ ] Mencionar RLS y políticas de acceso (si aplica).
- [ ] Ensayar demo con flujo completo.
