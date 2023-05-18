from datetime import timedelta

import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    """The 'uh oh' plugin, for when everything does wrong. (handles errors)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err: Exception):
        """
        Listens to and handles bot errors.
        This only listeners, not replaces. Core Modmail may have their own handlers.
        """
        # A pass just means we don't want to respond, and want the error to be silently ignored.
        # Any error not explicitly checked here will be handled as a generic error, and re-raised
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send(f"**Missing Required Argument**: `{err.param.name}`")
        elif isinstance(err, commands.BadArgument):
            pass
        elif isinstance(err, commands.CommandNotFound):
            pass
        elif isinstance(err, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown, try again in "
                           f"**{str(timedelta(seconds=err.retry_after)).split('.')[0]}**")
        elif isinstance(err, commands.NotOwner):
            pass
        elif isinstance(err, commands.MissingPermissions):
            pass
        elif isinstance(err, commands.BotMissingPermissions):
            await ctx.send("**Bot Missing Permissions**: I need ~~more Eidolons~~ "
                           f"`{', '.join(i.replace('_', ' ') for i in err.missing_permissions)}`"
                           " to do this")
        elif isinstance(err, commands.NoPrivateMessage):
            pass
        elif isinstance(err, commands.PrivateMessageOnly):
            pass
        elif isinstance(err, commands.CheckFailure):
            pass
        else:
            await ctx.send(embed=discord.Embed(
                description=f"<:seelecry:1085625830010540042> Something went wrong! (`{repr(err)}`)",
                colour=discord.Colour.red()
            ))
