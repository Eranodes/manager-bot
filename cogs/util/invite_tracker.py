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

from datetime import datetime
import asyncio

from discord import AuditLogAction
import discord


class InviteTracker:

    def __init__(self, bot) -> None:
        self.bot = bot
        self._cache = {}
        self.add_listeners()

    async def set_invite_channel(self, channel_id: int):
        self.bot.invite_track_channel = await self.bot.fetch_channel(channel_id)

    @property
    def tracker_channel(self):
        return self.bot.invite_track_channel

    @property
    def cache(self):
        return self._cache

    def add_listeners(self):
        self.bot.add_listener(self.cache_invites, "on_ready")
        self.bot.add_listener(self.update_invite_cache, "on_invite_create")
        self.bot.add_listener(self.remove_invite_cache, "on_invite_delete")
        self.bot.add_listener(self.add_guild_cache, "on_guild_join")
        self.bot.add_listener(self.remove_guild_cache, "on_guild_remove")

    async def cache_invites(self):
        for guild in self.bot.guilds:
            try:
                self._cache[guild.id] = {}
                for invite in await guild.invites():
                    self._cache[guild.id][invite.code] = invite
            except discord.Forbidden:
                continue

    async def update_invite_cache(self, invite):
        if invite.guild.id not in self._cache.keys():
            self._cache[invite.guild.id] = {}
        self._cache[invite.guild.id][invite.code] = invite

    async def remove_invite_cache(self, invite):
        if invite.guild.id not in self._cache.keys():
            return
        ref_invite = self._cache[invite.guild.id][invite.code]
        if (
            (
                ref_invite.created_at.timestamp() + ref_invite.max_age
                > datetime.utcnow().timestamp()
                or ref_invite.max_age == 0
            )
            and ref_invite.max_uses > 0
            and ref_invite.uses == ref_invite.max_uses - 1
        ):
            try:
                async for entry in invite.guild.audit_logs(
                    limit=1, action=AuditLogAction.invite_delete
                ):
                    if entry.target.code != invite.code:
                        self._cache[invite.guild.id][ref_invite.code].revoked = True
                        return
                else:
                    self._cache[invite.guild.id][ref_invite.code].revoked = True
                    return
            except discord.Forbidden:
                self._cache[invite.guild.id][ref_invite.code].revoked = True
                return
        else:
            self._cache[invite.guild.id].pop(invite.code)

    async def add_guild_cache(self, guild):
        self._cache[guild.id] = {}
        for invite in await guild.invites():
            self._cache[guild.id][invite.code] = invite

    async def remove_guild_cache(self, guild):
        try:
            self._cache.pop(guild.id)
        except KeyError:
            return

    async def get_invites(self, sender_id):
        async with self.bot.pool.acquire() as c:
            data = await c.fetchall(
                "SELECT invitee_id FROM invites WHERE sender_id = ?", (sender_id,)
            )
            print(data)
        return data

    async def fetch_inviter(self, member):
        if not member:
            return None
        await asyncio.sleep(self.bot.latency)
        for new_invite in await member.guild.invites():
            for cached_invite in self._cache[member.guild.id].values():
                if (
                    new_invite.code == cached_invite.code
                    and new_invite.uses - cached_invite.uses == 1
                    or cached_invite.revoked
                ):
                    if cached_invite.revoked:
                        self._cache[member.guild.id].pop(cached_invite.code)
                    elif new_invite.inviter == cached_invite.inviter:
                        self._cache[member.guild.id][cached_invite.code] = new_invite
                    else:
                        self._cache[member.guild.id][cached_invite.code].uses += 1
                    return cached_invite.inviter
