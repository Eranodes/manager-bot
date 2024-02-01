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

import discord
from discord.ext import commands
from discord import app_commands

from .util.constants import EMOJIS


class UserWarn(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="siw")
    async def service_interrupt_warn(
        self, ctx: commands.Context, member: discord.Member, server_url: str
    ):
        # parse end of server url
        server_id = server_url.split("/")[-1]
        await member.send(
            f"""
🚨 **Server Suspension: Missing `hibernate.jar` Plugin**

Dear {member.mention},

Your server ([{server_id}]({server_url})) has been suspended due to the missing `hibernate.jar` plugin.
This plugin is crucial to maintain node performance.

To resolve this issue and reactivate your server, contact support for assistance through:
- A ticket here: <#1201061535200575599>

We understand the inconvenience this may cause and are here to assist you throughout this process.
If you require any guidance or support, please don't hesitate to contact us.

Thank you for your cooperation.

Best regards,
\\- __EraNodes Development & Maintenance Team__"""
        )

        await ctx.message.add_reaction(EMOJIS["yes"])


async def setup(bot: commands.Bot):
    await bot.add_cog(UserWarn(bot))
