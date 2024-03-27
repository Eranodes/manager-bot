import asyncio
import re
from typing import Optional
import io

import discord
from discord.ext import commands

from bot import ManagerBot
from config import MAIN_GUILD


class Validation(commands.Cog):
    @staticmethod
    def validate_name(member: discord.Member) -> Optional[str]:
        input_str: str = member.display_name

        # Remove leading symbols
        bad_chars: str = "!@#$%^&*()_+-=[]{}`~|;:,.<>?/'\"\\"
        cleaned_name: str = input_str.lstrip(bad_chars).strip()

        # Remove emojis
        cleaned_name: str = (
            cleaned_name.encode("ascii", "ignore").decode("ascii").strip()
        )

        # Check if only contains letters of the English alphabet
        no_symbols: str = "".join(c for c in cleaned_name if c not in bad_chars).strip()
        if re.match("^[a-zA-Z0-9 ]+$", no_symbols):
            if len(cleaned_name) <= 3:
                return member.name

            return cleaned_name

        return member.name

    async def name_change_warn(self, user: discord.Member, name: str):
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(label=f"Sent from {user.guild!s}", disabled=True)
        )

        try:
            await user.edit(nick=name, reason="Decancered name to follow ruleset.")
            await user.send(
                f"You nickname has been changed to `{name}`\n"
                f"We do not support emojis, special characters or hoisting characters.\n\n"
                f"__This was done automatically by this bot.__\n",
                view=view,
            )
        except discord.Forbidden:
            pass

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        if not member.guild.id == MAIN_GUILD:
            return

        name = self.validate_name(member)
        if name != member.display_name:
            await self.name_change_warn(member, name)

    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not before.guild.id == MAIN_GUILD:
            return

        # check if nickname was changed or display name was changed
        if before.display_name != after.display_name or before.nick != after.nick:
            name = self.validate_name(after)
            if name != after.display_name:
                await self.name_change_warn(after, name)

    @commands.command(name="validate")
    @commands.is_owner()
    async def validate(self, ctx, member: discord.Member):
        name = self.validate_name(member)
        if name != member.display_name:
            await ctx.send("Done!")
            await member.edit(nick=name, reason="Decancered name to follow ruleset.")
        else:
            await ctx.send(f"{member} is fine!")

    @commands.command(name="validate-all")
    @commands.is_owner()
    async def validate_all(self, ctx: commands.Context):
        valid = []
        no_change = []

        all_members = ctx.guild.members

        await ctx.send("Validating all members...")
        for member in all_members:
            name = self.validate_name(member)
            if name != member.display_name:
                await member.edit(
                    nick=name, reason="Decancered name to follow ruleset."
                )
                valid.append(member.name)
                await ctx.send(f"Validated {member!s}")
                await asyncio.sleep(0.5)
            else:
                no_change.append(member.name)

        end_text = (
            "Validated: " + ", ".join(valid) + "\nNo Change: " + ", ".join(no_change)
        )

        # turn end_text to file io bytestream
        file = io.BytesIO(end_text.encode("utf-8"))
        file.seek(0)
        await ctx.send(file=discord.File(file, filename="validation.txt"))


async def setup(bot: ManagerBot):
    await bot.add_cog(Validation(bot))
