@echo off
cd /d "%~dp0"
echo ========================================
echo GRANTLY - Quick start
echo ========================================
where docker >nul 2>nul
if %errorlevel%==0 (
  echo Starting GRANTLY with Docker Compose...
  docker compose up --build
) else (
  echo Docker Desktop was not found.
  echo Please install Docker Desktop, then run this file again.
  echo Manual setup instructions are in README.md.
  pause
)
