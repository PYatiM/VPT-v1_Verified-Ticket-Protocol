import time
import json
import redis.asyncio as redis

class RedisSessionStore:
    def __init__(self, redis_url="redis://localhost"):
        self.r = redis.from_url(redis_url, decode_responses=True)

    async def create_pending(self, ticket: str, data: dict) -> bool:
        await self.r.setex(f"pending:{ticket}", 60, json.dumps(data))
        return True

    async def get_pending(self, ticket):
        data = await self.r.get(f"pending:{ticket}")
        return json.loads(data) if data else None

    async def activate(self, ticket, session):
        await self.r.delete(f"pending:{ticket}")
        await self.r.setex(f"active:{ticket}", 3600, json.dumps(session))

    async def get_active(self, ticket):
        data = await self.r.get(f"active:{ticket}")
        return json.loads(data) if data else None

    async def invalidate(self, ticket):
        await self.r.delete(f"pending:{ticket}")
        await self.r.delete(f"active:{ticket}")

    async def cleanup(self):
        pass # redis will handle ttl on its own
        