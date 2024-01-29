import sys

import discord
import asqlite
import jishaku
from discord.ext import commands

from config import DISCORD_TOKEN

COGS = ("cogs.invites",)


class ManagerBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            owner_ids={767115163127906334, 993796385432424519},
            case_insensitive=True,
            strip_after_prefix=True,
            intents=discord.Intents.all(),
        )

    async def setup_hook(self) -> None:
        self.pool = await asqlite.create_pool("./db/eranodes_manager.db")
        async with self.pool.acquire() as c:
            with open("./db/schema.sql") as f:
                await c.executescript(f.read())

        loaded = []
        for ext in COGS:
            try:
                await self.load_extension(ext)
                loaded += [ext]
            except Exception as e:
                print(f"Failed to load extension {ext}: {e}")

        print(f"Loaded extensions: \n> {'\n> '.join(loaded)}")

    async def on_ready(self):
        print(
            f"<--- Ready --->",
            f"Logged in as {self.user} (ID: {self.user.id})",
            f"Seeing {len(self.guilds)} guilds",
            f"Python version: {sys.version}",
            f"discord.py {discord.__version__} | jishaku {jishaku.__version__}",
            sep="\n",
        )

    async def start(self) -> None:
        return await super().start(DISCORD_TOKEN, reconnect=True)
