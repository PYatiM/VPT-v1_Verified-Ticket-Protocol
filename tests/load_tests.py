import asyncio
import sys
import os
import time

sys.path.append(os.path.abspath("src"))

from client.client import VTPClient

CLIENTS = 25

async def spawn_client(i):
    try:
        client = VTPClient()
        await client.run()
        print(f"Client {i} finished")
    except Exception as e:
        print(f"Client {i} failed:", e)

async def main():
    start = time.time()
    tasks = []

    for i in range(CLIENTS):
        tasks.append(asyncio.create_task(spawn_client(i)))

    await asyncio.gather(*tasks)

    print("Total time:", round(time.time() - start, 2), "seconds")

if __name__ == "__main__":
    asyncio.run(main())
