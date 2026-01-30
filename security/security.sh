#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
SSL_DIR="${ROOT_DIR}/ssl"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.security.yml"

# Charger .env si présent dans le root dir
if [ -f "${ROOT_DIR}/.env" ]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

if ! command -v docker &> /dev/null; then
  echo "Docker introuvable. Installe Docker Desktop ou la CLI Docker." >&2
  exit 1
fi

mkdir -p "${SSL_DIR}"

GITIGNORE="${ROOT_DIR}/.gitignore"
if [ ! -f "${GITIGNORE}" ]; then
  echo "Création minimale de .gitignore"
  printf "%s\n" "ssl/*-key.pem" "ssl/rootCA-key.pem" > "${GITIGNORE}"
else
  grep -qxF "ssl/*-key.pem" "${GITIGNORE}" || printf "%s\n" "ssl/*-key.pem" >> "${GITIGNORE}"
  grep -qxF "ssl/rootCA-key.pem" "${GITIGNORE}" || printf "%s\n" "ssl/rootCA-key.pem" >> "${GITIGNORE}"
fi

# Valeur par défaut si HOSTS n’est pas défini dans .env
HOSTS="${HOSTS:-localhost broker backend 127.0.0.1 ::1}"
export HOSTS

echo "Utilisation des hôtes: ${HOSTS}"
echo "Les fichiers seront écrits dans: ${SSL_DIR}"
echo "Build et exécution du service mkcert + openssl..."

docker compose -f "${COMPOSE_FILE}" run --rm -T mkcert bash -c "
  # Certificat serveur (Angular HTTPS)
  mkcert -cert-file /data/server_cert.pem -key-file /data/server_key.pem \$HOSTS

  # Certificat client (backend MQTT)
  openssl genrsa -out /data/backend_key.pem 2048 &&
  openssl req -new -key /data/backend_key.pem -out /data/backend.csr -subj '/CN=backend-client' &&
  openssl x509 -req -in /data/backend.csr -CA /data/rootCA.pem -CAkey /data/rootCA-key.pem \
    -CAcreateserial -out /data/backend_cert.pem -days 365 -sha256
"

echo
echo "=== Résultat (sur l'hôte) ==="
ls -la "${SSL_DIR}" || true