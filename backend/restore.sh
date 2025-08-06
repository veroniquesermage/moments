#!/bin/bash

DB_USER="moments"
DB_PASSWORD="moments"
DB_NAME="moments"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "❌ Tu dois passer le chemin du fichier .sql en argument."
  echo "   Exemple : ./restore.sh backups/dev_dump_2025-08-06_09h17m.sql"
  exit 1
fi

echo "⚠️  Cette opération va SUPPRIMER toutes les données de la base '$DB_NAME' avant restauration."
read -p "✅ Tu confirmes ? (oui/non) : " CONFIRM

if [[ "$CONFIRM" != "oui" ]]; then
  echo "❌ Annulé."
  exit 1
fi

echo "🧹 Drop du schéma public..."
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "🔄 Restauration de $BACKUP_FILE vers la base $DB_NAME..."
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -f "$BACKUP_FILE"

echo "✅ Restauration terminée."
