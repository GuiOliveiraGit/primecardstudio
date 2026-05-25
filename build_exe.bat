@echo off
if exist "%~dp0.qa_venv\Scripts\python.exe" (
    "%~dp0.qa_venv\Scripts\python.exe" -m PyInstaller --noconfirm --windowed --name "PrimeStudio Card" main.py
) else (
    set "PYTHONPATH=%~dp0.vendor_packages;%PYTHONPATH%"
    python -m PyInstaller --noconfirm --windowed --name "PrimeStudio Card" main.py
)
echo.
echo Executavel criado em dist\PrimeStudio Card\
pause
