#!/bin/bash
cd /app || exit 1
python /app/script/cleanup_reservations.py >> /app/logs/cleanup.log 2>&1
python /app/script/cleanup_refresh_tokens.py >> /app/logs/cleanup.log 2>&1
