# utils/deps.py
from fastapi import Request

def get_mqtt(request: Request):
    mqtt = getattr(request.app.state, "mqtt", None)
    if mqtt is None:
        raise RuntimeError("MQTT client not initialised")
    return mqtt