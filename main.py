import asyncio

from bot import ManagerBot


async def start():
    async with ManagerBot() as bot:
        await bot.start()


if __name__ == "__main__":
    asyncio.run(start())
