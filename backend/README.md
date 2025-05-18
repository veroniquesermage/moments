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

