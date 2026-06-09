#!/bin/bash

if ! [ -d "venv" ] ; then
    python3.12 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r ../requirements.txt
else
    source venv/bin/activate
fi

uvicorn main:app --port 8000 --reload

# run from .../app/