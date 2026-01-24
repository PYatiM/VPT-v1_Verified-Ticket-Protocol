import asyncio
import sys
import os

sys.path.append(os.path.abspath("../src"))

from server.server import VTPServer

async def main():
    server = VTPServer(host="127.0.0.1", port=9000)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
