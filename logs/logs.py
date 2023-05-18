import discord
import os
from discord.ext import commands
from core import checks
from core.models import PermissionLevel


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def getlogs(self, ctx):
        
        for filename in os.listdir("./temp"):
            if filename.endswith(".txt"):
                file = filename
        
        files = [ 
        discord.File(f'temp/{file}')
        ]

        await ctx.reply(files=files)

async def setup(bot):
    await bot.add_cog(Logs(bot))
