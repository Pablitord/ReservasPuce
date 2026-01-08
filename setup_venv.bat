@echo off
echo ========================================
echo    Configuracion del Entorno Virtual
echo    Sistema de Reservas PUCE
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Python detectado correctamente
echo.

REM Verificar si el entorno virtual ya existe
if exist "venv" (
    echo [ADVERTENCIA] El entorno virtual ya existe
    echo.
    set /p respuesta="Deseas eliminarlo y crear uno nuevo? (s/n): "
    if /i "%respuesta%"=="s" (
        echo Eliminando entorno virtual existente...
        rmdir /s /q venv
        echo.
    ) else (
        echo Usando el entorno virtual existente.
        echo.
        goto :activate
    )
)

REM Crear el entorno virtual
echo [2/4] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado exitosamente
echo.

:activate
REM Activar el entorno virtual
echo [3/4] Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado
echo.

REM Actualizar pip
echo [4/4] Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias
echo Instalando dependencias desde requirements.txt...
cd app
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un problema instalando las dependencias
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo    Configuracion completada exitosamente!
echo ========================================
echo.
echo El entorno virtual esta activo y las dependencias estan instaladas.
echo.
echo IMPORTANTE: No cierres esta ventana si vas a ejecutar la aplicacion.
echo Para ejecutar la aplicacion en otra ventana, primero ejecuta:
echo     venv\Scripts\activate.bat
echo     cd app
echo     python run.py
echo.
echo O simplemente ejecuta 'run.bat' en una nueva ventana.
echo.
pause
