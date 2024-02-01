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

"""For support thread management"""

import discord
from discord import app_commands
from discord.ext import commands

from bot import ManagerBot
from .util.constants import EMOJIS
from config import SOLVED_TAG, SUPPORT_FORUM


class Support(commands.Cog):
    """For support thread management"""

    def __init__(self, bot: ManagerBot):
        self.bot = bot

    def can_close_threads(self, interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.channel, discord.Thread):
            return False

        permissions = interaction.channel.permissions_for(interaction.user)
        return interaction.channel.parent_id == SUPPORT_FORUM and (
            permissions.manage_threads
            or interaction.channel.owner_id == interaction.user.id
        )

    async def mark_as_solved(
        self, thread: discord.Thread, user: discord.abc.User
    ) -> None:
        tags = thread.applied_tags

        if not any(tag.id == SOLVED_TAG for tag in tags):
            tags.append(discord.Object(id=SOLVED_TAG))

        await thread.edit(
            locked=True,
            archived=True,
            applied_tags=tags[:5],
            reason=f"Marked as solved by {user} (ID: {user.id})",
        )

    @app_commands.command(name="solved")
    async def solved(self, interaction: discord.Interaction):
        """Marks the support thread as solved"""
        try:
            assert isinstance(interaction.channel, discord.Thread)
        except AssertionError:
            return await interaction.response.send_message(
                "This is not a thread", ephemeral=True
            )

        if not self.can_close_threads(interaction):
            return await interaction.response.send_message(
                "You do not have permission to close this thread", ephemeral=True
            )

        await interaction.response.send_message(
            f"{interaction.user.mention} marked {interaction.channel.mention} as solved ✅",
            ephemeral=True,
        )
        await self.mark_as_solved(interaction.channel, interaction.user)

    @app_commands.command(name="iis")
    async def iis(self, interaction: discord.Interaction):
        """Is it solved?"""
        await interaction.response.send_message(
            f"If you're satisfied with the response, please mark it as solved using `/solved` <:fwog:1201046667701518436>\n"
        )
        msg = await interaction.original_response()
        await msg.add_reaction(EMOJIS["yes"])


async def setup(bot: ManagerBot):
    await bot.add_cog(Support(bot))
