import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.channels, id=896803126542229534)
        if channel is not None:
            embed = discord.Embed(
                title=f"Welcome to our server, {member.name}!",
                description=f"Thanks for joining our community, {member.name}!",
                colour = discord.Colour.from_rgb(191, 255, 0)
            )
            embed.set_thumbnail(url=member.display_avatar)

            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
