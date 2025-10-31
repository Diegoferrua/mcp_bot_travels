@echo off
REM ============================================================================
REM SCRIPT DE EJECUCIÓN - IA ASSISTANT PRO
REM ============================================================================

echo.
echo ========================================================================
echo   EJECUTANDO - IA ASSISTANT PRO
echo ========================================================================
echo.

REM Verificar si existe el entorno virtual
if not exist venv (
    echo [ERROR] No se encontro el entorno virtual 'venv'
    echo Por favor ejecuta primero: setup.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [1/3] Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno activado
echo.

REM Verificar archivo .env
echo [2/3] Verificando configuracion...
if not exist .env (
    echo [ERROR] No se encontro el archivo .env
    echo Por favor ejecuta: copy .env.example .env
    echo Y configura tu OPENAI_API_KEY
    pause
    exit /b 1
)
echo [OK] Archivo .env encontrado
echo.

REM Ejecutar aplicación
echo [3/3] Iniciando aplicacion web...
echo.
echo ========================================================================
echo   La aplicacion se abrira en tu navegador
echo   Presiona Ctrl+C para detenerla
echo ========================================================================
echo.
streamlit run app.py

pause


