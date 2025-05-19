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