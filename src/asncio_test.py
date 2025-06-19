import asyncio
import httpx


async def call_slow(id: int):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get("http://127.0.0.1:8000/slow?seconds=10")
        print(f"[{id}] Got:", r.json())


async def main():
    await asyncio.gather(
        call_slow(1),
        call_slow(2),
        call_slow(3),
    )

asyncio.run(main())
