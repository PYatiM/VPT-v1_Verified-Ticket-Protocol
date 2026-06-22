import json
import struct
import asyncio

MAX_MESSAGE_SIZE = 1024 * 1024  # 1 MB safety cap
READ_TIMEOUT = 10.0

async def send_msg(writer, msg):
    data = json.dumps(msg, sort_keys=True, seperators=(",",":")).encode("utf-8")
    
    if len(data) > MAX_MESSAGE_SIZE:
        raise VTPProtocolError("Outgoing Message too large")

    writer.write(struct.pack(">I", len(data)))
    writer.write(data)
    try:
        await asyncio.wait_for(writer.drain(), timeout=10.0)
    except asyncio.TimeoutError:
        raise VTPProtocolError("write timeout - client not reading")

async def recv_msg(reader: asyncio.StreamReader) -> dict:
    try:
        header = await asyncio.wait_for(reader.readexactly(4), READ_TIMEOUT)
    except asyncio.TimeoutError:
        raise VTPProtocolError("Read timeout waiting for message header")

    length = struct.unpack(">I", header)[0]

    if length > MAX_MESSAGE_SIZE:
        raise VTPProtocolError(f"Message length {length} exceeds cap")

    try:
        data = await asyncio.wait_for(reader.readexactly(length), READ_TIMEOUT)
    except asyncio.TimeoutError:
        raise VTPProtocolError("Read timeout waiting for message body")

    try:
        return json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise VTPProtocolError(f"Malformed message bodu : {e}")