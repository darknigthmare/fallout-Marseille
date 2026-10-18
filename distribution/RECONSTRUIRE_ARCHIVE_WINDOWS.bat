@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (python RECONSTRUIRE_ARCHIVE.py) else (py -3 RECONSTRUIRE_ARCHIVE.py)
pause
