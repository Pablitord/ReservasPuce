# Guía para Configurar el Entorno Virtual

## 📋 Pasos para Configurar el Entorno Virtual (Windows)

### Paso 1: Verificar que tienes Python instalado

Abre PowerShell o CMD y verifica la versión:
```powershell
python --version
```

Si no tienes Python instalado, descárgalo de [python.org](https://www.python.org/downloads/)

---

### Paso 2: Navegar al directorio del proyecto

```powershell
cd C:\Users\Manta_Lab1_005\Desktop\ReservasPuce
```

O si ya estás en otro directorio:
```powershell
cd Desktop\ReservasPuce
```

---

### Paso 3: Crear el entorno virtual

```powershell
python -m venv venv
```

Esto creará una carpeta llamada `venv` en tu proyecto con el entorno virtual.

---

### Paso 4: Activar el entorno virtual

**En PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Si tienes problemas de permisos en PowerShell, ejecuta primero:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**O usa CMD en su lugar:**
```cmd
venv\Scripts\activate.bat
```

**✅ Cuando esté activado, verás `(venv)` al inicio de tu línea de comando:**
```
(venv) PS C:\Users\Manta_Lab1_005\Desktop\ReservasPuce>
```

---

### Paso 5: Instalar las dependencias

Una vez activado el entorno virtual, instala los requirements:

```powershell
cd app
pip install -r requirements.txt
```

Esto instalará:
- Flask==3.0.0
- python-dotenv==1.0.0
- supabase==2.0.0
- Werkzeug==3.0.1
- Jinja2==3.1.2
- python-dateutil==2.8.2

---

### Paso 6: Verificar la instalación

Verifica que Flask se instaló correctamente:
```powershell
pip list
```

Deberías ver Flask y todas las dependencias listadas.

---

### Paso 7: Crear el archivo .env

Vuelve al directorio raíz:
```powershell
cd ..
```

Crea un archivo `.env` con las variables de entorno necesarias:
```powershell
# Puedes crearlo con notepad o desde PowerShell:
notepad .env
```

Copia y pega esto en el archivo `.env`:
```
SECRET_KEY=dev-secret-key-change-in-production
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-supabase-aqui
FLASK_DEBUG=True
HOST=127.0.0.1
PORT=5000
```

**⚠️ IMPORTANTE:** Reemplaza los valores de `SUPABASE_URL` y `SUPABASE_KEY` con tus credenciales reales de Supabase.

---

### Paso 8: Ejecutar la aplicación

```powershell
cd app
python run.py
```

Deberías ver algo como:
```
 * Running on http://127.0.0.1:5000
```

---

## 🔄 Para Futuras Sesiones

Cada vez que quieras trabajar en el proyecto:

1. **Abre PowerShell o CMD en el directorio del proyecto**
2. **Activa el entorno virtual:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. **Ejecuta la aplicación:**
   ```powershell
   cd app
   python run.py
   ```

---

## ❌ Desactivar el Entorno Virtual

Cuando termines de trabajar, puedes desactivar el entorno virtual:

```powershell
deactivate
```

---

## 🐛 Solución de Problemas

### Error: "python no se reconoce como comando"
- Verifica que Python está instalado: `python --version`
- Asegúrate de que Python está en tu PATH del sistema

### Error: "No se puede cargar el archivo porque la ejecución de scripts está deshabilitada"
Ejecuta en PowerShell como administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "pip no se reconoce"
- Asegúrate de que el entorno virtual está activado (verás `(venv)`)
- Instala pip: `python -m ensurepip --upgrade`

### Error al instalar dependencias
```powershell
pip install --upgrade pip
pip install -r app/requirements.txt
```

---

## 📝 Notas Importantes

- **Siempre activa el entorno virtual antes de instalar paquetes o ejecutar la aplicación**
- El entorno virtual (`venv`) debe estar en la carpeta `.gitignore` (ya está incluido)
- Cada proyecto debe tener su propio entorno virtual
- No subas la carpeta `venv` a repositorios Git
