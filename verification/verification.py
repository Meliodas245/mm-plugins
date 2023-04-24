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
        # Get Message object from the Verification Channel
        channel = self.bot.get_channel(1097760934090514523) # Channel ID
        msg = await channel.fetch_message(1097762971373027348) # Message ID
        
        # Get Guild
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id, self.bot.guilds)
        
        member = payload.member
        role = None
        
        if message_id == 1097762971373027348 and payload.emoji.name == '✅':
            # Get Butterflies Role
            role = discord.utils.get(guild.roles, id=896300858277494784)
            # Remove Reaction
            if not member.bot:
                await msg.remove_reaction('✅', member)
        
        # Remove other types of reactions
        elif message_id == 1097762971373027348:
            await msg.remove_reaction(payload.emoji, member)
        
        # If role exists
        if role is not None:
            # If member exists, Is not a bot and Doesn't have the Muted Role
            if member is not None and not member.bot and member.get_role(902856057662083103) is None:
                await member.add_roles(role)

    # In case all reactions get cleared
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def fixreaction(self, ctx):
        '''Fixes the reactions in verification channel'''
        msg = self.bot.get_message(1097762971373027348)
        await msg.add_reaction('✅')
        
        embed = discord.Embed(description = 'Reaction added!', colour = discord.Colour.from_rgb(0, 255, 0))
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Reaction(bot))
