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


from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot import ManagerBot
from config import MAIN_GUILD
from .util.constants import EMOJIS, PRIMARY_COLOR
from .util.paginator import CustomPaginator


class InvitesPaginator(CustomPaginator):
    def __init__(
        self,
        *,
        entries: List,
        per_page: int = 10,
        clamp_pages: bool = True,
        target,
        timeout=180,
        bot: ManagerBot,
    ) -> None:
        self.bot = bot

        super().__init__(
            entries=entries,
            per_page=per_page,
            clamp_pages=clamp_pages,
            target=target,
            timeout=timeout,
        )

    def format_page(self, entries, /) -> discord.Embed:
        """Formatting provided for embed for current page"""

        desc = ""

        for data in entries:
            # data = [int, {int: int}]

            position = data[0] + 1
            sender, count = list(data[1].items())[0]

            sender_mention = self.bot.get_user(sender).mention

            desc += f"`{position}.` {sender_mention}: **{count}** invites\n"

        return discord.Embed(
            title="EraNodes Invites Leaderboard",
            color=PRIMARY_COLOR,
            description=desc,
        )


class Invites(commands.GroupCog, name="invites"):
    def __init__(self, bot: ManagerBot) -> None:
        self.bot = bot
        self.invite_channel = self.bot.invite_tracker.tracker_channel

    @app_commands.command(name="leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """View top inviters"""
        await interaction.response.defer(thinking=True)

        async with self.bot.pool.acquire() as c:
            data = await c.fetchall("SELECT sender_id, invitee_id FROM invites")

        sender_invitations_count = {}

        # Iterate through the sender counts and get the senders per invitee
        for row in data:
            sender, invitee = row
            if sender not in sender_invitations_count:
                sender_invitations_count[sender] = 0
            sender_invitations_count[sender] += 1

        invite_counts = []

        # return position index and dict of senderid:count
        for position, (sender, count) in enumerate(
            sorted(sender_invitations_count.items(), key=lambda x: x[1], reverse=True)
        ):
            invite_counts.append([position, {sender: count}])

        paginator = InvitesPaginator(
            bot=self.bot,
            entries=invite_counts,
            target=interaction,
        )
        embed = await paginator.embed()
        await interaction.followup.send(embed=embed, view=paginator)

    @app_commands.command(name="view")
    async def invites(
        self, interaction: discord.Interaction, user: Optional[discord.Member]
    ):
        # numpy style docstrings
        """
        View invites of a user

        """
        if not user:
            user = interaction.user

        async with self.bot.pool.acquire() as c:
            data = await c.fetchall(
                "SELECT invitee_id FROM invites WHERE sender_id = ?",
                (user.id,),
            )
        if not data:
            await interaction.response.send_message(
                f"**{user.name}** has not invited anyone."
            )
            return

        await interaction.response.send_message(
            f"**{user.name}** has invited **{len(data)}** users."
        )

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        if not member.guild.id == MAIN_GUILD:  # only check main guild
            return

        # check if user is a bot and was invited through oauth
        if member.bot:
            await self.invite_channel.send(
                f"{EMOJIS['white_plus']} **{member}** was added via OAuth2.",
            )
            return

        inviter = await self.bot.invite_tracker.fetch_inviter(member)
        if not inviter:  # check if inviter was found
            await self.invite_channel.send(
                f"{EMOJIS['white_plus']} **{member.name}** joined. I don't know who invited them.",
            )
            return

        async with self.bot.pool.acquire() as c:
            # check if user is in db
            data = await c.fetchall(
                "SELECT invitee_id FROM invites WHERE sender_id = ?", (inviter.id,)
            )
            if member.id in [d[0] for d in data]:
                raise ValueError("User already in invites")

            # add invitee & sender to db
            invites = await c.fetchall(
                "INSERT INTO invites (sender_id, invitee_id) VALUES (?, ?)",
                (inviter.id, member.id),
            )

        await self.invite_channel.send(
            f"{EMOJIS['white_plus']} **{member.name}** was invited by **{inviter.name}**.",
        )

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        if not member.guild.id == MAIN_GUILD:  # only check main guild
            return

        async with self.bot.pool.acquire() as c:
            data = await c.fetchone(
                "SELECT invitee_id, sender_id FROM invites WHERE invitee_id = ?",
                (member.id,),
            )

            await c.execute("DELETE FROM invites WHERE invitee_id = ?", (member.id,))

            if not data:

                await self.invite_channel.send(
                    f"{EMOJIS['white_minus']} **{member.name}** left. I don't know who invited them."
                )
                return

            inviter = self.bot.get_user(data[1])
            await self.invite_channel.send(
                f"{EMOJIS['white_minus']} **{member.name}** left. They were invited by **{inviter.name}**.",
            )


async def setup(bot: ManagerBot) -> None:
    await bot.add_cog(Invites(bot))
