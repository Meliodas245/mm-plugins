import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(member):
        channel = discord.utils.get(member.guild.channels, name='welcome-channel')
        if channel is not None:
            embed = discord.Embed(
                title=f"Welcome to our server, {member.name}!",
                description=f"Thanks for joining our community, {member.name}!",
                color="0x00ff00"
            )
            embed.set_thumbnail(url=member.avatar_url)

            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))