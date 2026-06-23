import asyncio
import logging
import ssl

from common.framing import VTPProtocolError, recv_msg, send_msg
from server.session_store import SessionStore
from server.handlers import ProtocolHandlers
from server.rate_limiter import TokenBucket

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VTPServer")

class VTPServer:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.store = SessionStore()
        self.handlers = ProtocolHandlers(self.store)
        self.rate_limiter = TokenBucket(rate=5, burst=10)

    async def handle_client(self, reader, writer):
        ip = writer.get_extra_info("peername")[0]

        async def send(data):
            await send_msg(writer, data)

        try:
            while True:
                msg = await recv_msg(reader)
                t = msg.get("type")

                if t == "hello":
                    if not self.rate_limiter.allow(ip):
                        logger.info(f"[{ip}] rate limit exceeded — closing connection")
                        writer.close()
                        return
                    await self.handlers.handle_hello(msg, ip, send)

                elif t == "activate":
                    await self.handlers.handle_activate(msg, ip, send)

                elif t == "data":
                    payload = await self.handlers.handle_data(msg, ip)
                    if payload:
                        logger.info(f"[{ip}] {payload}")

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

    async def cleanup_loop(self):
        while True:
            await asyncio.sleep(60)
            await self.store.cleanup()

    async def start(self):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port,
            ssl=ssl_context
        )

        logger.info(f"VTP Server running on {self.host}:{self.port}")

        async with server:
            await server.serve_forever()

        asyncio.create_task(self.store.cleanup_loop())
