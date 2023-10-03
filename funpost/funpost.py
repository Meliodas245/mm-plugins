import asyncio
import json
import random
from os.path import dirname, exists

import discord
from discord.ext import commands
from urlextract import URLExtract

from core import checks
from core.models import PermissionLevel

# List of commands here:
# ?gaydar
# ?magic8ball
# ?fetchYuri
# ?yuri

DIR = dirname(__file__)
GAY_STICKERS = [
    "https://static.wikia.nocookie.net/houkai-star-rail/images/d/db/Arlan_Sticker_01.png/revision/latest?cb=20230505074117",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/4/47/Asta_Sticker_01.png/revision/latest?cb=20230505074119",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/6/6a/Bailu_Sticker_02.png/revision/latest?cb=20230420184826",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/d/d4/Caelus_Sticker_02.png/revision/latest?cb=20230420195451",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/5/5c/Stelle_Sticker_02.png/revision/latest?cb=20230420195524",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/2/22/Dan_Heng_Sticker_01.png/revision/latest?cb=20230505074120",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/2/26/Herta_Sticker_01.png/revision/latest?cb=20230505074121",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/4/45/Himeko_Sticker_01.png/revision/latest?cb=20230505074123",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/c/c7/Jing_Yuan_Sticker_02.png/revision/latest?cb=20230420194038",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/6/6e/Kafka_Sticker_01.png/revision/latest?cb=20230505074126",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/2/28/Silver_Wolf_Sticker_01.png/revision/latest?cb=20230505074135",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/1/12/March_7th_Sticker_05.png/revision/latest?cb=20220425065144",
    "https://static.wikia.nocookie.net/houkai-star-rail/images/5/5f/Serval_Sticker_01.png/revision/latest?cb=20230505074134"
]
EIGHT_BALL_TITLES = [
    'Ruan Mei has calculated..',
    'Ruan_Mei.exe outputs..',
    'Ruan Mei has thought about this..'
]

class Misc(commands.Cog):
    """Funpost Plugin"""

    def __init__(self, bot):
        self.bot = bot
        self.footer = ""  # TODO: REPLACE ME

    # Gaydar
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(aliases=['gay', 'gae', 'gayrate'])
    async def gaydar(self, ctx: commands.Context, member: commands.MemberConverter = None):
        """🌈?"""
        if member is None:
            member = ctx.author

        num = random.randrange(10001) / 100

        embed = discord.Embed(
            title=f"The Genius Society has decided...",
            description=f"{member.display_name} is **{num}%** gae.",
            colour=discord.Colour.random()
        )
        embed.set_thumbnail(url=random.choice(GAY_STICKERS))

        # funi footer if anyone gets either
        if num == 0:
            embed.set_footer(text=f'[{member.display_name} is now a Certified Hetero]')
            role = discord.utils.get(ctx.guild.roles, id=HETERO_ROLE)
        elif num == 100:
            embed.set_footer(text=f'[{member.display_name} is now a Certified Gay]')
            role = discord.utils.get(ctx.guild.roles, id=GAY_ROLE)

        await ctx.send(embed=embed)

    # Magic 8 Ball
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(aliases=['8ball', 'ball'])
    async def magic8ball(self, ctx: commands.Context, *, text: str):
        """Ask the magic Seele~"""

        num = random.randint(0, 9)

        with open(f'{DIR}/8ball.json') as f:
            ans = json.load(f)

        if num < 3:
            thumbnail = "https://img-os-static.hoyolab.com/communityWeb/upload/19dacf2bf7dad6cea3b4a1d8d68045a0.png"
            emote = discord.utils.get(ctx.guild.emojis, id=1085605320065302630)
            answer = random.choice(ans[2]["negative"])
        elif num < 6:
            thumbnail = "https://img-os-static.hoyolab.com/communityWeb/upload/e92fbe1a02852189373f0c0f48f9fe5b.png"
            emote = discord.utils.get(ctx.guild.emojis, id=1085593631584432178)
            answer = random.choice(ans[1]["neutral"])
        elif num < 10:
            thumbnail = "https://img-os-static.hoyolab.com/communityWeb/upload/c4422f55fa7b4596174a0e2568e50d4b.png"
            emote = discord.utils.get(ctx.guild.emojis, id=1087154553255895040)
            answer = random.choice(ans[0]["positive"])
        else:  # Easter egg
            thumbnail = "https://s3.blankdvth.com/74b72448-f31f-4d85-a765-fa04bca84edd.jpg"
            emote = "🐛"
            answer = f"You've won, you've done the impossible. Contact the bot devs to see them become confused. (`{num}`)"

        embed = discord.Embed(
            title=random.choice(EIGHT_BALL_TITLES),
            colour=discord.Colour.random()
        )

        embed.add_field(name='Question', value=text)
        embed.set_footer(text=self.footer)
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name="Answer", value=f"{emote} {answer}", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Misc(bot))
