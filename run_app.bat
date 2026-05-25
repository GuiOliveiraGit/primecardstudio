@echo off
if exist "%~dp0.qa_venv\Scripts\python.exe" (
    "%~dp0.qa_venv\Scripts\python.exe" "%~dp0main.py"
) else (
    set "PYTHONPATH=%~dp0.vendor_packages;%PYTHONPATH%"
    python "%~dp0main.py"
)
