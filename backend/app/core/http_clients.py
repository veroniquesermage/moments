import httpx
from app.core.logger import logger

# Client HTTP global réutilisable pour les APIs Google
google_client = httpx.AsyncClient(
    timeout=httpx.Timeout(
        connect=2.0,    # Timeout connexion TCP
        read=3.0,       # Timeout lecture réponse  
        write=5.0,      # Timeout écriture requête
        pool=5.0        # Timeout acquisition connexion du pool
    ),
    limits=httpx.Limits(
        max_connections=10,             # Max connexions simultanées
        max_keepalive_connections=5,    # Connexions keep-alive
        keepalive_expiry=30             # Durée keep-alive (30s)
    ),
    headers={
        "User-Agent": "Moments-API/1.0",
        "Accept": "application/json"
    }
)

async def close_http_clients():
    """Ferme proprement les clients HTTP au shutdown de l'application"""
    logger.info("Fermeture des clients HTTP...")
    await google_client.aclose()
    logger.info("Clients HTTP fermés")