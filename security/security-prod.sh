#!/usr/bin/env bash
set -euo pipefail

# Production MQTT SSL certificate generation
# This script generates certificates for MQTT broker in production

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
SSL_DIR="${ROOT_DIR}/ssl-mqtt"
DOMAIN="${MQTT_DOMAIN:-ezplantparent.com}"

echo "=== Production MQTT Certificate Generation ==="
echo "Domain: ${DOMAIN}"
echo "SSL Directory: ${SSL_DIR}"

mkdir -p "${SSL_DIR}"

# Check if certificates already exist
if [ -f "${SSL_DIR}/rootCA.pem" ] && [ -f "${SSL_DIR}/server_cert.pem" ] && [ -f "${SSL_DIR}/backend_cert.pem" ]; then
  echo "Certificates already exist. To regenerate, delete ${SSL_DIR} first."
  exit 0
fi

echo ""
echo "Step 1: Generate Root CA"
echo "------------------------"
openssl genrsa -out "${SSL_DIR}/rootCA-key.pem" 4096
openssl req -x509 -new -nodes -key "${SSL_DIR}/rootCA-key.pem" \
  -sha256 -days 3650 -out "${SSL_DIR}/rootCA.pem" \
  -subj "/C=CA/ST=Quebec/L=Montreal/O=EzPlantParent/CN=EzPlantParent Root CA"

echo ""
echo "Step 2: Generate MQTT Broker Server Certificate"
echo "------------------------------------------------"
openssl genrsa -out "${SSL_DIR}/server_key.pem" 2048

# Create config file for Subject Alternative Names (SAN)
cat > "${SSL_DIR}/server.cnf" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C = CA
ST = Quebec
L = Montreal
O = EzPlantParent
CN = ${DOMAIN}

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = *.${DOMAIN}
DNS.3 = localhost
DNS.4 = broker
DNS.5 = broker_prod
IP.1 = 127.0.0.1
EOF

openssl req -new -key "${SSL_DIR}/server_key.pem" \
  -out "${SSL_DIR}/server.csr" \
  -config "${SSL_DIR}/server.cnf"

openssl x509 -req -in "${SSL_DIR}/server.csr" \
  -CA "${SSL_DIR}/rootCA.pem" \
  -CAkey "${SSL_DIR}/rootCA-key.pem" \
  -CAcreateserial -out "${SSL_DIR}/server_cert.pem" \
  -days 365 -sha256 \
  -extensions v3_req \
  -extfile "${SSL_DIR}/server.cnf"

echo ""
echo "Step 3: Generate Backend Client Certificate"
echo "--------------------------------------------"
openssl genrsa -out "${SSL_DIR}/backend_key.pem" 2048
openssl req -new -key "${SSL_DIR}/backend_key.pem" \
  -out "${SSL_DIR}/backend.csr" \
  -subj "/CN=backend-client"
openssl x509 -req -in "${SSL_DIR}/backend.csr" \
  -CA "${SSL_DIR}/rootCA.pem" \
  -CAkey "${SSL_DIR}/rootCA-key.pem" \
  -CAcreateserial -out "${SSL_DIR}/backend_cert.pem" \
  -days 365 -sha256

echo ""
echo "Step 4: Generate ESP32 Client Certificate Template"
echo "---------------------------------------------------"
echo "To generate certificates for ESP32 devices, run:"
echo ""
echo "  openssl genrsa -out ${SSL_DIR}/esp32_<MAC>_key.pem 2048"
echo "  openssl req -new -key ${SSL_DIR}/esp32_<MAC>_key.pem \\"
echo "    -out ${SSL_DIR}/esp32_<MAC>.csr -subj '/CN=<MAC_ADDRESS>'"
echo "  openssl x509 -req -in ${SSL_DIR}/esp32_<MAC>.csr \\"
echo "    -CA ${SSL_DIR}/rootCA.pem -CAkey ${SSL_DIR}/rootCA-key.pem \\"
echo "    -CAcreateserial -out ${SSL_DIR}/esp32_<MAC>_cert.pem -days 365 -sha256"
echo ""

# Set permissions
chmod 600 "${SSL_DIR}"/*-key.pem 2>/dev/null || true
chmod 644 "${SSL_DIR}"/*.pem 2>/dev/null || true

echo ""
echo "=== Certificate Generation Complete ==="
echo ""
echo "Generated files in ${SSL_DIR}:"
ls -lh "${SSL_DIR}"

echo ""
echo "Important files for ESP32 devices:"
echo "  - rootCA.pem: Root CA certificate (copy to ESP32)"
echo "  - server_cert.pem: Broker certificate (for verification)"
echo ""
echo "For backend (already mounted in docker-compose):"
echo "  - backend_cert.pem: Client certificate"
echo "  - backend_key.pem: Client private key"
echo ""
echo "Next steps:"
echo "1. Restart docker-compose: docker compose -f docker-compose.traefik.yml down && docker compose -f docker-compose.traefik.yml up -d"
echo "2. Copy rootCA.pem to your ESP32 devices for TLS verification"
echo "3. Configure ESP32 to connect to ${DOMAIN}:8883 with TLS"
