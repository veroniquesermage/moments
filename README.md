# Commandes utiles pour déployer sur VPS

### Modification avant livraison:
- A la racine :
  - le .env de dev doit être remplacé par celui de prod
  - dans pgbouncer:
    - .ini -> remplacer le user admin et les valeurs de prod d'appel à la bdd (attention ! à remplacer dans les blocs database et pgbouncer)
    - userlist -> mettre le userlist de prod
  - supprimer les fichiers inutiles :
    - .env autre que ceux de prod
    - docker_compose.yml
- Dans le backend :
  - supprimer les fichiers inutiles :
    - les .env autre que ceux de prod
    - les fichiers .iml
    - le repertoire .venv
  - modifier dans cleanup_bdd.py cette ligne avec l'env de prod :
    ```python
        load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env.prod", override=True)
    ```
  - verifier que cleanup.cron est bien en LF (sinon dos2unix cleanup.cron)
- Dans le front :
  - supprimer les fichiers inutiles :
    - node_modules
    - les fichiers .iml
  - renommer frontend/src/environments/environment.prod.ts par environment.ts:

### création d'un tar.gz y compris avec les fichiers cachés:
```bash
tar --exclude=./moments.tar.gz -czf moments.tar.gz .
pour vérifier :
tar -tvf moments.tar.gz
```

### envoi au serveur:
```bash
scp moments.tar.gz admin@193.181.210.186:/home/admin/
```

### se connecter au serveur :
```bash
ssh admin@193.181.210.186
```

### faire un backups:
```bash
mv moments moments_backup_$(date +%s)
```
#### si besoin :
```bash
rm -rf moments
```

### décompresser :
```bash
mkdir moments
tar xzf moments.tar.gz -C moments
```

### relancer docker :
```bash
cd moments
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### lancer les migrations alembic :
```bash
docker exec -it moments-backend bash
alembic upgrade head
```

### Vérifier que toutes les tables sont créées
```bash
docker exec -it moments-postgres psql -U Mom3ntsAdm1n moments
\dt
```

### pour entrer dans le container du back et vérifier qu'il y a bien un cron qui tourne par exemple :
```bash
docker exec -it moments-backend bash
crontab -l
```

### s'assurer que le fichier cron est bien en LF :
```bash
dos2unix cleanup.cron
```