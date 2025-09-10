# Analyse de Performance - Endpoint `/api/auth/google`

## 🚨 Problème Identifié

**Alerte Prometheus** : Endpoint `/api/auth/google` avec **p95 > 300ms** (seuil d'alerte)

**Trace Jaeger** : Temps de réponse total de **430.25ms**

## 📊 Décomposition de la Trace Jaeger

### Breakdown des opérations tracées :
- **Opérations base de données** : ~27ms (6%) ✅
  - `SELECT moments`: 19.68ms + 1.11ms
  - `DELETE moments`: 4.64ms  
  - `INSERT moments`: 1.52ms
  - Connexions DB: 170μs total

- **Appels HTTP tracés** : ~85ms (20%) ⚠️
  - 3 appels `POST /api/auth/google http send`: 39ms + 26ms + 20ms

- **🎯 PROBLÈME CRITIQUE : Opération non-tracée** : **322.69ms (75%)**
  - Représente la majorité du temps d'exécution
  - Correspond aux appels Google OAuth non-instrumentés

## 🔍 Analyse du Code d'Authentification

### Flow d'authentification Google :

1. **`POST /api/auth/google`** (`auth_route.py:18`)
2. **`AuthService.authenticate_google_user`** (`auth_service.py:34`)
3. **Appels Google non-tracés** :
   - `exchange_code_for_tokens()` → Google Token API (~150-200ms)
   - `verify_google_id_token()` → Google JWK fetch + JWT decode (~100-150ms)
4. **Opérations DB** : `get_or_create_user` + `store_refresh_token`

### Code critique identifié :

```python
# app/services/auth/google_auth_service.py:22
async with httpx.AsyncClient() as client:
    response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)

# app/core/google_jwt.py:12
async with httpx.AsyncClient() as client:
    jwks = (await client.get(GOOGLE_JWK_URL)).json()
```

**Problèmes identifiés** :
- ❌ Pas de traçage OpenTelemetry
- ❌ Création/destruction de client HTTP à chaque requête
- ❌ Fetch des JWK Google à chaque validation
- ❌ Pas de timeout configuré
- ❌ Opérations séquentielles non-optimisées

## 🚀 Solutions d'Optimisation Recommandées

### 1. **Ajout de Traces OpenTelemetry** (Priorité: Haute)

**Objectif** : Visibilité complète sur les 322ms manquants

```python
# app/core/google_jwt.py
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def verify_google_id_token(id_token: str) -> dict:
    with tracer.start_as_current_span("google_jwt_verification") as span:
        span.set_attribute("jwt.token_length", len(id_token))
        
        with tracer.start_as_current_span("google_jwks_fetch"):
            async with httpx.AsyncClient() as client:
                jwks = (await client.get(GOOGLE_JWK_URL)).json()
        
        with tracer.start_as_current_span("jwt_decode"):
            payload = jwt.decode(...)
            
        return payload

# app/services/auth/google_auth_service.py  
async def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    with tracer.start_as_current_span("google_token_exchange") as span:
        span.set_attribute("oauth.code_length", len(code))
        
        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
        
        return response.json()
```

### 2. **Client HTTP Persistant** (Priorité: Haute)

**Objectif** : Réutilisation des connexions TCP, timeouts optimisés

```python
# app/core/http_clients.py (nouveau fichier)
import httpx

# Client global réutilisable pour Google APIs
google_client = httpx.AsyncClient(
    timeout=httpx.Timeout(connect=2.0, read=3.0, pool=5.0),
    limits=httpx.Limits(
        max_connections=10, 
        max_keepalive_connections=5,
        keepalive_expiry=30
    ),
    headers={"User-Agent": "Moments-API/1.0"}
)

# Cleanup au shutdown de l'app
async def close_http_clients():
    await google_client.aclose()
```

**Modification des services** :
```python
# app/core/google_jwt.py
from app.core.http_clients import google_client

async def verify_google_id_token(id_token: str) -> dict:
    jwks = (await google_client.get(GOOGLE_JWK_URL)).json()
    # ...

# app/services/auth/google_auth_service.py
from app.core.http_clients import google_client

async def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    response = await google_client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
    # ...
```

### 3. **Cache JWK en Mémoire** (Priorité: Moyenne)

**Objectif** : Éviter le fetch des clés Google à chaque validation (TTL sécurisé: 5min)

```python
# app/core/google_jwt.py
import time
from typing import Optional, Tuple

_jwks_cache: Optional[Tuple[dict, float]] = None
CACHE_TTL = 300  # 5 minutes = fenêtre de sécurité acceptable

async def get_cached_jwks() -> dict:
    global _jwks_cache
    
    now = time.time()
    if _jwks_cache is None or (now - _jwks_cache[1]) > CACHE_TTL:
        with tracer.start_as_current_span("google_jwks_fetch") as span:
            jwks = (await google_client.get(GOOGLE_JWK_URL)).json()
            _jwks_cache = (jwks, now)
            span.set_attribute("jwks.cache_miss", True)
    else:
        span.set_attribute("jwks.cache_hit", True)
    
    return _jwks_cache[0]

async def verify_google_id_token(id_token: str) -> dict:
    with tracer.start_as_current_span("google_jwt_verification"):
        jwks = await get_cached_jwks()
        # ... reste du code JWT decode
```

### 4. **Configuration du Shutdown** (Priorité: Faible)

```python
# app/main.py
from app.core.http_clients import close_http_clients

@app.on_event("shutdown")
async def shutdown_event():
    await close_http_clients()
```

## 📈 Impact Attendu des Optimisations

| Solution | Gain Performance | Risque | Complexité | Priorité |
|----------|------------------|--------|------------|----------|
| **Traces OpenTelemetry** | Visibilité debug | Aucun | Faible | **Haute** |
| **Client HTTP persistant** | -30-60ms (15-20%) | Aucun | Faible | **Haute** |
| **Cache JWK 5min** | -50-100ms sur 50% des requêtes | Faible | Faible | **Moyenne** |
| **Timeouts optimisés** | Évite requêtes > 5s | Aucun | Faible | **Haute** |

### Résultat attendu :
- **Avant** : 430ms p95
- **Après** : **250-300ms p95** 
- **Amélioration** : **-30 à -40%** de réduction

## 🛠️ Plan d'Implémentation

### Phase 1 - Diagnostic (Urgent)
1. ✅ Ajouter traces OpenTelemetry sur `verify_google_id_token`
2. ✅ Ajouter traces OpenTelemetry sur `exchange_code_for_tokens`
3. ✅ Déployer et analyser nouvelle trace Jaeger

### Phase 2 - Optimisation (Haute priorité)  
1. ✅ Implémenter client HTTP persistant
2. ✅ Configurer timeouts optimisés
3. ✅ Tester en environnement de développement

### Phase 3 - Cache (Optionnel)
1. ⏳ Implémenter cache JWK 5 minutes
2. ⏳ Monitorer hit/miss ratio
3. ⏳ Ajuster TTL selon besoins

## 🔧 Validation Post-Optimisation

### Métriques à surveiller :
- **Latence p95** : Objectif < 250ms
- **Traces Jaeger** : Visibilité complète des 430ms
- **Taux d'erreur** : Maintenir < 1%
- **Cache hit ratio** : > 70% (si implémenté)

### Tests à effectuer :
```bash
# Load testing
artillery quick --count 50 --num 10 https://moments-ep.com/api/auth/google

# Monitoring Prometheus
# Vérifier diminution du p95 sur le dashboard
```

---
**Analyse réalisée le** : 2025-09-08  
**Endpoint concerné** : `POST /api/auth/google`  
**Trace ID** : Jaeger trace 430.25ms  
**Objectif** : Réduire p95 sous le seuil d'alerte (300ms)