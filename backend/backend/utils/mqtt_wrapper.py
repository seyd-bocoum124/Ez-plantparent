import asyncio
import logging
from typing import Dict, Set, Optional
from starlette.websockets import WebSocket as StarletteWebSocket

from utils.mqtt_client import MQTTClient

logger = logging.getLogger(__name__)

class MQTTWrapper:
    """
    Wrapper around raw MQTTClient.
    - Delegates payload serialization to MQTTClient.publish (no json.dumps here).
    - active_ws_map is a Dict[station_id, Set[WebSocket]].
    - publish_and_notify can notify a specific station or all stations.
    """
    def __init__(self, raw_client: MQTTClient, loop: asyncio.AbstractEventLoop, active_ws_map: Dict[str, Set[StarletteWebSocket]]):
        self._client = raw_client
        self._loop = loop
        self._active_ws_map = active_ws_map
        self._logger = logging.getLogger(__name__)

    def publish_json(self, topic: str, obj):
        """
        Publish obj to broker and let MQTTClient handle serialization.
        obj may be a dict, list, str, bytes — behaviour follows MQTTClient.publish contract.
        """
        try:
            # Try the common signature: publish(topic, payload)
            self._client.publish(topic, obj)
        except TypeError:
            # Try alternative signatures progressively (best-effort)
            try:
                # some clients expect bytes
                if isinstance(obj, str):
                    self._client.publish(topic, obj.encode("utf-8"))
                else:
                    self._client.publish(topic, obj)
            except Exception:
                self._logger.exception("MQTT publish failed (fallback attempts) for topic=%s", topic)
                raise
        except Exception:
            self._logger.exception("MQTT publish failed for topic=%s", topic)
            raise

    def publish_and_notify(self, topic: str, obj, notify_text: Optional[str] = None, notify_station: Optional[str] = None):
        """
        Publish to broker then notify websockets.
        - notify_station: if provided, notify only that station's sockets.
        - if notify_station is None and notify_text provided, notify all registered stations.
        """
        # publish first (delegate serialization to MQTTClient)
        self.publish_json(topic, obj)

        if not notify_text:
            return

        async def _notify_station(st_id: str, text: str):
            for ws in list(self._active_ws_map.get(st_id, set())):
                try:
                    await ws.send_text(text)
                except Exception:
                    try:
                        self._active_ws_map[st_id].discard(ws)
                    except Exception:
                        pass
                    self._logger.info("Removed closed websocket during publish notify for station %s", st_id)

        async def _notify_all(text: str):
            for st_id in list(self._active_ws_map.keys()):
                await _notify_station(st_id, text)

        def _safe_task(coro):
            task = asyncio.create_task(coro)
            def _swallow_done(t):
                try:
                    t.result()
                except Exception as e:
                    logger.warning("Unhandled exception in notify task: %s", e)
            task.add_done_callback(_swallow_done)
            return task

        try:
            if notify_station:
                self._loop.call_soon_threadsafe(_safe_task, _notify_station(notify_station, notify_text))
            else:
                self._loop.call_soon_threadsafe(_safe_task, _notify_all(notify_text))
        except Exception:
            self._logger.exception("Failed to schedule websocket notify task")
            raise