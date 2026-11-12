@echo off
REM Duplo clique aqui sobe o NextBarber em http://localhost:3000
REM Nao precisa de npm install: usa so o Node.
cd /d "%~dp0"
where node >nul 2>&1
if errorlevel 1 (
  echo.
  echo   Node nao encontrado. Instale em https://nodejs.org
  echo.
  pause
  exit /b 1
)
node servidor.js %1
pause
