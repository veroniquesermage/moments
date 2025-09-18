#!/usr/bin/env python3
"""
Script pour lancer FastAPI en mode développement avec débogage
Usage:
    python run_dev.py
"""
import os
import sys
from pathlib import Path

def main():
    # Se positionner dans le dossier backend
    backend_path = Path(__file__).parent / "backend"
    os.chdir(backend_path)

    # Ajouter le backend au PYTHONPATH
    sys.path.insert(0, str(backend_path))

    # Variables d'environnement
    os.environ["PYTHONPATH"] = str(backend_path)
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["APP_ENV"] = "dev"

    print(f"Démarrage FastAPI depuis: {os.getcwd()}")
    print("Mode développement avec débogage activé")
    print("=" * 50)

    # Importer et lancer uvicorn SANS reload pour le débogage
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Désactivé pour permettre le débogage
        log_level="info"
    )

if __name__ == "__main__":
    main()