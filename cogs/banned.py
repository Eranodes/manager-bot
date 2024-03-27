import discord
from discord.ext import commands

from bot import ManagerBot
from config import MAIN_GUILD, YET_TO_APPEAL_ROLE, PETETIONS_GUILD


class Banned(commands.Cog):
    def __init__(self, bot: ManagerBot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_member_ban")
    async def add_role_in_petetions(self, guild: discord.Guild, member: discord.Member):
        if not guild.id == MAIN_GUILD:
            return

        petetions_guild = self.bot.get_guild(PETETIONS_GUILD)
        role = petetions_guild.get_role(YET_TO_APPEAL_ROLE)

        if isinstance(member, discord.User):
            member = petetions_guild.get_member(member.id)

        if not member:
            return

        try:
            await member.add_roles(role)
        except discord.Forbidden:
            pass

    @commands.Cog.listener("on_member_unban")
    async def remove_role_in_petetions(
        self, guild: discord.Guild, member: discord.Member
    ):
        if not guild.id == MAIN_GUILD:
            return

        petetions_guild = self.bot.get_guild(PETETIONS_GUILD)
        role = petetions_guild.get_role(YET_TO_APPEAL_ROLE)

        if isinstance(member, discord.User):
            member = petetions_guild.get_member(member.id)

        if not member:
            return

        try:
            await member.remove_roles(role)
        except discord.Forbidden:
            pass


async def setup(bot: ManagerBot):
    await bot.add_cog(Banned(bot))
