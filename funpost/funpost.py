import asyncio
import json
import random

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
HETERO_ROLE = 1108845861305339995
GAY_ROLE = 1108845603338846339
EIGHT_BALL_TITLES = [
    'Seele has decided..',
    'Seele is choosing..',
    'Seele has thought about this..',
    '"Seele" has picked this for you..'
]
SHIP_CHANNELS = {
    "starch": 1101776593422127144,
    "brsl": 1101627790492708984,
    "kafhime": 1103593594440396810
}


async def fetch_yuri_messages(bot: commands.Bot, channel_id: int, ship: str) -> int:
    """Fetch and save all yuri images from a Discord channel

    :param bot: Discord commands.Bot instance
    :param channel_id: Channel to fetch images from
    :param ship: What ship the images are of
    :return: Number of messages fetched
    """
    channel = bot.get_channel(channel_id)
    if channel:
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            if message.embeds and message.type != discord.MessageType.reply and 'tenor.com' not in message.content:
                messages.append(message.content)

        messages = list(set(messages))  # Make sure messages is unique

        file_name = f'plugins/Meliodas245/mm-plugins/funpost-master/links_{ship}.json'

        # Get the current links
        with open(file_name, 'r') as f:
            url = json.load(f)

        extractor = URLExtract()
        for link in messages:
            if link != '':
                url[f'url{len(url)}'] = extractor.find_urls(link, with_schema_only=True)[0]  # Only extract the link
        with open(file_name, 'w') as f:
            json.dump(url, f, indent=4)

        return len(messages)
    else:
        return 0


# --------------------------------------------------------------------------------------------------------------------------------

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
            title=f"The 🏳️‍🌈 has decided...",
            description=f"{member.nick if member.nick else member.name} is **{num}%** gae.",
            colour=discord.Colour.random()
        )
        embed.set_thumbnail(url=random.choice(GAY_STICKERS))

        # funi footer if anyone gets either
        if num == 0:
            embed.set_footer(text=f'[{member.nick} is now a Certified Hetero]')
            role = discord.utils.get(ctx.guild.roles, id=HETERO_ROLE)
            await member.add_roles(role)
        elif num == 100:
            embed.set_footer(text=f'[{member.nick} is now a Certified Gay]')
            role = discord.utils.get(ctx.guild.roles, id=GAY_ROLE)
            await member.add_roles(role)

        await ctx.send(embed=embed)

    # Magic 8 Ball
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(aliases=['8ball', 'ball'])
    async def magic8ball(self, ctx: commands.Context, *, text: str):
        """Ask the magic Seele~"""

        num = random.randint(0, 9)

        with open('plugins/Meliodas245/mm-plugins/funpost-master/8ball.json') as f:
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

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command(name='fetchYuri', aliases=['yurifetch', 'fetchyuri', 'fetchgay'])
    async def fetch_yuri_command(self, ctx: commands.Context, *, ship="brsl"):
        """Fetched the links in the relative ship thread, only run this once (ever)"""
        if ship not in SHIP_CHANNELS:
            return await ctx.reply(
                'specify the ship to fetch as ' + ", ".join([f"`{i}`" for i in SHIP_CHANNELS.keys()]))
        channel_id = SHIP_CHANNELS[ship]

        with ctx.typing():
            # Fetch the links
            file_name = f'plugins/Meliodas245/mm-plugins/funpost-master/links_{ship}.json'
            with open(file_name, 'r') as f:
                url = json.load(f)

            if len(url) <= 1:
                message_count = await fetch_yuri_messages(self.bot, channel_id, ship)
                await ctx.reply(f'fetched {message_count} {ship} links')
            else:
                await ctx.reply(f'already fetched {ship}, new messages are automatically fetched')

    # Yuri
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(name='Yuri', aliases=['yuri'])
    async def Yuri(self, ctx, *, ship="all"):
        """Sends a random yuri art, default is a random ship"""
        if ship == 'steven':
            ship = 'starch'
        elif ship == "all":
            ship = random.choice(list(SHIP_CHANNELS.keys()))

        file_name = f'plugins/Meliodas245/mm-plugins/funpost-master/links_{ship}.json'
        try:
            with open(file_name, 'r') as f:
                links = json.load(f)

            # Convert to list and store it to links_list
            links_list = list(links)
            if len(links_list) > 0:
                url = random.choice(links_list)
                await ctx.reply(links[url])
            else:
                await ctx.reply(f'not data fetched')  # just in case
        except FileNotFoundError:
            await ctx.reply(f'try writing the ships like: ' + ", ".join([f"`{i}`" for i in SHIP_CHANNELS.keys()]))

    # Yuri + Commands Archive
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def archive(self, ctx: commands.Context):
        """Archives the json files"""
        files = [discord.File('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json')] + [
            discord.File(f"plugins/Meliodas245/mm-plugins/funpost-master/links_{i}.json") for i in SHIP_CHANNELS.keys()
        ]
        await ctx.reply(files=files)

    # Listener to autofetch yuri from thread
    # I don't want to fix this again -jej
    @commands.Cog.listener("on_message")
    async def food(self, message):
        # Check if the message is from one of the threads aforementioned
        if message.channel.id in SHIP_CHANNELS.values():
            await asyncio.sleep(1.5)  # not noice
            if message.embeds and message.type != discord.MessageType.reply and 'tenor.com' not in message.content:
                # Get the corresponding JSON file name

                file_name = ""
                for ship, id_ in SHIP_CHANNELS.items():
                    if message.channel.id == id_:
                        file_name = f"plugins/Meliodas245/mm-plugins/funpost-master/links_{ship}.json"
                        break

                # fetch the content of the message
                try:
                    with open(file_name, 'r') as f:
                        url = json.load(f)
                except FileNotFoundError:  # just in case again
                    url = {}

                # Extract only the urls
                extractor = URLExtract()

                # Ignores the comments (i hope)
                with open(file_name, 'w') as f:
                    if message.content != '':
                        url[f'url{len(url)}'] = extractor.find_urls(message.content, with_schema_only=True)[0]
                        json.dump(url, f, indent=4)

                # Twitter verification checkmark :yello:
                await message.add_reaction('✅')


async def setup(bot):
    await bot.add_cog(Misc(bot))
