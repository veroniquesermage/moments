# 🎁 Liste2Wish - Backend

Backend Python de l'application Liste2Wish, permettant aux membres d'une famille de partager leurs idées de cadeaux de Noël.  
Cette version est une migration depuis Spring Boot vers FastAPI, avec authentification Google et JWT.

---

## 🚀 Lancement local

### ⚙️ Prérequis

- Python 3.11+
- PostgreSQL ou SQLite (en local pour le dev)
- [Poetry](https://python-poetry.org/) ou `pip` classique

### 📦 Installation

```bash
git clone https://github.com/ton-utilisateur/liste2wish-back.git
cd liste2wish-back
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

Swagger : http://127.0.0.1:8000/docs
Localhost: http://127.0.0.1:8000/

### 🛢️ Mise à jour base de données (Alembic)

On génère d'abord la version avec un message d'upgrade:
```bash
alembic revision --autogenerate -m "Ajout du code dans Group et création de UserGroup"
```
On vérifie que els tables sont bien créées dans le fichier de version et on crée la base :
```bash
alembic upgrade head
```

## 🔄 Convention des routes API

### Méthodes HTTP

| Action                              | Méthode | Exemple de route                          | Payload attendu                   | Effet |
|-------------------------------------|---------|-------------------------------------------|------------------------------------|-------|
| Lire une ressource ou une collection | `GET`   | `/gift-ideas`, `/gifts/:id`               | —                                  | Renvoie les données demandées |
| Créer une nouvelle ressource         | `POST`  | `/gift-ideas`, `/gifts`                   | Données de la ressource à créer   | Crée un élément |
| Modifier partiellement une ressource| `PATCH` | `/gift-ideas/:id`, `/gifts/:id`           | Champs à modifier                 | Met à jour partiellement |
| Supprimer une ressource             | `DELETE`| `/gift-ideas/:id`, `/gifts/:id`           | —                                  | Supprime l’élément |
| Déclencher une action spécifique sur une ressource | `POST`  | `/gift-ideas/:id/actions/convert`         | (optionnel)                        | Action métier ciblée, générique |

---
| Code             | Quand l’utiliser                                        | Détail                                                                              |
| ---------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `204 No Content` | Action réussie, rien à renvoyer                         | Ex: modification, mise à jour, suppression                                          |
| `202 Accepted`   | Action **asynchrone**, déclenchée mais **pas terminée** | Ex: tu démarres un traitement qui prendra du temps                                  |
| `200 OK`         | OK même sans contenu, mais…                             | C’est toléré, mais on attend souvent un body. À éviter si tu renvoies rien.         |
| `201 Created`    | Tu crées une ressource                                  | Mais tu dois renvoyer au **minimum un `Location` header** ou l’ID nouvellement créé |

---

### 🔧 Convention pour les **actions spécifiques**

Plutôt que de faire `/gift-ideas/convert-to-gift` ou `/gift-ideas/take`,  
on utilise une route **générique d’action** par ressource :
```http
POST /<ressource>/:id/actions/<action_name>
```

#### 🔹 Exemples pour Liste2Wish :

| Cas métier                                             | Route                                      | Payload          |
|--------------------------------------------------------|---------------------------------------------|------------------|
| Transformer une idée en cadeau pris                   | `POST /gift-ideas/:id/actions/convert`      | `{ statut: 'PRIS' }` |
| Dupliquer une idée pour un autre membre               | `POST /gift-ideas/:id/actions/duplicate`    | `{ destinataireId: 123 }` |
| Partager une idée avec le groupe                      | `POST /gift-ideas/:id/actions/set-shared`   | — |
| Annuler la réservation d’un cadeau                    | `POST /gifts/:id/actions/unreserve`         | — |
| Confirmer un cadeau comme reçu                        | `POST /gifts/:id/actions/mark-received`     | — |

> ✅ Toutes les actions sont regroupées dans `/actions/<nom>`
> ✅ Le nom de l’action est explicite, mais pas “verbe” dans l’URL root
> ✅ Les routes REST principales restent intactes (`GET`, `PATCH`, etc.)

---

### 🧠 Bonus : règles maison

- ✅ **Pas de verbes** dans les noms de routes racines (`/get`, `/delete`, `/convert-to-gift`)  
- ✅ **POST** utilisé pour les **actions déclenchables**  
- ✅ **PATCH** utilisé pour modifier un ou plusieurs champs **sans effet de bord**  
- ✅ **GET** pour récupérer  
- ✅ **DELETE** pour supprimer une ressource  
- ❌ Jamais de logique métier dans `/gift-ideas/convert-to-gift` → ça devient `/gift-ideas/:id/actions/convert`

---

### 📦 Exemple d’extension future

Demain tu veux permettre de :
- **Archiver une idée**  
→ `POST /gift-ideas/:id/actions/archive`

- **Taguer une idée comme "urgence"**  
→ `PATCH /gift-ideas/:id` avec `{ urgent: true }`

- **Notifier un utilisateur d’une prise**  
→ `POST /gifts/:id/actions/notify`

---
