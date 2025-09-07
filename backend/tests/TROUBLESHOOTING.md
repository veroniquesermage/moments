# Guide de Résolution des Problèmes - Tests

## 🚨 "No tests found in the selected file or folder"

### Causes possibles et solutions:

#### 1. **Configuration VS Code/IDE**
**Symptôme**: L'IDE ne trouve pas les tests dans la nouvelle structure hiérarchique.

**Solutions**:
```bash
# Option A: Utiliser le script de lancement
python run_tests.py unit                    # Tests unitaires
python run_tests.py integration             # Tests d'intégration  
python run_tests.py unit/services          # Tests des services

# Option B: Commande directe depuis backend/
cd backend
python -m pytest tests/ -v

# Option C: Test spécifique
cd backend  
python -m pytest tests/unit/services/test_gift_service_simple.py -v
```

**Configuration VS Code** (`.vscode/settings.json`):
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["backend/tests"],
    "python.testing.cwd": "./"
}
```

#### 2. **Répertoire de travail incorrect**
**Symptôme**: Tests lancés depuis le mauvais dossier.

**Solution**:
- Toujours lancer depuis la **racine du projet** (`moments/`)  
- Ou depuis `moments/backend/` avec le chemin `tests/`

#### 3. **Configuration pytest manquante**
**Symptôme**: pytest ne reconnaît pas la structure.

**Vérification**:
```bash
cd backend
python -m pytest --collect-only tests/
# Doit afficher 15 tests collectés
```

**Fichiers de config requis**:
- `pytest.ini` (racine et backend)
- `__init__.py` dans chaque dossier de tests
- `conftest.py` avec les fixtures

## 🔧 Autres Problèmes Fréquents

### Tests qui échouent après la réorganisation

**Cause**: Problèmes d'imports ou de fixtures isolées

**Solutions**:
1. **Utiliser les tests simples** en attendant l'adaptation:
   ```bash
   python run_tests.py unit/services/test_gift_service_simple.py
   ```

2. **Corriger les imports** dans les tests:
   ```python
   # Bon
   from tests.utils.test_helpers import assert_gift_properties
   
   # Mauvais (ancien)
   from conftest import assert_gift_basic_properties
   ```

3. **Utiliser les bonnes fixtures**:
   ```python
   # Tests unitaires
   async def test_example(unit_db_session, mock_trace_service):
   
   # Tests d'intégration  
   async def test_example(integration_db_session, test_client_with_auth):
   ```

### Erreurs de session SQLAlchemy

**Cause**: Objets attachés à différentes sessions

**Solution temporaire**: Utiliser les tests simples qui fonctionnent:
- ✅ `test_gift_service_simple.py` (2 tests validés)
- ✅ `test_group_route.py` (1 test d'intégration)
- ✅ `test_refresh_token.py` (1 test de service)

### Fixtures introuvables

**Erreur**: `fixture 'xyz' not found`

**Solutions**:
1. Vérifier les imports dans les fixtures
2. S'assurer que les `__init__.py` existent
3. Utiliser les fixtures correctes selon le type de test

## ✅ Tests Qui Fonctionnent Actuellement

```bash
# ✅ Ces tests passent avec la nouvelle structure:
python run_tests.py unit/services/test_gift_service_simple.py    # 2 tests
python run_tests.py integration/test_group_route.py               # 1 test  
python run_tests.py unit/services/test_refresh_token.py           # 1 test
```

## 🛠️ Outils de Diagnostic

```bash
# Vérifier la collecte des tests
python -m pytest --collect-only backend/tests/

# Lister les fixtures disponibles  
python -m pytest --fixtures backend/tests/

# Mode verbeux pour debugging
python -m pytest backend/tests/ -v -s --tb=long

# Tests par marqueurs
python -m pytest backend/tests/ -m unit -v
python -m pytest backend/tests/ -m integration -v
```

## 📞 Support

Si les problèmes persistent:

1. **Vérifier l'environnement**:
   ```bash
   cd backend
   .venv/Scripts/activate  # Windows
   pip list | grep pytest
   ```

2. **Nettoyer le cache**:
   ```bash
   cd backend  
   rm -rf .pytest_cache __pycache__ tests/__pycache__
   ```

3. **Mode de compatibilité**: Revenir temporairement aux tests dans `tests/` à la racine si nécessaire.