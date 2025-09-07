#!/usr/bin/env python3
"""
Script pour lancer les tests facilement depuis la racine du projet
Usage:
    python run_tests.py                    # Tous les tests
    python run_tests.py unit               # Tests unitaires seulement
    python run_tests.py integration        # Tests d'intégration seulement
    python run_tests.py unit/services      # Tests des services seulement
"""
import sys
import subprocess
import os
from pathlib import Path

def main():
    # Se positionner dans le dossier backend
    backend_path = Path(__file__).parent / "backend"
    os.chdir(backend_path)
    
    # Arguments par défaut
    test_path = "tests/"
    
    # Si un argument est fourni, l'utiliser comme chemin
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["unit", "integration"]:
            test_path = f"tests/{arg}/"
        elif "/" in arg or "\\" in arg:
            test_path = f"tests/{arg}"
        else:
            test_path = f"tests/{arg}/"
    
    # Commande pytest
    cmd = ["python", "-m", "pytest", test_path, "-v", "--tb=short"]
    
    print(f"Lancement des tests: {test_path}")
    print(f"Repertoire de travail: {os.getcwd()}")
    print(f"Commande: {' '.join(cmd)}")
    print("=" * 50)
    
    # Lancer les tests
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nTests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du lancement des tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()