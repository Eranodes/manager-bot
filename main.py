"""
A Helper/Management bot for the official EraNodes discord server.
Copyright (c) 2023-present Ritam Das

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Repository:
    https://github.com/EraNodes/manager-bot
"""

import asyncio

from bot import ManagerBot


async def start():
    async with ManagerBot() as bot:
        await bot.start()


if __name__ == "__main__":
    asyncio.run(start())
