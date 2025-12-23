import aiohttp
import asyncio


async def main():
    session = aiohttp.ClientSession("https://openlibrary.org/")
    # res = await session.get("search.json")
    # print(await res.text())
    async with session.get("search.json") as res:
        print(await res.text())


if __name__ == "__main__":
    asyncio.run(main=main())
