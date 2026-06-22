import time
import asyncio

MAX_PENDING_PER_IP = 5

class SessionStore:
    def __init__(self):
        self.pending: dict = {}
        self.active: dict = {}
        self._lock = asyncio.Lock()

    async def create_pending(self, ticket: str, data: dict) -> bool:
        ip = data["ip"]
        current = sum(1 for v in self.pending.values() if v["ip"] == ip)
        if current >= MAX_PENDING_PER_IP:
            return False
        async with self._lock:  
            self.pending[ticket] = data
        return True

    async def get_pending(self, ticket):
        async with self._lock:
            return self.pending.get(ticket)

    async def activate(self, ticket, session):
        self.pending.pop(ticket, None)
        self.active[ticket] = session

    async def get_active(self, ticket):
        async with self._lock:
            return self.active.get(ticket)

    async def invalidate(self, ticket):
        self.pending.pop(ticket, None)
        self.active.pop(ticket, None)

    async def cleanup(self):
        now = time.time()

        for t in list(self.pending.keys()):
            if self.pending[t]["expires"] < now:
                self.pending.pop(t)

        for t in list(self.active.keys()):
            if self.active[t]["expires"] < now:
                self.active.pop(t)
