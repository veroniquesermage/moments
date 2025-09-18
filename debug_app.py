#!/usr/bin/env python3
"""
Application FastAPI pour le débogage - complètement isolée
"""
import os
import sys
from pathlib import Path

def create_debug_app():
    # Configuration environnement
    backend_path = Path(__file__).parent / "backend"
    os.chdir(backend_path)
    sys.path.insert(0, str(backend_path))

    os.environ["PYTHONPATH"] = str(backend_path)
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["APP_ENV"] = "dev"

    from fastapi import FastAPI
    from starlette.middleware.cors import CORSMiddleware

    # App complètement nouvelle
    debug_app = FastAPI(title="Moments Debug", version="1.0.0")

    # CORS
    debug_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes de test
    @debug_app.get("/")
    async def debug_root():
        return {"message": "🐛 FastAPI Debug Mode Active"}

    @debug_app.get("/health")
    async def debug_health():
        return {"status": "debug", "port": 8000}

    # Ajouter UNE route spécifique pour tester
    @debug_app.get("/debug/gifts")
    async def debug_gifts():
        return {"gifts": [], "debug": True}

    return debug_app

def main():
    print("🐛 Création app debug isolée")
    print("=" * 50)

    app = create_debug_app()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug", reload=False)

if __name__ == "__main__":
    main()