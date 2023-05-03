import discord
from discord.ext import commands

# FUTURE 2DO: make a generalized version of this
class CustomMsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        # Check if message contains the **Word**
        if 'masochist' in message.content.lower():
            await message.channel.send('seele mains promotes holy and pure actions!')
        elif 'gepard' in message.content.lower():
            await message.channel.send('you mean g*pard')
async def setup(bot):
    await bot.add_cog(CustomMsg(bot))
