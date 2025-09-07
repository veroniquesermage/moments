# Optimisations Backend - Moments API

## 📊 Vue d'ensemble
Ce document détaille les optimisations et améliorations recommandées pour le backend de l'application Moments après analyse complète du code.

## 🚀 Optimisations de Performance

### 1. Base de Données

#### Pagination
**Problème** : Aucune pagination sur les endpoints retournant des listes
**Impact** : Performance dégradée avec de gros volumes de données
**Solution** :
```python
# Ajouter à gift_service.py
async def get_my_gifts(db: AsyncSession, effective_user_id: int, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    result = await db.execute(
        select(Gift)
        .where(and_(Gift.destinataire_id == effective_user_id, Gift.gift_idea_id.is_(None)))
        .order_by(Gift.priorite)
        .offset(offset)
        .limit(limit)
        .options(selectinload(Gift.destinataire), selectinload(Gift.reserve_par))
    )
```

#### Index Composites
**Localisation** : `models/gift.py`
**Amélioration** :
```python
__table_args__ = (
    Index("ix_gift_utilisateur", "destinataire_id"),
    Index("ix_gift_reserve_par", "reserve_par_id"), 
    Index("ix_gift_statut", "statut"),
    # NOUVEAUX INDEX COMPOSITES
    Index("ix_gift_user_status_priority", "destinataire_id", "statut", "priorite"),
    Index("ix_gift_status_expiration", "statut", "expiration_reservation"),
)
```

#### Optimisation des Requêtes N+1
**Localisation** : `gift_service.py:203-220`
**Problème actuel** :
```python
# Ligne 203-207 - Requête en deux temps
gifts_list = (await db.execute(
    select(Gift).where(Gift.id.in_(ids))
    .options(selectinload(Gift.reserve_par))
    .options(selectinload(Gift.destinataire))
)).scalars().all()
```

**Solution optimisée** :
```python
# Utiliser une seule requête avec jointures
gifts_list = (await db.execute(
    select(Gift)
    .join(User, Gift.destinataire_id == User.id)
    .outerjoin(User.alias("reserver"), Gift.reserve_par_id == User.alias("reserver").id)
    .where(Gift.id.in_(ids), Gift.destinataire_id == current_user.id)
    .options(contains_eager(Gift.destinataire), contains_eager(Gift.reserve_par))
)).scalars().all()
```

### 2. Mise en Cache

#### Cache Redis
**Implémentation recommandée** :
```python
# Nouveau fichier: app/core/cache.py
import redis.asyncio as redis
from functools import wraps

redis_client = redis.from_url("redis://localhost:6379")

def cache_result(expire_time: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

#### Utilisation dans les services :
```python
# Dans group_service.py
@cache_result(expire_time=600)  # 10 minutes
async def get_groups(db: AsyncSession, current_user: User) -> list[GroupResponse]:
    # Code existant...
```

### 3. Optimisation des Requêtes Complexes

#### Vue Matérialisée pour les Statistiques
**Création d'une migration Alembic** :
```sql
CREATE MATERIALIZED VIEW gift_stats AS
SELECT 
    destinataire_id,
    COUNT(*) as total_gifts,
    COUNT(CASE WHEN statut = 'RESERVE' THEN 1 END) as reserved_gifts,
    COUNT(CASE WHEN statut = 'PRIS' THEN 1 END) as taken_gifts
FROM cadeaux 
GROUP BY destinataire_id;

CREATE INDEX ON gift_stats (destinataire_id);
```

## 🛡️ Améliorations de Sécurité

### 1. Rate Limiting
**Implémentation** :
```python
# app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Dans main.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Utilisation dans les routes
@router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
```

### 2. Validation Renforcée
**Amélioration des schémas Pydantic** :
```python
# schemas/gift/gift_create.py
from pydantic import validator, Field
import bleach

class GiftCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('nom', 'description')
    def sanitize_html(cls, v):
        if v:
            return bleach.clean(v, tags=[], strip=True)
        return v
    
    @validator('prix')
    def validate_price(cls, v):
        if v and v < 0:
            raise ValueError('Le prix ne peut pas être négatif')
        return v
```

### 3. Audit Trail Amélioré
**Localisation** : Améliorer `trace_service.py`
```python
class TraceService:
    @staticmethod
    async def record_security_event(
        db: AsyncSession,
        user_identifier: str,
        event_type: str,
        ip_address: str,
        user_agent: str,
        details: dict
    ):
        # Enregistrer les événements de sécurité spécifiques
        trace = Trace(
            utilisateur=user_identifier,
            action=f"SECURITY_{event_type}",
            details={
                **details,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        db.add(trace)
        await db.commit()
```

## 🔧 Améliorations du Code

### 1. Gestion des Erreurs Centralisée
**Nouveau fichier** : `app/core/exceptions.py`
```python
class BusinessLogicError(HTTPException):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=message)

class GiftNotFoundError(BusinessLogicError):
    def __init__(self):
        super().__init__("Cadeau introuvable", 404)

class UnauthorizedGiftAccess(BusinessLogicError):
    def __init__(self):
        super().__init__("Accès non autorisé à ce cadeau", 403)
```

### 2. Constants et Messages
**Nouveau fichier** : `app/core/constants.py`
```python
class ErrorMessages:
    GIFT_NOT_FOUND = "Cadeau introuvable"
    UNAUTHORIZED_ACCESS = "Accès non autorisé"
    GIFT_ALREADY_RESERVED = "Ce cadeau est déjà réservé"
    INVALID_GIFT_STATUS = "Statut de cadeau invalide"

class CacheKeys:
    USER_GROUPS = "user_groups:{user_id}"
    GIFT_DETAILS = "gift_details:{gift_id}:{group_id}"
    GROUP_MEMBERS = "group_members:{group_id}"
```

### 3. Fix du Bug Potentiel
**Localisation** : `gift_service.py:165`
**Problème** : Accès à `gift_idea.proposee_par` sans vérifier si `gift_idea` existe
**Solution** :
```python
# Ligne 165 - Version corrigée
if updates.destinataire_id != current_user.id and (
    not existing.gift_idea or 
    existing.gift_idea.proposee_par_id != current_user.id
):
    raise HTTPException(
        status_code=400,
        detail="❌ Vous ne pouvez modifier que vos propres cadeaux ou idées."
    )
```

### 4. Amélioration des Type Hints
**Localisation** : `models/__init__.py:5`
**Problème** : Duplication de l'import `GiftPurchaseInfo`
**Solution** :
```python
# Supprimer la ligne 5 dupliquée
from .gift_purchase_info import GiftPurchaseInfo  # Garder une seule fois
```

## 📊 Monitoring et Observabilité

### 1. Métriques Personnalisées
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Métriques business
gift_operations = Counter('gift_operations_total', 'Total gift operations', ['operation', 'status'])
gift_processing_time = Histogram('gift_processing_seconds', 'Time spent processing gifts')
active_reservations = Gauge('active_reservations_total', 'Number of active reservations')

# Utilisation dans gift_service.py
@gift_processing_time.time()
async def create_gift(db: AsyncSession, current_user: User, gift_created: GiftCreate):
    try:
        # Code existant...
        gift_operations.labels(operation='create', status='success').inc()
        return result
    except Exception as e:
        gift_operations.labels(operation='create', status='error').inc()
        raise
```

### 2. Health Checks Améliorés
```python
# app/routes/health.py
@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    checks = {
        "database": await check_database_health(db),
        "redis": await check_redis_health(),
        "external_apis": await check_external_apis()
    }
    
    status = "healthy" if all(checks.values()) else "unhealthy"
    return {"status": status, "checks": checks}
```

## 🚀 Déploiement et Infrastructure

### 1. Configuration de Production
**Ajout au** `docker-compose.yml` :
```yaml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    
  app:
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      
volumes:
  redis_data:
```

### 2. Scripts de Maintenance
**Nouveau fichier** : `scripts/optimize_db.py`
```python
#!/usr/bin/env python3
"""Script de maintenance pour optimiser la base de données"""

async def cleanup_expired_reservations():
    """Nettoie les réservations expirées"""
    # Code de nettoyage automatique
    
async def refresh_materialized_views():
    """Rafraîchit les vues matérialisées"""
    # Code de rafraîchissement

async def analyze_performance():
    """Analyse les performances et génère un rapport"""
    # Code d'analyse
```

## 📈 Métriques de Succès

- **Performance** : Réduction du temps de réponse de 30%
- **Scalabilité** : Support de 10x plus d'utilisateurs simultanés
- **Fiabilité** : 99.9% d'uptime
- **Sécurité** : Zéro incident de sécurité

## 🎯 Priorités d'Implémentation

### Phase 1 (Critique) - 1-2 semaines
1. Fix du bug ligne 165 dans `gift_service.py`
2. Ajout de la pagination
3. Rate limiting de base

### Phase 2 (Important) - 2-4 semaines  
1. Implémentation du cache Redis
2. Index composites en base
3. Validation renforcée

### Phase 3 (Optimisation) - 1-2 mois
1. Vues matérialisées
2. Métriques personnalisées
3. Scripts de maintenance

---

*Document généré le : {{ date.today() }}*
*Dernière mise à jour : À maintenir lors des évolutions*