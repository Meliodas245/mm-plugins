import discord
from discord.ext import commands

class Booster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @checks.has_permissions(PermissionLevel.REGULAR)
    # Check if the member has the Babochka's Esteemed Booster Role by ID
    # Add another check if the member already has claimed a Role
    @commands.has_role(1086878794880659548)
    async def claim(self, ctx, *, role):
        '''Claim a custom role~'''
        member = ctx.author

