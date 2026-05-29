import asyncio
from logging import logger

from common.framing import VTPProtocolError, recv_msg, send_msg
from server.session_store import SessionStore
from server.handlers import ProtocolHandlers
 
class VTPServer:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.store = SessionStore()
        self.handlers = ProtocolHandlers(self.store)

    async def handle_client(self, reader, writer):
        ip = writer.get_extra_info("peername")[0]

        async def send(data):
            await send_msg(writer, data)

        try:
            while True:
                msg = await recv_msg(reader)
                t = msg.get("type")

                if t == "hello":
                    await self.handlers.handle_hello(msg, ip, send)

                elif t == "activate":
                    await self.handlers.handle_activate(msg, ip, send)

                elif t == "data":
                    payload = await self.handlers.handle_data(msg, ip)
                    if payload:
                        print(f"[{ip}] {payload}")

                self.store.cleanup()
        except:
            pass
        except VTPProtocolError as e:
            logger.warning(f"Protocol error from {ip}: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error from {ip}")
        finally:
            writer.close()
            await writer.wait_closed()

        writer.close()
        await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )

        print(f"VTP Server running on {self.host}:{self.port}")

        async with server:
            await server.serve_forever()
