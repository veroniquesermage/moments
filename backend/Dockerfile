FROM python:3.11-slim

WORKDIR /app

# Installer cron et postregsql
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    cron \
    postgresql-client-16 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Copier requirements et installer les deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Ajouter le cron et le script de démarrage
COPY cron/cleanup.cron /etc/cron.d/cleanup-cron
COPY start.sh /app/start.sh

# Droits pour cron et le start.sh
RUN chmod 0644 /etc/cron.d/cleanup-cron && \
    crontab /etc/cron.d/cleanup-cron && \
    chmod +x /app/start.sh && \
    chmod +x /app/script/backup_db.sh && \
    chmod +x /app/script/run_cleanup.sh


# Port FastAPI
EXPOSE 8000

# Commande par défaut
CMD ["/app/start.sh"]