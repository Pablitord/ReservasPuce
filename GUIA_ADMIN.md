# Guía para Crear Administradores

Hay varias formas de crear usuarios administradores en el sistema:

## 📋 Opción 1: Usando el Script Python (Recomendado)

### Pasos:

1. **Asegúrate de tener el entorno virtual activado:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Ejecuta el script:**
   ```powershell
   python create_admin.py
   ```

3. **Sigue las instrucciones:**
   - Ingresa el email del administrador
   - Ingresa la contraseña (mínimo 6 caracteres)
   - Ingresa el nombre completo
   - Ingresa el ID de estudiante (opcional, presiona Enter para generar uno automático)

4. **Confirma la creación**

✅ **Ventajas:**
- Fácil de usar
- Valida los datos
- Hashea la contraseña correctamente
- Verifica que el email no esté duplicado

---

## 📋 Opción 2: Directamente desde Supabase

### Pasos:

1. **Accede a tu proyecto en Supabase:**
   - Ve a [supabase.com](https://supabase.com)
   - Inicia sesión
   - Selecciona tu proyecto

2. **Ve al SQL Editor:**
   - Haz clic en "SQL Editor" en el menú lateral

3. **Ejecuta este SQL (reemplaza los valores):**
   ```sql
   INSERT INTO users (email, password_hash, name, student_id, role)
   VALUES (
       'admin2@puce.edu.ec',  -- Email del admin
       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5KqZz8eHGqR1q',  -- Hash de 'admin123'
       'Nombre del Admin',  -- Nombre completo
       'ADMIN002',  -- ID único
       'admin'  -- Rol
   );
   ```

4. **Para generar el hash de una contraseña personalizada:**
   
   Puedes usar Python:
   ```python
   from werkzeug.security import generate_password_hash
   password = "tu_contraseña_aqui"
   print(generate_password_hash(password))
   ```
   
   O usar este comando en Python:
   ```powershell
   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('tu_contraseña'))"
   ```

⚠️ **Nota:** Usa esta opción solo si sabes cómo generar el hash de contraseña correctamente.

---

## 📋 Opción 3: Convertir un Usuario Existente en Admin

Si ya tienes un usuario registrado y quieres convertirlo en administrador:

1. **Ve a Supabase → Table Editor → users**

2. **Busca el usuario por email**

3. **Edita el campo `role` y cámbialo de `user` a `admin`**

O ejecuta este SQL:
```sql
UPDATE users 
SET role = 'admin' 
WHERE email = 'email_del_usuario@puce.edu.ec';
```

---

## 📋 Opción 4: Usar el Admin por Defecto

Si ejecutaste el schema SQL (`01_schema.sql`), ya tienes un admin creado:

- **Email:** `admin@puce.edu.ec`
- **Contraseña:** `admin123`
- **Rol:** `admin`

⚠️ **IMPORTANTE:** Cambia esta contraseña en producción.

---

## 🔐 Cambiar Contraseña de un Admin

Si necesitas cambiar la contraseña de un administrador existente:

### Opción A: Desde Python

```python
from werkzeug.security import generate_password_hash

# Generar nuevo hash
nueva_contraseña = "nueva_contraseña_segura"
password_hash = generate_password_hash(nueva_contraseña)
print(f"Hash: {password_hash}")
```

Luego en Supabase SQL Editor:
```sql
UPDATE users 
SET password_hash = 'EL_HASH_GENERADO_AQUI' 
WHERE email = 'admin@puce.edu.ec';
```

### Opción B: Usando el Script

Podrías modificar `create_admin.py` para que también permita actualizar usuarios existentes.

---

## ✅ Verificar que un Usuario es Admin

Puedes verificar en Supabase:

```sql
SELECT id, email, name, role 
FROM users 
WHERE role = 'admin';
```

O desde la aplicación, si eres admin, puedes ver todos los usuarios en el dashboard.

---

## 🚀 Recomendaciones

1. **Usa el script Python** (`create_admin.py`) para la mayoría de casos - es más seguro y fácil
2. **Nunca compartas las contraseñas** de los administradores
3. **Cambia la contraseña por defecto** del admin inicial
4. **Usa contraseñas seguras** (mínimo 8 caracteres, con mayúsculas, números y símbolos)
5. **Limita el número de administradores** - solo crea los necesarios

---

## 📝 Notas Importantes

- El campo `student_id` debe ser único para cada usuario
- El email también debe ser único
- Los admins pueden ver el dashboard, aprobar/rechazar reservas y ver todas las reservas
- Los usuarios normales solo pueden crear reservas y ver las suyas
