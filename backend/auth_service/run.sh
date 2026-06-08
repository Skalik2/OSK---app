#!/bin/bash
source venv/bin/activate
uvicorn auth_service.main:app --port 8001 --reload

# run from .../backend/