import asyncio
import sys
import os

sys.path.append(os.path.abspath("../src"))

from client.client import VTPClient

async def main():
    client = VTPClient(host="127.0.0.1", port=9000)
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())

