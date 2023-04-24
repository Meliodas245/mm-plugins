import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

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
        
        # Remove other types of reactions
        elif message_id == 1097762971373027348:
            await remove_reaction(payload.emoji.name, member)
        
        # If role exists
        if role is not None:
            member = payload.member
            # If member exists, Is not a bot and Doesn't have the Muted Role
            if member is not None and not member.bot and member.get_role(902856057662083103) is None:
                await member.add_roles(role)

            # Remove the reaction for member
            if not member.bot:
                await remove_reaction('✅', member)

    # In case all reactions get cleared
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def fixreaction(self, ctx):
        '''Fixes the reactions in verification channel'''
        msg = self.bot.get_message(1097762971373027348)
        await msg.add_reaction('✅')

async def setup(bot):
    await bot.add_cog(Reaction(bot))
