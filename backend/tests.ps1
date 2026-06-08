. venv\Scripts\Activate.ps1
python -m pytest auth_service/tests/ -v
python -m pytest app/tests/ -v
Read-Host -Prompt "Press Enter to exit"