@echo off
where python >nul 2>nul || (echo Python 3 requis. & pause & exit /b 1)
python "%~dp0tools\install_local_pack_v041.py" --workers 3
pause
