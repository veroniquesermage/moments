#!/bin/bash

# Charger les variables d'environnement
set -o allexport
# Charger les variables d'environnement depuis le fichier .env
APP_ENV=${APP_ENV:-dev}
# shellcheck source=/dev/null
source /app/.env.${APP_ENV}
set +o allexport

# Valeurs par défaut au cas où
DB_USER="${POSTGRES_USER:-moments}"
DB_PASSWORD="${POSTGRES_PASSWORD:-moments}"
DB_NAME="${POSTGRES_DB:-moments}"
DB_HOST="${POSTGRES_HOST:-localhost}"

# Préparer le backup
export PGPASSWORD="$DB_PASSWORD"
BACKUP_DIR="/app/backups"
mkdir -p "$BACKUP_DIR"

DATE=$(date +\%Y-\%m-\%d_\%Hh\%Mm)
FILENAME="${DB_NAME}_${DATE}.sql"

# Lancer le dump
pg_dump -U "$DB_USER" -h "$DB_HOST" "$DB_NAME" > "$BACKUP_DIR/$FILENAME"

# Nettoyer les dumps vieux de plus de 7 jours
find "$BACKUP_DIR" -type f -name "${DB_NAME}_*.sql" -mtime +7 -exec rm {} \;

echo "✅ Backup terminé : $FILENAME"
