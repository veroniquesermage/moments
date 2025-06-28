FROM python:3.11-slim

WORKDIR /app

# Installer cron
RUN apt-get update && apt-get install -y cron && apt-get clean

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
    chmod +x /app/start.sh

# Port FastAPI
EXPOSE 8000

# Commande par défaut
CMD ["/app/start.sh"]