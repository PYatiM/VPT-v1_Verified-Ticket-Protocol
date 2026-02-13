import time
 
class SessionStore:
    def __init__(self):
        self.pending = {}
        self.active = {}

    def create_pending(self, ticket, data):
        self.pending[ticket] = data

    def get_pending(self, ticket):
        return self.pending.get(ticket)

    def activate(self, ticket, session):
        self.pending.pop(ticket, None)
        self.active[ticket] = session

    def get_active(self, ticket):
        return self.active.get(ticket)

    def invalidate(self, ticket):
        self.pending.pop(ticket, None)
        self.active.pop(ticket, None)

    def cleanup(self):
        now = time.time()

        for t in list(self.pending.keys()):
            if self.pending[t]["expires"] < now:
                self.pending.pop(t)

        for t in list(self.active.keys()):
            if self.active[t]["expires"] < now:
                self.active.pop(t)
