from typing import List

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

CHANNEL_ID = 896989898526052373
CODES_ROLE_ID = 1086580742378770442


class AnnounceCodes(commands.Cog):
    """Quickly announce HSR codes"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["ac", "announcecode"])
    @commands.cooldown(rate=2, per=60)
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def announcecodes(self, ctx: commands.Context, *codes):
        """Announce HSR gift code(s) quickly.

        Codes are separated by spaces after the command, and are automatically capitalized.

        You can add additional info (e.g. what the code gives) by putting it after a colon after the code.
        If the additional info includes a space, you NEED to surround the ENTIRE segment in double-quotes. For example:
        `?announcecodes "FOOBAR1:60xStellar Jade, 10xCoins" FOOBAR2 FOOBAR3`
        """
        codes: List[str]
        if len(codes) > 25:
            return await ctx.reply("You can only post up to 25 codes at once.")

        channel = self.bot.get_channel(CHANNEL_ID)
        embed = discord.Embed(
            title=f"New HSR Gift Code{'s' if len(codes) > 1 else ''}!",
            description="You can quickly redeem a code by pressing the respective button below. "
                        "Alternatively, you can manually redeem by copying the codes in the embed. "
                        "To copy a code on mobile, tap and hold the code itself.",
            colour=0x7a7dfd
        )
        view = discord.ui.View()
        for num, code in enumerate(codes):
            name = f"Code {num + 1}"
            if ":" in code:
                code, name = code.split(":", 1)
            if not code.isalnum():
                return await ctx.reply(
                    f"The code *`{code.replace('`', '[backtick]')}`* doesn't look right, "
                    f"please double-check that your command formatting is correct!"
                )
            code = code.upper()
            embed.add_field(name=name, value=code, inline=False)
            view.add_item(discord.ui.Button(
                label=f"Redeem {name}", style=discord.ButtonStyle.url,
                url=f"https://hsr.hoyoverse.com/gift?code={code}"
            ))
        msg = await ctx.reply("Announcing...")
        await channel.send(content=f"<@&{CODES_ROLE_ID}>", embed=embed, view=view)
        await msg.edit(content="Codes have been announced")


async def setup(bot):
    await bot.add_cog(AnnounceCodes(bot))
