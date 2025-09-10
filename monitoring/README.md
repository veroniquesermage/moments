# Monitoring Stack - Grafana + Loki + Promtail

Cette configuration permet d'accéder facilement aux logs de production depuis n'importe où via une interface web.

## Déployement

1. **Lancer la stack complète** :
```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. **Accès Grafana** :
- URL : `http://votre-serveur:3000`
- Login : `admin`
- Mot de passe : `moments2024!`

## Utilisation

### Interface Grafana
- **Dashboard "Moments - Application Logs"** : Vue d'ensemble avec métriques et logs récents
- **Explore** : Requêtes LogQL personnalisées pour rechercher dans les logs

### Requêtes LogQL utiles
```logql
# Tous les logs de l'application
{job="moments-backend"}

# Erreurs uniquement
{job="moments-backend", level="ERROR"}

# Logs contenant un terme spécifique
{job="moments-backend"} |= "error"

# Logs d'un utilisateur spécifique
{job="moments-backend"} |= "user_id=123"

# Comptage d'erreurs sur 5 minutes
sum(count_over_time({job="moments-backend", level="ERROR"}[5m]))
```

### Filtres avancés
- **Regex** : `{job="moments-backend"} |~ "user_id=[0-9]+"`
- **Exclusions** : `{job="moments-backend"} != "healthcheck"`
- **Plages de temps** : Sélecteur en haut à droite

## Architecture

- **Loki** (port 3100) : Stockage et indexation des logs
- **Promtail** : Collecte des logs depuis les fichiers et containers
- **Grafana** (port 3000) : Interface de visualisation

## Avantages

✅ **Accès distant** : Interface web accessible depuis n'importe où  
✅ **Recherche avancée** : Filtres, regex, plages de temps  
✅ **Temps réel** : Logs en streaming  
✅ **Historique** : Conservation des logs avec rotation automatique  
✅ **Alertes** : Possibilité d'ajouter des alertes sur erreurs  
✅ **Performance** : Pas d'impact sur l'application  

## Sécurité

⚠️ **Important** : En production, configurez :
- HTTPS avec certificat SSL
- Authentification plus robuste (OAuth, LDAP)
- Restriction d'accès par IP si nécessaire