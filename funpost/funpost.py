import discord
import random
import json
import asyncio
from urlextract import URLExtract
from discord.ext import commands
from urllib.request import urlopen
from core import checks
from core.models import PermissionLevel

# List of commands here:
# ?advice
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
        
        file_name = f'plugins/Meliodas245/mm-plugins/funpost-master/links_{ship}.json'

        # Fetch the links
        with open(file_name, 'r') as f:
            url = json.load(f)

        # Extract only the urls
        extractor = URLExtract()

        # Write to file
        for link in messages:
            with open(file_name, 'w') as f:
                url[f'url{len(url)}'] = extractor.find_urls(link, check_dns=True, with_schema_only=True)[0] # get domains with schema only
                json.dump(url, f, indent=4)
        
        return len(messages)
    
    else:
        return 0
#--------------------------------------------------------------------------------------------------------------------------------

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
    
    #fetch messages from threads
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command(name='fetchYuri',aliases = ['fetchyuri','fetchgay'])
    async def fetch_yuri_command(self, ctx):
        
        '''Fetches the links in all ship threads, can be only run once.'''
        
        ships_sailed = [
            {
                'ship' : 'starch',
                'channel_id' : 1101776593422127144
            },
            {
                'ship' : 'brsl',
                'channel_id' : 1101627790492708984
            },
            {
                'ship' : 'kafhime',
                'channel_id' : 1103593594440396810
            }            
        ]

        for gay in ships_sailed:
            ship = gay['ship']
            channel_id = gay['channel_id']
            file_name = f'plugins/Meliodas245/mm-plugins/funpost-master/links_{ship}.json'
            
            with open(file_name, 'r') as f:
                url = json.load(f)
            
            if len(url) < 1:
                message_count = await fetch_yuri_messages(self.bot, channel_id, ship)
                await ctx.send(f'fetched {message_count} {ship} links')
            
            #wanted to clean up the code omg
            #else:
            #    await ctx.reply(f'already fetched, new messages are automatically fetched')
    
    # Yuri
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(name='Yuri', aliases=['yuri'])
    async def Yuri(self, ctx, *, ship="all"):
        
        '''Sends a random yuri art, default is both ships, ships: `brsl`, `starch`, `kafhime`'''
        
        if ship == 'steven' or ship == 'stelle7':
            ship = 'starch'
        
        if ship == "all":
            num = random.randint(0,2)
            # starch True ship
            # this can be changed to a switch type statement 
            if num == 1:
                ship = 'starch'
            elif num == 2:
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
    
    # Yuri Archive
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def archive(self, ctx):
        
        '''Archives the json files'''
        await asyncio.sleep(0.5)
        files = [ 
        discord.File('plugins/Meliodas245/mm-plugins/funpost-master/links_brsl.json'),
        discord.File('plugins/Meliodas245/mm-plugins/funpost-master/links_starch.json'),
        discord.File('plugins/Meliodas245/mm-plugins/funpost-master/links_kafhime.json')
        ]
        await ctx.reply(files=files)

    #Listener to autofetch yuri from thread
    @commands.Cog.listener()
    async def on_message(self,message):
        #Set thread's ids (same as fetch_yuri_command)
        brsl_channel_id = 1101627790492708984   # Replace this id with brsl thread id (already done)
        starch_channel_id = 1101776593422127144 # Replace this id with starch thread id (already done)
        kafhime_channel_id = 1103593594440396810 # Replace this id with kafhime thread id (done)

        # Check if the message is from one of the threads aforementioned
        if message.channel.id == brsl_channel_id or message.channel.id == starch_channel_id or message.channel.id == kafhime_channel_id:
            await asyncio.sleep(0.5)
            if message.embeds and message.type != discord.MessageType.reply and 'tenor.com' not in message.content:
                # Get the corresponding JSON file name
                # maybe we should change this to a "switch" type statement :yello:
                if message.channel.id == brsl_channel_id:
                    file_name = "plugins/Meliodas245/mm-plugins/funpost-master/links_brsl.json"  
                elif message.channel.id == starch_channel_id :
                    file_name = "plugins/Meliodas245/mm-plugins/funpost-master/links_starch.json" 
                else:
                    file_name = "plugins/Meliodas245/mm-plugins/funpost-master/links_kafhime.json" 
                        

                # fetch the content of the message
                try:
                    with open(file_name, 'r') as f:
                        url = json.load(f)
                except FileNotFoundError: #just in case again 
                    url = []

                with open(file_name, 'w') as f:
                    url[f'url{len(url)}'] = message.content
                    json.dump(url, f, indent=4)

                await message.add_reaction('✅')
        
        await self.bot.process_commands(message)
            
async def setup(bot):
    await bot.add_cog(Misc(bot))
