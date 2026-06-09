if (-not (Test-Path "venv")) {
    python -m venv venv

    . venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r ..\requirements.txt
} else {
    . venv\Scripts\Activate.ps1
}
uvicorn main:app --port 8001 --reload