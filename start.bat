@echo off
REM Lanzador rápido para Monitor Vital en Electron

echo.
echo ============================================
echo  MONITOR VITAL: DRA. PERFINKA
echo ============================================
echo.

REM Verifica si Node está instalado
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js no está instalado
    echo Descárgalo de: https://nodejs.org
    pause
    exit /b 1
)

REM Verifica si package.json existe
if not exist package.json (
    echo [ERROR] package.json no encontrado
    echo Asegúrate de estar en la carpeta correcta
    pause
    exit /b 1
)

REM Instala dependencias si es necesario
if not exist node_modules (
    echo [INFO] Instalando dependencias...
    call npm install
)

echo.
echo [INFO] Iniciando aplicación...
echo.

REM Inicia Electron
call npm start

pause
