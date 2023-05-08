import discord
from discord.ext import commands

# FUTURE 2DO: make a generalized version of this
class CustomMsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def goofy(self, message):

        # Check if message contains the **Word**
        if 'masochist' in message.content.lower():
            await message.channel.send('seele mains promotes holy and pure actions!')
            await self.bot.process_commands(message)
        elif 'gepard' in discord.utils.remove_markdown(message.content.lower()):
            await message.channel.send('you mean g*pard')
            await self.bot.process_commands(message)
            
async def setup(bot):
    await bot.add_cog(CustomMsg(bot))
