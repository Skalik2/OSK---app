#!/bin/bash
source venv/bin/activate
python -m pytest auth_service/tests/ -v
python -m pytest app/tests/ -v

# run from .../backend/