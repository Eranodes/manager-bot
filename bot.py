#
# This file is part of EraNodes/manager-bot. (https://github.com/eranodes/manager-bot)
# Copyright (c) 2023-present Ritam Das
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys

import discord
import asqlite
import jishaku
from discord.ext import commands

from config import DISCORD_TOKEN, INVITE_TRACKING_CHANNEL, OWNER_IDS
from cogs.util.invite_tracker import InviteTracker

COGS = [
    "cogs.dev",
    "cogs.error",
    "cogs.invites",
    "cogs.validation",
    "cogs.suggestions",
    "cogs.support",
    "cogs.userwarn",
    "cogs.banned",
]


class ManagerBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            owner_ids=OWNER_IDS,
            case_insensitive=True,
            strip_after_prefix=True,
            intents=discord.Intents.all(),
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="over EraNodes"
            ),
        )

    async def setup_hook(self) -> None:
        # Set uptime values
        self.up_for = discord.utils.utcnow()

        # Setup invite tracker
        self.invite_tracker = InviteTracker(self)
        await self.invite_tracker.set_invite_channel(INVITE_TRACKING_CHANNEL)

        # Setup logging
        discord.utils.setup_logging()

        # Setup DBs
        self.pool = await asqlite.create_pool("./db/eranodes_manager.db")
        async with self.pool.acquire() as c:
            with open("./db/schema.sql") as f:
                await c.executescript(f.read())

        # Load Extensions
        await self.load_extension("jishaku")
        loaded = []
        for ext in COGS:
            try:
                await self.load_extension(ext)
                loaded += [ext]
            except Exception as e:
                print(f"Failed to load extension {ext}: {e}")

        print(
            f"----------------- ⚙️ Loaded Extensions ----------------- \n> {'\n> '.join(loaded)}",
            f"--------------------------------------------------------",
            f"\n",
            sep="\n",
        )

    async def on_ready(self):
        print(
            f"\n",
            f"----------------------- 🌟 Ready -----------------------",
            f"Logged in as {self.user} (ID: {self.user.id})",  # type: ignore
            f"Seeing {len(self.guilds)} guilds",
            f"Python version: {sys.version}",
            f"discord.py {discord.__version__} | jishaku {jishaku.__version__}",
            f"--------------------------------------------------------",
            f"\n",
            sep="\n",
        )

    async def start(self) -> None:
        return await super().start(DISCORD_TOKEN, reconnect=True)
