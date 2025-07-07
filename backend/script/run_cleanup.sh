##!/bin/bash
cp /app
python /app/script/cleanup_reservations.py >> /app/logs/cleanup.log 2>&1
