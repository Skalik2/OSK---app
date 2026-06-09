pushd .
cd auth_service
. ..\venv\Scripts\Activate.ps1
python -m pytest tests/ -v
popd

pushd .
cd app
. ..\venv\Scripts\Activate.ps1
python -m pytest tests/ -v
popd