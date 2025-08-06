#!/bin/bash

DB_USER="moments"
DB_PASSWORD="moments"
DB_NAME="moments"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="backups"

echo "🔄 Sauvegarde de la base..."
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT $DB_NAME > "$BACKUP_DIR/dev_dump_$(date +%Y-%m-%d_%Hh%Mm).sql"
echo "✅ Dump terminé."
