#!/bin/bash
cd /app
/usr/local/bin/python /app/script/cleanup_bdd.py >> /app/logs/cleanup.log 2>&1
/app/script/backup_db.sh >> /app/logs/backup.log 2>&1