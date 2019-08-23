import asyncio
import time

import aioredis
from sqlalchemy import event
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket


class DataNotify:
    group = "data_notify"

    @classmethod
    def register_model(cls, model) -> None:
        """ register a sqlalchemy models to send data updates for """

        @event.listens_for(model, "after_insert", propagate=True)
        def receive_after_insert(mapper, connection, target):
            data = cls.data_message(target, "insert")
            asyncio.ensure_future(cls.send_data_event(data))

        @event.listens_for(model, "after_update", propagate=True)
        def receive_after_update(mapper, connection, target):
            data = cls.data_message(target, "update")
            asyncio.ensure_future(cls.send_data_event(data))

        @event.listens_for(model, "after_delete", propagate=True)
        def receive_after_delete(mapper, connection, target):
            data = cls.data_message(target, "delete")
            asyncio.ensure_future(cls.send_data_event(data))

    @classmethod
    def data_message(cls, target, method):
        return {
            "message_type": f"{cls.group}.{method}",
            "object_id": target.id,
            "table": target.__class__.__table__.name,
            "time_sent": int(time.time()),
        }

    @classmethod
    async def send_data_event(cls, data):
        redis = await aioredis.create_redis("redis://redis/0")
        redis.publish_json(f"{cls.group}:1", data)


class DataSocket(WebSocketEndpoint):
    encoding = "json"  # type: ignore
    group = "data_notify"

    async def subscribe(self, ws):
        redis = await aioredis.create_redis("redis://redis/0")
        channel = (await redis.subscribe(f"{self.group}:1"))[0]
        while await channel.wait_message():
            msg = await channel.get_json()
            await ws.send_json(msg)

    async def validate_token(self, token: str) -> bool:
        return token == "123456"

    async def on_receive(self, websocket: WebSocket, data):
        if "token" not in data:
            return

        token = data["token"]
        token_is_valid = await self.validate_token(token)

        if not token_is_valid:
            await websocket.send_json({"status": "invalid token"})
        else:
            await websocket.send_json({"status": "authenticated"})
            try:
                await self.subscribe(websocket)
            except Exception:
                pass
