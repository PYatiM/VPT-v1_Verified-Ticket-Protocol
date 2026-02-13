import asyncio
import sys
import os

sys.path.append(os.path.abspath("src"))

from common.crypto import hmac_sha256, rand_hex
from common.framing import send_msg, recv_msg
from common.config import SERVER_SECRET

async def run():
    reader, writer = await asyncio.open_connection("127.0.0.1", 9000)

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
    real_payload = "secure-message"

    mac = hmac_sha256(
        session_key,
        f"{seq}{real_payload}".encode()
    )

    tampered_payload = "hacked-message"

    print("Sending tampered packet")

    await send_msg(writer, {
        "v": 1,
        "type": "data",
        "ticket": ticket,
        "seq": seq,
        "payload": tampered_payload,
        "mac": mac
    })

    writer.close()
    await writer.wait_closed() 

if __name__ == "__main__":
    asyncio.run(run())
