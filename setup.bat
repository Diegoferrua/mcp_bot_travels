@echo off
REM ============================================================================
REM SCRIPT DE INSTALACIÓN - IA ASSISTANT PRO
REM ============================================================================

echo.
echo ========================================================================
echo   INSTALACION - IA ASSISTANT PRO
echo ========================================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    echo Por favor instala Python desde: https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python detectado:
python --version
echo.

REM PASO 1: Crear entorno virtual
echo [PASO 1/4] Creando entorno virtual 'venv'...
if exist venv (
    echo [ADVERTENCIA] El directorio 'venv' ya existe
    echo Deseas eliminarlo y crear uno nuevo? (S/N)
    set /p respuesta=
    if /i "%respuesta%"=="S" (
        rmdir /s /q venv
        python -m venv venv
    )
) else (
    python -m venv venv
)

if not exist venv (
    echo [ERROR] No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado
echo.

REM PASO 2: Activar entorno virtual
echo [PASO 2/4] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado
echo.

REM PASO 3: Actualizar pip e instalar dependencias
echo [PASO 3/4] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM PASO 4: Configurar archivo .env
echo [PASO 4/4] Configurando archivo .env...
if exist .env (
    echo [OK] Archivo .env ya existe
) else (
    if exist .env.example (
        copy .env.example .env
        echo [OK] Archivo .env creado desde .env.example
        echo.
        echo [IMPORTANTE] Ahora debes editar el archivo .env y agregar tu API key:
        echo 1. Abre .env con un editor de texto
        echo 2. Reemplaza XXXXXXXX con tu API key real de OpenAI
        echo 3. Obten tu clave en: https://platform.openai.com/api-keys
    ) else (
        echo [ADVERTENCIA] No se encontro .env.example
    )
)
echo.

echo ========================================================================
echo   INSTALACION COMPLETADA
echo ========================================================================
echo.
echo SIGUIENTE PASO:
echo 1. Configura tu API key en el archivo .env
echo 2. Ejecuta la aplicacion con: venv\Scripts\activate.bat
echo    Luego: streamlit run app.py
echo.
echo Para activar el entorno virtual en el futuro:
echo    venv\Scripts\activate.bat
echo.
pause


