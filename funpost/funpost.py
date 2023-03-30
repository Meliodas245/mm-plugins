import discord
import random
import json
from discord.ext import commands
from urllib.request import urlopen
from core import checks
from core.models import PermissionLevel

# List of commands here:
# ?advice
# ?gaydar
# ?yatta

class Misc(commands.Cog):
    """Funpost Plugin"""
    def __init__(self, bot):
        self.bot = bot
        self.footer = "Coming from jej's spaghetti code 🍝"

    # Advice
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command()
    async def advice(self, ctx):

        '''Have a random slip of advice~'''
        
        url = "https://api.adviceslip.com/advice"

        r = urlopen(url)
        adv = json.loads(r.read().decode('utf-8'))

        embed = discord.Embed(
            title = f"Have a random slip of advice~",
            description = f"{adv['slip']['advice']}",
            colour = discord.Colour.random()
        )

        embed.set_thumbnail(url="https://upload-os-bbs.hoyolab.com/upload/2022/08/24/fbfc78ea104a8a3294edbb04352138fb_2018653294500640692.png")
        
        await ctx.send(embed=embed)

    # Gaydar
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command()
    async def gaydar(self, ctx, member: commands.MemberConverter):

        '''🌈?'''

        # self rate
        if member is None:
            member = ctx.author
        
        num = random.randint(1, 10001)/100

        embed = discord.Embed(
            title = f"The 🏳️‍🌈 has decided...",
            description = f"{member.name} is **{num}%** gae.",
            colour = discord.Colour.random()
        )
        
        embed.set_thumbnail(url="https://upload-bbs.mihoyo.com/upload/2022/06/12/2f55e1f199efc29f3c4e9076d3288365_7013897107954424230.png")
        embed.set_footer(text=self.footer)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Misc(bot))