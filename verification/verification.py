import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

CHANNEL_ID = 1097760934090514523
MESSAGE_ID = 1097762971373027348
ROLE_ID = 896300858277494784
MUTED_ID = 902856057662083103


class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_raw_reaction_add")
    async def verification_on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        message_id = payload.message_id
        msg = await self.bot.get_channel(CHANNEL_ID).fetch_message(MESSAGE_ID)
        if message_id != msg.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = payload.member
        if payload.emoji.name == '✅':
            # Remove Reaction
            if not member.bot:
                await msg.remove_reaction('✅', member)
        # Remove other types of reactions
        else:
            return await msg.remove_reaction(payload.emoji, member)

        # Get Butterflies role
        role = discord.utils.get(guild.roles, id=ROLE_ID)
        # If member exists, is not a bot and doesn't have the Muted Role
        if member is not None and not member.bot and member.get_role(MUTED_ID) is None:
            await member.add_roles(role)

    # In case all reactions get cleared
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def fixreaction(self, ctx: commands.Context):
        """Fixes the reactions in verification channel"""
        # Get Message object from the Verification Channel
        channel = self.bot.get_channel(CHANNEL_ID)
        msg = await channel.fetch_message(MESSAGE_ID)
        await msg.add_reaction('✅')

        await ctx.send(embed=discord.Embed(description='Reaction added!', colour=discord.Colour.from_rgb(0, 255, 0)))


async def setup(bot):
    await bot.add_cog(Verification(bot))
