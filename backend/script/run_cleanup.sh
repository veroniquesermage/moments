#!/bin/bash
cd /app

# Nettoyage de la base de données
/usr/local/bin/python /app/script/cleanup_bdd.py >> /app/logs/cleanup.log 2>&1

# Backup de la base de données
/app/script/backup_db.sh >> /app/logs/backup.log 2>&1

# Nettoyage Docker (une fois par semaine, le dimanche)
if [ "$(date +%u)" = "7" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Nettoyage Docker hebdomadaire" >> /app/logs/cleanup.log
    /app/script/cleanup_docker.sh >> /app/logs/docker_cleanup.log 2>&1
fi