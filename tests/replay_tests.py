import asyncio
import sys
import os

sys.path.append(os.path.abspath("src")) 

from client.client import VTPClient
from common.crypto import hmac_sha256
from common.framing import send_msg, recv_msg
from common.config import SERVER_SECRET

class ReplayClient(VTPClient):
    async def run(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)

        from common.crypto import rand_hex

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

        seq = 1
        payload = "replay-test"

        mac = hmac_sha256(
            session_key,
            f"{seq}{payload}".encode()
        )

        packet = {
            "v": 1,
            "type": "data",
            "ticket": ticket,
            "seq": seq,
            "payload": payload,
            "mac": mac
        }

        print("Sending original packet")
        await send_msg(writer, packet)

        await asyncio.sleep(1)

        print("Replaying same packet")
        await send_msg(writer, packet)

        writer.close()
        await writer.wait_closed()

async def main():
    client = ReplayClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
