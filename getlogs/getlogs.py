import discord
import os
from discord.ext import commands
from core import checks
from core.models import PermissionLevel


class getLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def getlogs(self, ctx):
        # ignore this aight

        for filename in os.listdir("./temp"):
            if filename.endswith(".log"):
                file = filename
        
        files = [ 
        discord.File(f'temp/{file}')
        ]

        await ctx.reply(files=files)

async def setup(bot):
    await bot.add_cog(getLogs(bot))