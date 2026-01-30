# Déploiement Production avec Traefik - Guide rapide

## Architecture

- **Traefik** : Reverse proxy avec gestion automatique SSL (Let's Encrypt)
- **Backend** : FastAPI (port 3000 interne)
- **Frontend** : Angular (port 80 interne)
- **Postgres** : Base de données (interne uniquement)

## Prérequis sur le VPS

### 1. Installer Docker et Docker Compose
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy
```

### 2. Configurer le DNS
Pointer votre domaine vers l'IP du VPS :
```
A    ezplantparent.com          -> <VPS_IP>
A    www.ezplantparent.com      -> <VPS_IP>
A    traefik.ezplantparent.com  -> <VPS_IP> (optionnel, pour dashboard)
```

### 3. Créer le fichier .env.prod
```bash
cd /home/deploy/app
cp .env.prod.example .env.prod
nano .env.prod
```

Remplir les valeurs :
```bash
DB_PASSWORD=VotreMotDePasseSecurise123
JWT_SECRET=UneLongueChaineAleatoireDe32CaracteresMinimum
ACME_EMAIL=admin@ezplantparent.com
```

## Déploiement manuel

```bash
cd /home/deploy/app
docker compose -f docker-compose.traefik.yml --env-file .env.prod up -d --build
```

## Vérifier le déploiement

```bash
# Voir les conteneurs
docker compose -f docker-compose.traefik.yml ps

# Voir les logs Traefik
docker compose -f docker-compose.traefik.yml logs -f traefik

# Voir les certificats SSL
docker compose -f docker-compose.traefik.yml exec traefik cat /letsencrypt/acme.json

# Tester l'API
curl https://ezplantparent.com/health
```

## URLs disponibles

- **Frontend** : https://ezplantparent.com
- **Backend API** : https://ezplantparent.com/api/
- **WebSocket** : wss://ezplantparent.com/ws/
- **Health Check** : https://ezplantparent.com/health
- **Traefik Dashboard** : https://traefik.ezplantparent.com (optionnel)

## Arrêter l'application

```bash
docker compose -f docker-compose.traefik.yml down
```

## Points importants

✅ **SSL automatique** : Traefik obtient et renouvelle automatiquement les certificats Let's Encrypt
✅ **Redirection HTTP → HTTPS** : Automatique
✅ **Base de données** : Pas exposée publiquement
✅ **WebSocket** : Supporté nativement par Traefik
✅ **Certificats persistés** : Stockés dans un volume Docker

## Dépannage

### Les certificats ne sont pas générés
1. Vérifier que les ports 80 et 443 sont ouverts :
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

2. Vérifier que le DNS pointe bien vers le VPS :
   ```bash
   dig ezplantparent.com +short
   ```

3. Voir les logs Traefik :
   ```bash
   docker compose -f docker-compose.traefik.yml logs traefik
   ```

### Erreur "too many certificates"
Let's Encrypt a une limite de 5 certificats par semaine. Si vous testez beaucoup, utilisez le staging :
```yaml
# Dans docker-compose.traefik.yml, ajouter :
- "--certificatesresolvers.letsencrypt.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory"
```
