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
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def announcecodes(self, ctx: commands.Context, *codes):
        """Announce HSR gift code(s) quickly. Codes are separated by spaces after the command"""
        codes: list[str]
        if len(codes) > 25:
            return await ctx.reply("You can only post up to 25 codes at once.")

        channel = self.bot.get_channel(CHANNEL_ID)
        embed = discord.Embed(
            title="New HSR Gift Codes!",
            description="To copy a code on mobile, tap and hold the code itself.",
            colour=0x7a7dfd
        )
        for num, code in enumerate(codes):
            embed.add_field(name=f"Code {num + 1}", value=code.upper(), inline=False)

        msg = await ctx.reply("Announcing...")
        await channel.send(content=f"<@&{CODES_ROLE_ID}>", embed=embed, view=discord.ui.View().add_item(
            discord.ui.Button(label="Redeem Page", style=discord.ButtonStyle.url,
                              url="https://hsr.hoyoverse.com/gift")))
        await msg.edit(content="Codes have been announced")


async def setup(bot):
    await bot.add_cog(AnnounceCodes(bot))
