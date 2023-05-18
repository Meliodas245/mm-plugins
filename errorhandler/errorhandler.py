import os
from asyncio import TimeoutError
from datetime import timedelta
from random import randint
from traceback import format_exception
from uuid import uuid4

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

LOG_TO_FILE = True


class ErrorHandler(commands.Cog):
    """The 'uh oh' plugin, for when everything does wrong. (handles errors)"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @commands.command()
    async def viewlog(self, ctx: commands.Context, uuid: str):
        """View a log file"""
        try:
            with open(f"plugins/Meliodas245/mm-plugins/errorhandler-master/{uuid}.log") as f:
                log = f.read()
        except FileNotFoundError:
            await ctx.reply(f"Log `{uuid}` not found")
        if len(log) > 3994:
            await ctx.reply(files=[discord.File(f"plugins/Meliodas245/mm-plugins/errorhandler-master/{uuid}.log")])
        else:
            await ctx.reply(embed=discord.Embed(title=uuid, description=f"```{log}```", colour=discord.Colour.random()))

    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @commands.command()
    async def deletelog(self, ctx: commands.Context, uuid: str):
        """Deletes a log file"""
        # This is run by trusted users, so not doing too much checking
        if ".." in uuid:
            return await ctx.reply("No. Just no.")
        try:
            os.remove(f"plugins/Meliodas245/mm-plugins/errorhandler-master/{uuid}.log")
            return await ctx.reply(f"Log `{uuid}` deleted")
        except FileNotFoundError:
            return await ctx.reply(f"Log `{uuid}` not found")

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command(aliases=["wipelog"])
    async def wipelogs(self, ctx: commands.Context):
        """Wipes ALL log files (use with caution)"""
        # Generate a random 6 digit confirmation code to prevent accidental wipes
        code = str(randint(100000, 999999))
        await ctx.reply(
            f"This will wipe ALL logs and cannot be undone. Reply with `{code}` to confirm within 30 seconds.")
        try:
            await self.bot.wait_for(
                'message',
                check=lambda message: message.channel == ctx.message.channel and
                                      message.author == ctx.message.author and message.content == code,
                timeout=30)
        except TimeoutError:
            return await ctx.reply("Timed out, logs have NOT been wiped")

        count = 0
        for file in os.listdir("plugins/Meliodas245/mm-plugins/errorhandler-master"):
            os.remove(f"plugins/Meliodas245/mm-plugins/errorhandler-master/{file}")
            count += 1

        await ctx.reply(f"Successfully wiped {count} logs.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err: Exception):
        """
        Listens to and handles bot errors.
        This only listeners, not replaces. Core Modmail may have their own handlers.
        """
        # A pass just means we don't want to respond, and want the error to be silently ignored.
        # Any error not explicitly checked here will be handled as a generic error, and re-raised if not logged
        # Currently all command-input related errors are pass-ed as the upstream handler already handles them
        if isinstance(err, commands.MissingRequiredArgument):
            pass
        elif isinstance(err, commands.BadArgument):
            pass
        elif isinstance(err, commands.CommandNotFound):
            pass
        elif isinstance(err, commands.CommandOnCooldown):
            pass
        elif isinstance(err, commands.NotOwner):
            pass
        elif isinstance(err, commands.MissingPermissions):
            pass
        elif isinstance(err, commands.BotMissingPermissions):
            pass
        elif isinstance(err, commands.NoPrivateMessage):
            pass
        elif isinstance(err, commands.PrivateMessageOnly):
            pass
        elif isinstance(err, commands.CheckFailure):
            pass
        else:
            embed = discord.Embed(
                description="<:seelecry:1085625830010540042> Something went wrong! "
                            "Please report this to the developers.",
                colour=discord.Colour.red()
            )
            if LOG_TO_FILE:
                uuid = uuid4()  # Generate a random UUID, if this conflicts, you should buy a lottery ticket...
                with open(f"plugins/Meliodas245/mm-plugins/errorhandler-master/{uuid}.log") as f:
                    log_content = f"""
                    User: {ctx.author} ({ctx.author.id})
                    Command: {ctx.command}
                    Args: {ctx.args} | {ctx.kwargs}
                    Message: {repr(ctx.message.content)}
                    Message URL: {ctx.message.jump_url}
                    Traceback:
                    {''.join(format_exception(type(err), err, err.__traceback__))}
                    """
                    f.write(log_content)
                embed.add_field(name="Error ID", value=uuid, inline=False)
            await ctx.send(embed=embed)
            if not LOG_TO_FILE:
                raise err


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
