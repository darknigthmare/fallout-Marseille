@echo off
where python >nul 2>nul || (echo Python 3 requis pour le mode application. & pause & exit /b 1)
python "%~dp0tools\serve_game.py"
