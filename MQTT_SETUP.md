# MQTT Setup Guide

## Architecture

The MQTT broker (Eclipse Mosquitto) is used for real-time communication between:
- **Backend** → **Broker**: Publishes commands and subscribes to sensor data
- **ESP32 devices** → **Broker**: Publishes sensor data and subscribes to commands

## Local Development

### 1. Generate Certificates

```bash
./develop.sh
# Choose option 8: Generate security certificates (local dev)
```

This creates certificates in `./ssl/`:
- `rootCA.pem`: Root CA certificate
- `server_cert.pem`: Broker server certificate
- `server_key.pem`: Broker server private key
- `backend_cert.pem`: Backend client certificate
- `backend_key.pem`: Backend client private key

### 2. Start Local Environment

```bash
docker-compose up -d
```

The broker is available at:
- `localhost:1883` - Non-TLS (allow_anonymous)
- `localhost:8883` - TLS (require_certificate)

### 3. Backend Configuration

The backend connects to MQTT with TLS in `backend/backend/utils/mqtt_client.py`:

```python
MQTTClient(
    broker_host="broker",
    broker_port=8883,
    ca_cert="/ssl/rootCA.pem",
    certfile="/ssl/backend_cert.pem",
    keyfile="/ssl/backend_key.pem"
)
```

## Production Deployment

### 1. Generate Production Certificates

On your VPS or via GitHub Actions:

```bash
chmod +x security/security-prod.sh
MQTT_DOMAIN=ezplantparent.com ./security/security-prod.sh
```

This creates certificates in `./ssl-mqtt/`:
- `rootCA.pem`: Root CA (copy this to ESP32 devices)
- `server_cert.pem`: Broker certificate with SAN for domain
- `backend_cert.pem`: Backend client certificate

### 2. Deploy with Docker Compose

```bash
docker compose -f docker-compose.traefik.yml up -d
```

The broker is available at:
- **Internal**: `broker:8883` (for backend via Docker network)
- **External**: `ezplantparent.com:8883` (for ESP32 devices via Traefik)

### 3. Firewall Configuration

Ensure port 8883 is open on your VPS:

```bash
# UFW
sudo ufw allow 8883/tcp

# Or firewalld
sudo firewall-cmd --permanent --add-port=8883/tcp
sudo firewall-cmd --reload
```

## ESP32 Configuration

### 1. Copy Root CA to ESP32

Download `ssl-mqtt/rootCA.pem` from your VPS and embed it in your ESP32 firmware.

### 2. MQTT Connection Code

```cpp
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

const char* mqtt_server = "ezplantparent.com";
const int mqtt_port = 8883;

// Copy content of rootCA.pem here
const char* root_ca = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIFXzCCA0egAwIBAgIUXXXXXXXXXXXXXXXXXXXXXXXXXXXwDQYJKoZIhvcNAQEL\n" \
// ... rest of certificate ...
"-----END CERTIFICATE-----\n";

WiFiClientSecure espClient;
PubSubClient client(espClient);

void setup() {
  espClient.setCACert(root_ca);
  espClient.setInsecure(); // Remove this line for production!
  
  client.setServer(mqtt_server, mqtt_port);
  
  // Connect with station MAC address as client ID and CN
  String clientId = WiFi.macAddress();
  clientId.replace(":", "");
  client.connect(clientId.c_str());
}
```

### 3. Generate ESP32 Client Certificate (Optional, for mutual TLS)

For enhanced security with `require_certificate true`:

```bash
cd ssl-mqtt
MAC="781C3CB76C2C"  # Replace with your ESP32 MAC address

# Generate client certificate
openssl genrsa -out esp32_${MAC}_key.pem 2048
openssl req -new -key esp32_${MAC}_key.pem \
  -out esp32_${MAC}.csr -subj "/CN=${MAC}"
openssl x509 -req -in esp32_${MAC}.csr \
  -CA rootCA.pem -CAkey rootCA-key.pem \
  -CAcreateserial -out esp32_${MAC}_cert.pem -days 365 -sha256
```

Then embed both certificate and key in ESP32:

```cpp
espClient.setCACert(root_ca);
espClient.setCertificate(client_cert);  // esp32_${MAC}_cert.pem
espClient.setPrivateKey(client_key);     // esp32_${MAC}_key.pem
```

## MQTT Topics

### Station Data (ESP32 → Backend)

```
stations/{MAC_ADDRESS}/data
```

Payload example:
```json
{
  "temperature": 22.5,
  "humidity": 65.0,
  "soil_moisture": 450,
  "timestamp": "2025-12-04T10:30:00Z"
}
```

### Station Commands (Backend → ESP32)

```
stations/{MAC_ADDRESS}/commands
```

Payload example:
```json
{
  "action": "water",
  "duration": 5000,
  "pump_id": 1
}
```

## Mosquitto Configuration

Located in `broker/config/mosquitto.conf`:

```conf
# Allow anonymous on port 1883 (local only)
listener 1883
allow_anonymous true

# Require TLS certificate on port 8883
listener 8883
cafile /mosquitto/ssl/rootCA.pem
certfile /mosquitto/ssl/server_cert.pem
keyfile /mosquitto/ssl/server_key.pem
require_certificate true
use_identity_as_username true
acl_file /mosquitto/config/acl
```

## Access Control (ACL)

Located in `broker/config/acl`:

```conf
# Stations can only read/write their own topics
pattern read  stations/%u/#
pattern write stations/%u/#

# Backend has full access
user backend-client
topic write stations/+/#
topic read  stations/+/#
```

The `%u` is replaced by the CN from the client certificate (MAC address for ESP32).

## Troubleshooting

### Backend can't connect to broker

Check logs:
```bash
docker logs backend_prod
```

Verify certificates are mounted:
```bash
docker exec backend_prod ls -la /ssl/
```

### ESP32 connection refused

1. Check firewall allows port 8883
2. Verify ESP32 has correct rootCA.pem
3. Test with `openssl s_client`:

```bash
openssl s_client -connect ezplantparent.com:8883 -CAfile ssl-mqtt/rootCA.pem
```

### Certificate expired

Regenerate certificates:
```bash
rm -rf ssl-mqtt
./security/security-prod.sh
docker compose -f docker-compose.traefik.yml restart broker backend
```

## Security Best Practices

1. **Never commit private keys** to git (already in `.gitignore`)
2. **Use certificate-based authentication** in production (`require_certificate true`)
3. **Keep certificates up to date** (regenerate yearly)
4. **Use unique certificates per ESP32** for device-level revocation
5. **Monitor broker logs** for unauthorized access attempts

## Monitoring

View broker logs:
```bash
docker logs broker_prod -f

# Or check log files
docker exec broker_prod tail -f /mosquitto/log/mosquitto.log
```

Check connected clients:
```bash
docker exec broker_prod mosquitto_sub -t '$SYS/broker/clients/connected' -C 1
```
