py -3.12 -m venv venv

. ./venv/Scripts/activate - na windows

uvicorn app.main:app --reload

# linux
# python3.12 -m venv venv
# source venv/bin/activate
# uvicorn app.main:app --reload
