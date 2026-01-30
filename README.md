# EzPlantParent

IoT plant monitoring and watering system with ESP32 stations, FastAPI backend, and Angular frontend.

## Quick Start

### Development Environment

1. Create `.env` file at root with `CHAT_GPT_KEY=your_key`
2. Run `./develop.sh` (change permissions if needed)
3. Follow instructions to install, run, or test the system

### Access the System

Once running in background:
- Backend API: https://localhost:3000 (documentation)
- Frontend: http://localhost:4200
- Test Coverage: https://localhost:3000/coverage/

### Production Deployment

See deployment workflow in `.github/workflows/test-ssh.yml`

Production site: https://ezplantparent.com

## MQTT Setup

For MQTT broker configuration and ESP32 device setup, see [MQTT_SETUP.md](./MQTT_SETUP.md)

Quick commands:
- Generate local dev certificates: `./develop.sh` → option 8
- Generate production certificates: `./develop.sh` → option 9


mettre l'adresse ip du pc dans le reaseau local dans
.env: ex MQTT_IP=192.168.2.17

Rendre le port sécurisé accessible:
netsh interface portproxy add v4tov4 listenport=8883 listenaddress=192.168.2.17 connectport=8883 connectaddress=127.0.0.1
Voir la règle
netsh interface portproxy show all   

tester l'accès
openssl s_client -connect 192.168.2.17:8883 -CAfile ssl/rootCA.pem

current station id is hardcoded untill le pairage
781C3CB76C2C

tests de un fichier
 ./test-only.sh tests/usecases/ManageUsers/test_auth_user.py





 Voilà ! Maintenant, après avoir déployé cette modification, la documentation sera accessible à :

https://ezplantparent.com/api/docs - Documentation Swagger
https://ezplantparent.com/api/redoc - Documentation ReDoc
https://ezplantparent.com/api/openapi.json - Schéma OpenAPI
En développement local, ce sera :

https://localhost:3000/docs
https://localhost:3000/redoc

