# Commandes utiles pour déployer sur VPS


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

### faire un backup:
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

### penser à remettre d'querre l'environnement du front:
```bash
cd frontend/src/environments
rm environment.ts
mv environment.prod.ts environment.ts
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