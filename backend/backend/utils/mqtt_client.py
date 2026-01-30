import paho.mqtt.client as mqtt
import json
import logging
logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, broker_host="localhost", broker_port=8883, client_id="backend",
                 ca_cert="/ssl/rootCA.pem", certfile="/ssl/backend_cert.pem", keyfile="/ssl/backend_key.pem"):
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.topic_callbacks = {}

        # Activer TLS seulement si les certificats sont fournis
        if ca_cert and certfile and keyfile:
            self.client.tls_set(ca_certs=ca_cert, certfile=certfile, keyfile=keyfile)
            self.client.tls_insecure_set(False)

        self.client.connect(broker_host, broker_port, keepalive=60)
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("✅ MQTT connected successfully")
        else:
            logger.error("❌ MQTT connection failed (rc=%s)", rc)
        
        for topic in self.topic_callbacks:
            client.subscribe(topic)
            client.message_callback_add(topic, self.topic_callbacks[topic])

    def _on_message(self, client, userdata, msg):
        logger.info("📦 Unhandled MQTT message received: topic=%s payload=%s", msg.topic, msg.payload.decode())

    def register_callback(self, topic, callback):
        self.topic_callbacks[topic] = callback
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, callback)

    def publish(self, topic, payload, retain=False):
        if isinstance(payload, (str, bytes)):
            raw = payload if isinstance(payload, str) else payload.decode("utf-8")
        else:
            raw = json.dumps(payload)
        self.client.publish(topic, raw, retain=retain)