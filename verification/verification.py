import discord
from discord.ext import commands
'''
Currently not installed, as long as carl is working kekw
'''
class Reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # carl you tried
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id, self.bot.guilds)
        
        if message_id == 1097762971373027348 and payload.emoji.name == '✅':
            # Get Butterflies Role
            role = discord.utils.get(guild.roles, id=896300858277494784)
        
        if role is not None:
            member = payload.member
            if member is not None:
                await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(Reaction(bot))
