#!/bin/bash

cd auth_service
source venv/bin/activate
python -m pytest tests/ -v

cd ../app
source venv/bin/activate
python -m pytest tests/ -v
cd ..

# run from .../backend/