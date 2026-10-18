@echo off
setlocal
where python >nul 2>nul || (echo Python 3 est requis pour reconstituer et lancer le jeu. & pause & exit /b 1)
python "%~dp0RECONSTRUIRE_ARCHIVE.py"
set "RESULT=%ERRORLEVEL%"
pause
exit /b %RESULT%
