import asyncio
import sys

from server.server import VTPServer
from client.client import VTPClient

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py server|client")
        return

    mode = sys.argv[1]

    if mode == "server":
        asyncio.run(VTPServer().start())

    elif mode == "client":
        asyncio.run(VTPClient().run())

    else:
        print("Invalid mode")

if __name__ == "__main__":
    main()
