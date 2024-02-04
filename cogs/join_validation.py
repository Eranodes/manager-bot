import re

import discord
from discord.ext import commands

from bot import ManagerBot
from config import MAIN_GUILD


class JoinValidation(commands.Cog):
    @staticmethod
    def validate_displayname(input_str: str) -> bool:
        typable_characters = set(
            r"`~!@#$%^&*()-_=+[]\|;'\"',<>.?ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 "
        )
        for char in input_str:
            if char not in typable_characters:
                return False
        return True

    @staticmethod
    def strip_emojis(input_str: str) -> str:

        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+",
            flags=re.UNICODE,
        )

        return emoji_pattern.sub(r"", input_str)

    @staticmethod
    def dehoist_username(username, char="!") -> str:

        while username.startswith(char):
            username = username[1:]
        return username

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        if not member.guild.id == MAIN_GUILD:  # only check main guild
            return

        if not member.avatar:  # check if user has an avatar and if not kick them
            try:
                await member.send(
                    "You were kicked from **EraNodes - Freemium Hosting** because you __don't__ have an avatar.\n"
                    "Please add an avatar and try again.\n"
                    "\n"
                    "This is to avoid selfbots and raiders from joining our server."
                )
            except discord.errors.Forbidden:
                pass

            return await member.kick(reason="Missing avatar")

        stripped = self.strip_emojis(member.display_name.upper())
        if not self.validate_displayname(
            stripped
        ):  # check if display name is valid else decancer into @username
            await member.edit(nick=member.name)
        else:
            nick = self.dehoist_username(member.display_name)
            await member.edit(nick=nick)


async def setup(bot: ManagerBot):
    await bot.add_cog(JoinValidation(bot))
