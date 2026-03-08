@echo off
REM Lanzador rápido para Monitor Vital en Python

echo.
echo ============================================
echo  MONITOR VITAL: DRA. PERFINKA (Python)
echo ============================================
echo.

REM Verifica si Python está instalado
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no está instalado
    echo Descárgalo de: https://www.python.org
    pause
    exit /b 1
)

REM Verifica si pywebview está instalado
python -c "import webview" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Instalando PyWebView...
    call pip install pywebview
)

echo.
echo [INFO] Iniciando aplicación...
echo.

REM Inicia la app Python
call python run_game.py

pause
