import discord
import asqlite
from discord import app_commands
from discord.ext import commands

from bot import ManagerBot


class Invites(commands.Cog):
    def __init__(self, bot: ManagerBot) -> None:
        self.bot = bot

    async def get_invites(self, sender_id):
        async with self.bot.pool.acquire() as c:
            data = await c.fetchall(
                "SELECT invitee_id FROM invites WHERE sender_id = ?", (sender_id,)
            )
            print(data)
        return data

    @commands.command(name="invites")
    async def _invites(
        self, ctx: commands.Context, user: discord.Member = None
    ) -> None:
        data = await self.get_invites(user.id if user else ctx.author.id)
        await ctx.send(f"{[d[0] for d in data]}" if data else "No invites found")

    @commands.command(name="addinv")
    async def _addinv(
        self,
        ctx: commands.Context,
        user: discord.Member = None,
        inviter: discord.Member = None,
    ):
        print("got")
        async with self.bot.pool.acquire() as c:
            print("acquired")

            await c.execute(
                "INSERT INTO invites (sender_id, invitee_id) VALUES (?, ?)",
                (
                    user.id if user else ctx.author.id,
                    inviter.id if inviter else ctx.author.id,
                ),
            )
            print("executed")

        await ctx.send("updated")


async def setup(bot: ManagerBot) -> None:
    await bot.add_cog(Invites(bot))
