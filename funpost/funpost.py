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
# ?magic8ball

class Misc(commands.Cog):
    """Funpost Plugin"""
    def __init__(self, bot):
        self.bot = bot
        self.footer = "coming from jej's spaghetti code 🍝"

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

    # Magic 8 Ball
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(aliases=['8ball', 'ball'])
    async def magic8ball(self, ctx, *, text):
        
        '''Ask the magic Seele~'''

        num = random.randint(0, 9)
        
        titles = [
            'Seele has decided..',
            'Seele is choosing..',
            'Seele has thought about this..',
            '"Seele" has picked this for you..'
        ]

        embed = discord.Embed(
            title = f'{titles[random.randint(0, len(titles)-1)]}',
            colour = discord.Colour.random()
        )

        embed.add_field(name='Question', value=text)
        embed.set_footer(text=self.footer)

        with open('plugins/Meliodas245/mm-plugins/funpost-master/8ball.json') as f:
            ans = json.load(f)

        if num >= 6 and num<= 9:
            x = random.randint(0,len(ans[0]['positive']) - 1)
            embed.set_thumbnail(url="https://img-os-static.hoyolab.com/communityWeb/upload/c4422f55fa7b4596174a0e2568e50d4b.png")
            embed.add_field(name='Answer', value=f":8ball: {ans[0]['positive'][x]}", inline=False)
            await ctx.send(embed=embed)
        
        elif num >= 3 and num < 6:
            y = random.randint(0,len(ans[1]['neutral']) - 1)
            embed.set_thumbnail(url="https://img-os-static.hoyolab.com/communityWeb/upload/e92fbe1a02852189373f0c0f48f9fe5b.png")
            embed.add_field(name='Answer', value=f":8ball: {ans[1]['neutral'][y]}", inline=False)
            await ctx.send(embed=embed)
        
        elif num >= 0 and num < 3:
            z = random.randint(0,len(ans[2]['negative']) - 1)
            embed.set_thumbnail(url="https://img-os-static.hoyolab.com/communityWeb/upload/19dacf2bf7dad6cea3b4a1d8d68045a0.png")
            embed.add_field(name='Answer', value=f":8ball: {ans[2]['negative'][z]}", inline=False)
            await ctx.send(embed=embed)
            
async def setup(bot):
    await bot.add_cog(Misc(bot))
