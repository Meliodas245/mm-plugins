import discord
import random
import json
import asyncio
from urlextract import URLExtract
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

# List of commands here:
# ?gaydar
# ?magic8ball
# ?fetchYuri
# ?yuri

#Yuri command fetch function idk if this can be relocated in another part of the code :)  - ChoZix
#--------------------------------------------------------------------------------------------------------------------------------
async def fetch_yuri_messages(bot, channel_id, ship):
    channel = bot.get_channel(channel_id)
    if channel:
        messages = []
        async for message in channel.history(limit=None, oldest_first = True):
            if message.embeds and message.type != discord.MessageType.reply and 'tenor.com' not in message.content:
                messages.append(message.content)
        
        # UNIQUE MESSAGES
        messages = list(set(messages))

        file_name = f'plugins/Meliodas245/mm-plugins/funpost-master/links_{ship}.json'

        # Fetch the links
        with open(file_name, 'r') as f:
            url = json.load(f)

        # Extract only the urls
        extractor = URLExtract()

        # Write to file
        for link in messages:
            with open(file_name, 'w') as f:
                if link != '':
                    url[f'url{len(url)}'] = extractor.find_urls(link, with_schema_only=True)[0]
                    json.dump(url, f, indent=4)
        
        return len(messages)
    
    else:
        return 0
#--------------------------------------------------------------------------------------------------------------------------------

class Misc(commands.Cog):
    
    """Funpost Plugin"""
    
    def __init__(self, bot):
        self.bot = bot

    # Gaydar
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(aliases=['gay', 'gae', 'gayrate'])
    async def gaydar(self, ctx, member: commands.MemberConverter = None):

        '''🌈?'''
        
        # self rate (actually works)
        if member is None:
            member = ctx.author

        num = random.randrange(10001)/100

        embed = discord.Embed(
            title = f"The 🏳️‍🌈 has decided...",
            description = f"{member.nick if member.nick else member.name} is **{num}%** gae.",
            colour = discord.Colour.random()
        )
        
        # why isn't there an official seele one or bronya, i couldn't find :skull: -jej
        stickers = [
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

        embed.set_thumbnail(url=random.choice(stickers))
        
        # funi footer if anyone gets either
        if num == 0:
            embed.set_footer(text=f'[{member.nick} is now a Certified Hetero]')
        elif num == 100:
            embed.set_footer(text=f'[{member.nick} is now a Certified Homosexual]')
        
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
            seele_smug = discord.utils.get(ctx.guild.emojis, id=1087154553255895040)
            x = random.randint(0,len(ans[0]['positive']) - 1)
            embed.set_thumbnail(url="https://img-os-static.hoyolab.com/communityWeb/upload/c4422f55fa7b4596174a0e2568e50d4b.png")
            embed.add_field(name='Answer', value=f"{seele_smug} {ans[0]['positive'][x]}", inline=False)
            await ctx.send(embed=embed)
        
        elif num >= 3 and num < 6:
            seele_acid = discord.utils.get(ctx.guild.emojis, id = 1085593631584432178)
            y = random.randint(0,len(ans[1]['neutral']) - 1)
            embed.set_thumbnail(url="https://img-os-static.hoyolab.com/communityWeb/upload/e92fbe1a02852189373f0c0f48f9fe5b.png")
            embed.add_field(name='Answer', value=f"{seele_acid} {ans[1]['neutral'][y]}", inline=False)
            await ctx.send(embed=embed)
        
        elif num >= 0 and num < 3:
            seele_omg = discord.utils.get(ctx.guild.emojis, id = 1085605320065302630)
            z = random.randint(0,len(ans[2]['negative']) - 1)
            embed.set_thumbnail(url="https://img-os-static.hoyolab.com/communityWeb/upload/19dacf2bf7dad6cea3b4a1d8d68045a0.png")
            embed.add_field(name='Answer', value=f"{seele_omg} {ans[2]['negative'][z]}", inline=False)
            await ctx.send(embed=embed)
            
    # Yuri commands
    
    # fetch messages from threads
    
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command(name='fetchYuri',aliases = ['yurifetch','fetchyuri','fetchgay'])
    async def fetch_yuri_command(self, ctx, *, ship="brsl"):
        
        '''Fetched the links in the relative ship thread, only can be run once.'''
        
        channel_id = None
       
        if ship == "starch":
            channel_id = 1101776593422127144 # STARCH
        elif ship == "brsl":
             channel_id = 1101627790492708984 # BRONSEELE
        elif ship == "kafhime":
             channel_id = 1103593594440396810 # KAFHIME
        
        if channel_id:
            # PREVENT DUPLICATION
            # Fetch the links
            file_name = f'plugins/Meliodas245/mm-plugins/funpost-master/links_{ship}.json'
            with open(file_name, 'r') as f:
                url = json.load(f)

            if len(url) <= 1:
                message_count = await fetch_yuri_messages(self.bot, channel_id, ship)
                await ctx.reply(f'fetched {message_count} {ship} links')
            
            else:
                await ctx.reply(f'already fetched {ship}, new messages are automatically fetched')
        
        else:
            await ctx.reply('specify the ship to fetch as `brsl`, `starch` or `kafhime`')
    
    # Yuri
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(name='Yuri', aliases=['yuri'])
    async def Yuri(self, ctx, *, ship="all"):
        
        '''Sends a random yuri art, default is both ships, ships: brsl, starch'''
        if ship == 'steven':
            ship = 'starch'
        
        if ship == "all":
            num = random.randint(0,2)
            # starch True ship
            if num == 0:
                ship = 'starch'
            elif num == 1:
                ship = 'brsl'
            else:
                ship = 'kafhime'
        
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
                await ctx.reply(f'not data fetched') # just in case
        
        except FileNotFoundError:
            await ctx.reply(f'try writing the ships like: "brsl", "starch" or "kafhime"')
    
    # Yuri + Commands Archive
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def archive(self, ctx, *, ship="brsl"):
        
        '''Archives the json files'''
        
        files = [ 
        discord.File('plugins/Meliodas245/mm-plugins/funpost-master/links_brsl.json'),
        discord.File('plugins/Meliodas245/mm-plugins/funpost-master/links_starch.json'),
        discord.File('plugins/Meliodas245/mm-plugins/funpost-master/links_kafhime.json'),
        discord.File('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json')
        ]
        await ctx.reply(files=files)

    # Listener to autofetch yuri from thread
    # I dont want to fix this again -jej
    @commands.Cog.listener("on_message")
    async def food(self,message):
        #Set thread's ids (same as fetch_yuri_command)
        bot_dev_food = [
            1101776593422127144, # STARCH
            1101627790492708984, # BRONSEELE
            1103593594440396810  # KAFHIME
        ]

        # Check if the message is from one of the threads aforementioned
        if message.channel.id in bot_dev_food:
            await asyncio.sleep(1.5) #not noice
            if message.embeds and message.type != discord.MessageType.reply and 'tenor.com' not in message.content:
                # Get the corresponding JSON file name

                file_name = ""
                
                if message.channel.id == bot_dev_food[0]:
                    file_name = "plugins/Meliodas245/mm-plugins/funpost-master/links_starch.json"

                elif message.channel.id == bot_dev_food[1]:
                    file_name = "plugins/Meliodas245/mm-plugins/funpost-master/links_brsl.json" 

                elif message.channel.id == bot_dev_food[2]:
                    file_name = "plugins/Meliodas245/mm-plugins/funpost-master/links_kafhime.json" 
                        

                # fetch the content of the message
                try:
                    with open(file_name, 'r') as f:
                        url = json.load(f)
                except FileNotFoundError: #just in case again 
                    url = []
                
                # Extract only the urls
                extractor = URLExtract()
                
                # Ignores the comments (i hope)
                with open(file_name, 'w') as f:
                    if message.content != '':
                        url[f'url{len(url)}'] = extractor.find_urls(message.content, with_schema_only=True)[0]
                        json.dump(url, f, indent=4)
                
                # Twitter verification checkmark :yello:
                await message.add_reaction('✅')
                await self.bot.process_commands(message)
        
async def setup(bot):
    await bot.add_cog(Misc(bot))
