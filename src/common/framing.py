import json
import struct
import asyncio

MAX_MESSAGE_SIZE = 1024 * 1024  # 1 MB safety cap

async def send_msg(writer, msg):
    data = json.dumps(msg).encode("utf-8")
    length = len(data)

    if length > MAX_MESSAGE_SIZE:
        raise ValueError("Message too large")

    writer.write(struct.pack(">I", length))
    writer.write(data)
    await writer.drain()

async def recv_msg(reader):
    header = await reader.readexactly(4)
    length = struct.unpack(">I", header)[0]

    if length > MAX_MESSAGE_SIZE:
        raise ValueError("Incoming message too large")

    data = await reader.readexactly(length)
    return json.loads(data.decode("utf-8"))
