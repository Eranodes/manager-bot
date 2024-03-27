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
from discord import app_commands
from discord.ext import commands

from bot import ManagerBot
from config import SUGGESTIONS_FORUM, ACCEPTED_TAG, DENIED_TAG, SUPPORT_ROLES


class Suggestions(commands.Cog):
    def __init__(self, bot: ManagerBot):
        self.bot = bot

    def can_mark_threads(self, interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.channel, discord.Thread):
            return False

        return interaction.channel.parent_id == SUGGESTIONS_FORUM and any(
            role.id in SUPPORT_ROLES for role in interaction.user.roles  # type: ignore
        )

    async def mark_status(
        self,
        user: discord.abc.User,
        thread: discord.Thread,
        accepted=False,
    ):
        status_tag: int = ACCEPTED_TAG if accepted else DENIED_TAG
        tags = thread.applied_tags

        if not any(tag.id == status_tag for tag in tags):
            tags.append(discord.Object(id=status_tag))  # type: ignore

        await thread.edit(
            locked=True,
            archived=True,
            applied_tags=tags[:5],
            reason=f"[MANAGER] Marked as {'accepted' if accepted else 'denied'} by {user} (ID: {user.id})",
        )

    async def respond(self, accepted: bool, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"{interaction.user.mention} marked {interaction.channel.mention} as **{'accepted' if accepted else 'denied'}**",  # type: ignore
        )
        await self.mark_status(
            accepted=accepted, thread=interaction.channel, user=interaction.user  # type: ignore
        )

    @app_commands.command(name="accept")
    async def accept(self, interaction: discord.Interaction):
        """Marks the suggestion as accepted"""

        try:
            assert isinstance(interaction.channel, discord.Thread)
        except AssertionError:
            return await interaction.response.send_message(
                "This is not a thread", ephemeral=True
            )

        if not self.can_mark_threads(interaction):
            return await interaction.response.send_message(
                "You do not have permission to close this thread", ephemeral=True
            )

        await self.respond(accepted=True, interaction=interaction)

    @app_commands.command(name="deny")
    async def deny(self, interaction: discord.Interaction):
        """Marks the suggestion as denied"""
        try:
            assert isinstance(interaction.channel, discord.Thread)
        except AssertionError:
            return await interaction.response.send_message(
                "This is not a thread", ephemeral=True
            )

        if not self.can_mark_threads(interaction):
            return await interaction.response.send_message(
                "You do not have permission to close this thread", ephemeral=True
            )

        await self.respond(accepted=False, interaction=interaction)


async def setup(bot: ManagerBot):
    await bot.add_cog(Suggestions(bot))
