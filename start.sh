#!/usr/bin/env bash

# Python виртуалды ортаны активтендіру
source venv/bin/activate

# Uvicorn-ды тікелей шақыру
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT