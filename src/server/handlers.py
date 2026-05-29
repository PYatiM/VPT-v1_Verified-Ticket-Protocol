import time
import hmac

from .exceptions import VTPProtocolError
from common.crypto import hmac_sha256, rand_hex,TICKET_KEY, SESSION_KEY
from common.config import MAX_SEQ, SERVER_SECRET, HANDSHAKE_TTL, SESSION_TTL

SCHEMAS = {
    "hello": {"V", "type", "client_nonce"},
    "activate": {"V", "type", "ticket", "proof"},
    "data": {"V", "type", "ticket", "seq", "payload", "mac"},
    }

def validate(msg:dict) -> None:
    t = msg.get("type")
    if t not in SCHEMAS:
        raise VTPProtocolError(f"Invalid message type: {t!r}")
    missing = SCHEMAS[t] - msg.keys()
    if missing:
        raise VTPProtocolError(f"Missing fields for {t} : {missing!r}")
    if msg["V"] != 1:
        raise VTPProtocolError(f"Unsupported protocol version: {msg.get('V')!r}")

class ProtocolHandlers:
    def __init__(self, store):
        self.store = store

    async def handle_hello(self, msg, ip, send_func):
        client_nonce = msg["client_nonce"]
        server_nonce = rand_hex(8)
        expires = time.time() + HANDSHAKE_TTL

        ticket = hmac_sha256(
            TICKET_KEY,
            f"{client_nonce}{server_nonce}{ip}{expires}".encode()
        )

        self.store.create_pending(ticket, {
            "client_nonce": client_nonce,
            "server_nonce": server_nonce,
            "ip": ip,
            "expires": expires
        })

        await send_func({
            "v": 1,
            "type": "challenge",
            "server_nonce": server_nonce,
            "expires_at": int(expires)
        })

        await send_func({
            "v": 1,
            "type": "ticket",
            "ticket": ticket,
            "expires_at": int(expires)
        })

    async def handle_activate(self, msg, ip, send_func):
        ticket = msg["ticket"]
        proof = msg["proof"]

        pending = self.store.get_pending(ticket)
        if not pending:
            return

        if pending["ip"] != ip:
            return

        key = hmac_sha256(
            SESSION_KEY,
            f"{ticket}{pending['client_nonce']}{pending['server_nonce']}".encode()
        ).encode()

        expected = hmac_sha256(key, b"ACTIVATE")

        if not hmac.compare_digest(expected, proof):
            return

        self.store.activate(ticket, {
            "session_key": key,
            "last_seq": 0,
            "ip": ip,
            "expires": time.time() + SESSION_TTL
        })

        await send_func({
            "v": 1,
            "type": "ok"
        })

    async def handle_data(self, msg, ip):
        ticket = msg["ticket"]
        seq = msg["seq"]
        payload = msg["payload"]
        mac = msg["mac"]

        session = self.store.get_active(ticket)
        if not isinstance(seq, int) or seq <= 0 or seq > MAX_SEQ:
            return None

        if not session:
            return None

        if time.time() > session["expires"]:
            self.store.invalidate(ticket)
            return None

        if session["ip"] != ip:
            return None

        async with self._lock:
            if seq <= session["last_seq"]:
                return None

            expected = hmac_sha256(
                session["session_key"],
                f"{seq}{payload}".encode()
            )

            if not hmac.compare_digest(expected, mac):
                return None

            session["last_seq"] = seq
        return payload
