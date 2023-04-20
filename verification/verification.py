import discord
from discord.ext import commands

class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # carl you tried
    @commands.Cog.listener()
    async def on_reaction_add(reaction, member):
        if reaction.message.id == 1097762971373027348:
            guild = member.guild
            role = discord.utils.get(guild.roles, id=896300858277494784)
            member.add_roles(role)
        
async def setup(bot):
    await bot.add_cog(Reaction(bot))
