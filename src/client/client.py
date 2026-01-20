import asyncio
import hmac

from common.crypto import hmac_sha256, rand_hex
from common.framing import send_msg, recv_msg
from common.config import SERVER_SECRET

class VTPClient:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.seq = 0

    async def run(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)

        client_nonce = rand_hex(8)

        await send_msg(writer, {
            "v": 1,
            "type": "hello",
            "client_nonce": client_nonce
        })

        challenge = await recv_msg(reader)
        ticket_msg = await recv_msg(reader)

        server_nonce = challenge["server_nonce"]
        ticket = ticket_msg["ticket"]

        session_key = hmac_sha256(
            SERVER_SECRET,
            f"{ticket}{client_nonce}{server_nonce}".encode()
        ).encode()

        proof = hmac_sha256(session_key, b"ACTIVATE")

        await send_msg(writer, {
            "v": 1,
            "type": "activate",
            "ticket": ticket,
            "proof": proof
        })

        await recv_msg(reader)

        for msg in ["hello", "secure world", "vtp protocol"]:
            self.seq += 1
            mac = hmac_sha256(
                session_key,
                f"{self.seq}{msg}".encode()
            )

            await send_msg(writer, {
                "v": 1,
                "type": "data",
                "ticket": ticket,
                "seq": self.seq,
                "payload": msg,
                "mac": mac
            })

        writer.close()
        await writer.wait_closed()
