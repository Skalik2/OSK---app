python -m venv venv
. venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Environment setup complete and dependencies installed." -ForegroundColor Green