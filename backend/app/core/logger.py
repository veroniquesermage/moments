import logging
import os
from logging.handlers import RotatingFileHandler

# Crée un dossier 'logs' si besoin
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("liste2wish")
logger.setLevel(logging.DEBUG)  # Pour permettre tous les niveaux

# Format commun
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Handler console (affiche tout, y compris DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Handler fichier avec rotation (par défaut INFO et plus)
file_handler = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Ajout des handlers (éviter doublons si réimporté)
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
