import discord
import json
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

# Set of custom commands:
custom_commands = {
    '?airplanes' : 'https://media.discordapp.net/attachments/1086240031720603708/1087156186467532830/image.png?width=1177&height=654'
}
class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Executing custom commands
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command()
    async def create(self, ctx, cmd, url):
        custom_commands[f'?{cmd}'] = url
    
    @commands.Cog.listener()
    async def on_message(self, message):
        
        cmd = message.content.split(' ')[0]
        
        if cmd in custom_commands:
            await message.channel.send(custom_commands[cmd])
        
        else:
            await bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(Custom(bot))
