@echo off
where python >nul 2>nul || (echo Python 3 requis. & pause & exit /b 1)
python "%~dp0tools\benchmark_map_v041.py"
pause
