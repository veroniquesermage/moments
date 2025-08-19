# 🧭 Monitoring – Moments (État au 20/08/2025)

Ce document explique **ce qui est en place** et **pourquoi** pour le monitoring de Moments, suite au déploiement sur VPS et à la mise en place d’un VPN avec la VM Freebox.

---

## ✅ Objectifs & raisons des choix

- **Métriques HTTP** de l’API (FastAPI) exposées en `/metrics` pour Prometheus.
- **Traces distribuées** via OpenTelemetry → **Jaeger** (OTLP HTTP).
- **Stats SQL** via **PgBouncer exporter**.
- **Alerte** via Alertmanager.
- **VPN WireGuard** entre **VPS (Moments)** et **VM (Monitoring)** afin d’éviter les problèmes de NAT/ports ouverts sur Internet et d’avoir un réseau privé stable entre les deux machines.

---

## 🗺️ Topologie (finale)

```
                Internet
                    │
          (IP publique VPS: 193.181.210.186)
                    │
           ┌──────────────────────┐
           │        VPS           │
           │ Moments (backend+fe) │
           │  - FastAPI /metrics  │
           │  - OTEL → Jaeger     │
           └─────────┬────────────┘
                     │  WireGuard (UDP 51820)
             10.66.66.1/30  ▲
                             │
                             ▼  10.66.66.2/30
           ┌──────────────────────┐
           │         VM           │
           │  Monitoring stack    │
           │  - Prometheus:9090   │
           │  - Jaeger:16686/4318 │
           │  - Alertmanager:9093 │
           └──────────────────────┘
```

- **IP privée VPN (VPS)** : `10.66.66.1`
- **IP privée VPN (VM)** : `10.66.66.2`

> Prometheus scrappe maintenant **via le VPN** (`10.66.66.1`) et l’API envoie ses **traces** vers Jaeger sur `10.66.66.2:4318`.

---

## 🧩 Composants

| Composant              | Rôle | Où | Notes clés |
|---|---|---|---|
| **FastAPI (Moments)** | Expose `/metrics` + instrumentation HTTP | VPS | Un **seul** endpoint de métriques via `prometheus_fastapi_instrumentator`. |
| **Prometheus** | Scrape métriques API + PgBouncer | VM | Volume de données avec UID **65534**, port **9090**, `--web.enable-lifecycle`. |
| **Jaeger All‑in‑One** | Traces OTLP HTTP (4318) | VM | UI `16686`, ports `4317/4318` exposés. |
| **Alertmanager** | Alerting | VM | SMTP déjà configuré. |
| **PgBouncer exporter** | Exporte stats PgBouncer | VPS (stack Moments) | DSN correcte via **`command:`**, MDP **URL‑encodé**. |

---

## ⚙️ Configuration — côté VPS (Moments)

### 1) FastAPI – métriques & OTel (extrait logique)
- **Métriques** : `Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)`
- **OTel export (HTTP)** déclaré **uniquement si** `OTEL_ENDPOINT` est défini :
   - `OTEL_ENDPOINT=http://10.66.66.2:4318/v1/traces`

> Important : **ne pas** doubler l’endpoint de métriques (éviter un `app.mount("/metrics", ...)` simultané).

### 2) Docker Compose (backend) – variable d’env
```yaml
services:
  backend:
    # …
    environment:
      - OTEL_ENDPOINT=http://10.66.66.2:4318/v1/traces
```

---

## ⚙️ Configuration — côté VM (Monitoring)

### 1) Prometheus (compose)

- **Volume de données** avec droits UID 65534 (user `nobody` dans l’image Prom) :
   - Dossier hôte : `./prom-data` → `chown -R 65534:65534 ./prom-data`
- **Un seul montage** pour la conf (éviter le conflit “not a directory”) :
```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    user: "65534:65534"
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
      - --web.enable-lifecycle
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus:ro
      - ./prom-data:/prometheus
```

### 2) Fichier `prometheus/prometheus.yml` (scrape via VPN)
```yaml
global:
  scrape_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "/etc/prometheus/alerting-rules.yml"
  - "/etc/prometheus/recording-rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'moments_api'
    metrics_path: /metrics
    static_configs:
      - targets: ['10.66.66.1:8000']   # API via VPN

  - job_name: 'pgbouncer_exporter'
    static_configs:
      - targets: ['10.66.66.1:9127']   # Exporter via VPN
```

### 3) Jaeger (compose)
```yaml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    restart: unless-stopped
    ports:
      - "16686:16686"   # UI
      - "4317:4317"     # OTLP gRPC
      - "4318:4318"     # OTLP HTTP
```

### 4) Alertmanager (compose + conf SMTP)
Port publié `9093`, fichier de conf existant (inchangé).

---

## ⚙️ Configuration — PgBouncer exporter (dans la stack Moments sur le VPS)

**Problème rencontré** : l’exporter pointait par défaut sur `[::1]:6543` (localhost/IPv6, mauvais port) car la “variable” était mal renseignée et le mot de passe contenait des caractères spéciaux non encodés.

**Fix** : utiliser **`command:`** avec DSN complète **URL‑encodée** et le **service pgbouncer** en host.

```yaml
pgbouncer-exporter:
  image: prometheuscommunity/pgbouncer-exporter:latest
  container_name: moments-pgbouncer-exporter
  restart: unless-stopped
  depends_on: [pgbouncer]
  ports:
    - "9127:9127"
  command:
    - '--pgBouncer.connectionString=postgres://statsMom3nts:D%3FR6%40nzro9kNDqdY@pgbouncer:6432/pgbouncer?sslmode=disable'
```

> **PgBouncer** : veiller à déclarer l’utilisateur de stats/admin (ex. `statsMom3nts`) dans `admin_users`/`stats_users` et dans `userlist.txt` selon `auth_type`.

---

## 🔐 WireGuard — mise en place **détaillée** (VPS ⇄ VM)

> Objectif : créer un **tunnel privé stable** entre le **VPS** (Moments) et la **VM Freebox** (Monitoring) pour :
> - envoyer les **traces OTLP** vers Jaeger **sans** exposer de port public,
> - scrapper l’API par Prometheus **via IP privée**,
> - éviter les soucis de NAT/CGNAT.

### 🧱 Paramètres retenus
- **VPS (public)** : IP pub `193.181.210.186` — **VPN** `10.66.66.1/30` (écoute UDP **51820**)
- **VM (chez Freebox)** : **VPN** `10.66.66.2/30` — `PersistentKeepalive=25`
- **AllowedIPs (des deux côtés)** : `10.66.66.0/30` (facile à lire et robuste)
- Services cibles via VPN :
   - **OTEL HTTP** : `10.66.66.2:4318` (Jaeger All-in-One)
   - **Prometheus scrapes** : `10.66.66.1:8000` (API) et `10.66.66.1:9127` (PgBouncer exporter)

### 1) Installation & clés (deux machines)
```bash
sudo apt update && sudo apt install -y wireguard
sudo install -d -m 700 /etc/wireguard

# Génère clé privée/publique (EN ROOT, sinon la redirection '>' échoue)
sudo bash -c 'umask 077; wg genkey | tee /etc/wireguard/wg0.key | wg pubkey > /etc/wireguard/wg0.pub'

# Vérif
sudo ls -l /etc/wireguard
# -rw------- root root wg0.key
# -rw-r--r-- root root wg0.pub
```

### 2) Config fichiers `wg0.conf` (copier/coller)

**VPS – `/etc/wireguard/wg0.conf`**
```ini
[Interface]
Address = 10.66.66.1/30
ListenPort = 51820
PrivateKey = <clé_privée_VPS>
SaveConfig = true

[Peer]
PublicKey = <clé_publique_VM>
AllowedIPs = 10.66.66.0/30
```

**VM – `/etc/wireguard/wg0.conf`**
```ini
[Interface]
Address = 10.66.66.2/30
PrivateKey = <clé_privée_VM>

[Peer]
PublicKey = <clé_publique_VPS>
Endpoint = 193.181.210.186:51820
AllowedIPs = 10.66.66.0/30
PersistentKeepalive = 25
```

> Sécurité : `sudo chmod 600 /etc/wireguard/wg0.conf /etc/wireguard/wg0.key`

### 3) Firewall & démarrage
```bash
# VPS : ouvrir l’UDP 51820 si UFW actif
sudo ufw allow 51820/udp
sudo ufw reload || true

# Démarrer sur les deux hôtes
sudo systemctl enable --now wg-quick@wg0
```

### 4) Vérifications (ordre conseillé)
```bash
# VPS : écoute du port
sudo ss -lun | grep 51820     # doit montrer 0.0.0.0:51820

# Les deux : état du tunnel
sudo wg show                  # chercher "peer:" + "latest handshake"

# Routage
ip route get 10.66.66.1 | cat # depuis VM → doit dire "dev wg0"
ip route get 10.66.66.2 | cat # depuis VPS → "dev wg0"

# Connectivité
ping -c2 10.66.66.1           # VM -> VPS
ping -c2 10.66.66.2           # VPS -> VM
```

### 5) Intégrations réseau (consommateurs)
- **Backend Moments (VPS)** : exporter OTel en privé
  ```yaml
  # docker-compose (service backend)
  environment:
    - OTEL_ENDPOINT=http://10.66.66.2:4318/v1/traces
  ```
- **Prometheus (VM)** : scrapes en privé
  ```yaml
  scrape_configs:
    - job_name: 'moments_api'
      static_configs:
        - targets: ['10.66.66.1:8000']

    - job_name: 'pgbouncer_exporter'
      static_configs:
        - targets: ['10.66.66.1:9127']
  ```

### 6) Dépannage rapide
- **`ping: Required key not available`** → pas de peer ou clés mal croisées. Re-lire `wg0.conf` des deux côtés, vérifier les **PublicKey** et **AllowedIPs** (`10.66.66.0/30`).
- **Pas de handshake** :
   - VM → vérifier `Endpoint=193.181.210.186:51820`, `PersistentKeepalive=25`.
   - VPS → `sudo ss -lun | grep 51820`, puis `sudo tcpdump -ni any udp port 51820` pendant un ping depuis la VM.
- **Trafic applicatif bloqué** : UFW côté VM (exposer `4318/tcp` sur **wg0** si filtrage strict) :
  ```bash
  sudo ufw allow in on wg0 to any port 4318 proto tcp
  ```

### 7) Pourquoi WireGuard (et pas juste des ports publics) ?
- Pas de dépendance aux forwards Freebox/NAT : ça marche partout.
- Moins d’exposition réseau (ports fermés côté Internet pour Jaeger & co).
- Performant et simple (un seul fichier `wg0.conf` par hôte, clé publique/privée).

## 🔎 URLs utiles

- **Prometheus** : `http://192.168.1.43:9090`
- **Jaeger UI** : `http://192.168.1.43:16686`
- **Alertmanager** : `http://192.168.1.43:9093`
- **API (debug)** : `http://193.181.210.186:8000/metrics` (public) — **préférer le VPN**

---

## 🧯 Runbook “panne rapide”

- **/metrics en 404** → vérifier code (un seul endpoint), puis **rebuild ciblé** du backend :  
  `docker compose -f docker-compose.prod.yml -f docker-compose.monitoring.yml --env-file .env.monitoring build --no-cache --pull backend && docker compose -f docker-compose.prod.yml -f docker-compose.monitoring.yml --env-file .env.monitoring up -d --force-recreate --no-deps backend`

- **Prometheus restart loop / permission denied** → corriger droits du volume `/prometheus` sur la VM :  
  `chown -R 65534:65534 ./prom-data`

- **VPN KO** → `ss -lun | grep 51820` (VPS), `wg show` (peers/handshake), `AllowedIPs=10.66.66.0/30`, pings `10.66.66.1/2`.

- **Traces absentes** → tester réseau depuis le conteneur backend vers `http://10.66.66.2:4318/` (404 au root = OK réseau), puis regarder les logs exporter OTLP.

- **PgBouncer exporter DOWN** → vérifier DSN en `command:` (host `pgbouncer`, port `6432`, mot de passe **URL‑encodé**), et droits stats dans PgBouncer.
- **Ouverture des ports**
   - Vérifier sur le VPS que les ports 8000 et 9127 sont ouverts :
      - `sudo ufw status verbose` → ports 8000 (API Moments) et 9127 (PgBouncer exporter) doivent être **ALLOW**.
   - Si pas ouvert, ajouter avec :
     ```bash
     sudo ufw allow 8000/tcp
     sudo ufw allow 9127/tcp
     ```

- **Pas de mails reçus**
   - `docker logs -f alertmanager` → erreurs SMTP ?
   - Vérifie `smtp_auth_password` (mot de passe d’app Gmail).
   - Vérifie que l’alerte est bien `firing` dans Prometheus (onglet **Alerts**).

- **Prometheus n’a plus de métriques**
   - <http://IP_VM:9090/targets> → check si `moments_api` et `pgbouncer` sont UP.
   - Si DOWN → réseau, firewall, mauvais port ?

- **Jaeger vide**
   - Vérifie que l’API envoie bien vers `http://IP_VM:4318/v1/traces`.
   - Test rapide : `curl -v http://IP_VM:4318/v1/traces` doit répondre `405 Method Not Allowed`.

- **Trop d’alertes “bruit”**
   - Aller sur <http://IP_VM:9093/#/silences> → créer un silence temporaire.

---

## ✍️ Historique des incidents & fixes (résumé)

- **404 `/metrics`** après déploiement : image backend non rebuildée + double exposition → **rebuild strict** et **un seul** endpoint.
- **Prometheus “permission denied”** sur `/prometheus/queries.active` : volume sans droits → **chown 65534** et montage propre (un seul dossier).
- **Jaeger injoignable** depuis VPS : NAT Freebox → **WireGuard** (`10.66.66.1/2`) + OTEL HTTP vers `10.66.66.2:4318`.
- **PgBouncer exporter DOWN** : DSN invalide/variable mal passée + MDP non encodé → **`command:`** + **URL‑encoding** ; `pgbouncer_up = 1` confirmé.

---

> Documents d’origine de la stack (avant corrections) : MONITORING.md initial dans le repo.


## 🛠️ Que vérifier en cas de pépin (Pense-bête)

1. **Ouverture des ports**
   - Vérifier sur le VPS que les ports 8000 et 9127 sont ouverts :
      - `sudo ufw status verbose` → ports 8000 (API Moments) et 9127 (PgBouncer exporter) doivent être **ALLOW**.
   - Si pas ouvert, ajouter avec :
     ```bash
     sudo ufw allow 8000/tcp
     sudo ufw allow 9127/tcp
     ```

2. **Pas de mails reçus**
   - `docker logs -f alertmanager` → erreurs SMTP ?
   - Vérifie `smtp_auth_password` (mot de passe d’app Gmail).
   - Vérifie que l’alerte est bien `firing` dans Prometheus (onglet **Alerts**).

3. **Prometheus n’a plus de métriques**
   - <http://IP_VM:9090/targets> → check si `moments_api` et `pgbouncer` sont UP.
   - Si DOWN → réseau, firewall, mauvais port ?

4. **Jaeger vide**
   - Vérifie que l’API envoie bien vers `http://IP_VM:4318/v1/traces`.
   - Test rapide : `curl -v http://IP_VM:4318/v1/traces` doit répondre `405 Method Not Allowed`.

5. **Trop d’alertes “bruit”**
   - Aller sur <http://IP_VM:9093/#/silences> → créer un silence temporaire.
