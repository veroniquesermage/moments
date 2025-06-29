#!/bin/bash

# Lancer cron
cron

# Lancer FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port 8000