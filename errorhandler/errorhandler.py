import os
from asyncio import TimeoutError
from random import randint
from re import compile
from traceback import format_exception
from uuid import uuid4

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

LOG_TO_FILE = True
LOG_DIR = os.path.dirname(__file__) + "/logs"
USERNAME_REGEX = compile(r"File \"/home/.*?/")
DEVELOPER_ROLE = 1087928500893265991


def role_or_perm(role: int, perm: PermissionLevel):
    """
    Decorator to check for either a role OR a PermissionLevel.
    Because apparently commands.check_any causes the default PermissionLevel check to break.

    As MM doesn't support local modules, copy this around as needed (I hate this too)
    """
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author) or ctx.author.id == ctx.bot.user.id:
            # Bot owner(s) (and creator) has absolute power over the bot
            return True

        if ctx.author.get_role(role):
            return True

        if (
                perm is not PermissionLevel.OWNER
                and ctx.channel.permissions_for(ctx.author).administrator
                and ctx.guild == ctx.bot.modmail_guild
        ):
            # Administrators have permission to all non-owner commands in the Modmail Guild
            return True

        checkables = {*ctx.author.roles, ctx.author}
        level_permissions = ctx.bot.config["level_permissions"]

        for level in PermissionLevel:
            if level >= perm and level.name in level_permissions:
                # -1 is for @everyone
                if -1 in level_permissions[level.name] or any(
                        str(check.id) in level_permissions[level.name] for check in checkables
                ):
                    return True
        return False

    return commands.check(predicate)


class ErrorHandler(commands.Cog):
    """The 'uh oh' plugin, for when everything goes wrong."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

    @commands.command()
    @role_or_perm(role=DEVELOPER_ROLE, perm=PermissionLevel.SUPPORTER)
    async def raiseerror(self, ctx: commands.Context):
        """Raises an error for testing purposes"""
        raise Exception("This is a test error")

    @commands.command(aliases=["vlog"])
    @role_or_perm(role=DEVELOPER_ROLE, perm=PermissionLevel.SUPPORTER)
    async def viewlog(self, ctx: commands.Context, uuid: str):
        """View a log file"""
        try:
            with open(f"{LOG_DIR}/{uuid}.log", encoding="utf-8") as f:
                log = f.read()
        except (FileNotFoundError, OSError):
            return await ctx.reply(f"Log `{uuid}` not found")
        if len(log) > 1984:
            await ctx.reply(files=[discord.File(f"{LOG_DIR}/{uuid}.log")])
        else:
            await ctx.reply(f"```asciidoc\n{log}```")

    @commands.command(aliases=["dlog", "dellog", "delog"])
    @role_or_perm(role=DEVELOPER_ROLE, perm=PermissionLevel.SUPPORTER)
    async def deletelog(self, ctx: commands.Context, uuid: str):
        """Deletes a log file"""
        # This is run by trusted users, so not doing too much checking
        if ".." in uuid:
            return await ctx.reply("No. Just no.")
        try:
            os.remove(f"{LOG_DIR}/{uuid}.log")
            return await ctx.reply(f"Log `{uuid}` deleted")
        except (FileNotFoundError, OSError):
            return await ctx.reply(f"Log `{uuid}` not found")

    @commands.command(aliases=["wipelog"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
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
        for file in os.listdir(LOG_DIR):
            os.remove(f"{LOG_DIR}/{file}")
            count += 1

        await ctx.reply(f"Successfully wiped {count} logs.")

    @commands.Cog.listener("on_command_error")
    async def error_handler_on_command_error(self, ctx: commands.Context, err: Exception):
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
                title="<:seelecry:1085625830010540042> Something went wrong!",
                description="Please report this to the developers.",
                colour=discord.Colour.red()
            )
            if LOG_TO_FILE:
                uuid = uuid4()  # Generate a random UUID, if this conflicts, you should buy a lottery ticket...
                traceback = "".join(format_exception(type(err), err, err.__traceback__))
                # Hide the hoster's username (assuming Linux system) for privacy reasons
                traceback = USERNAME_REGEX.sub("File \"/home/*****/", traceback)
                with open(f"{LOG_DIR}/{uuid}.log", "w", encoding="utf-8") as f:
                    log_content = "= Info =\n" \
                                  f"ID:: {uuid}\n" \
                                  f"User:: {ctx.author} ({ctx.author.id})\n" \
                                  f"Command:: {ctx.command}\n" \
                                  f"Args:: {repr(ctx.args)}\n" \
                                  f"Kwargs:: {repr(ctx.kwargs)}\n" \
                                  f"Message:: {repr(ctx.message.content)}\n" \
                                  f"Message URL:: {ctx.message.jump_url}\n\n= Traceback =\n" \
                                  f"{traceback}"
                    f.write(log_content)
                embed.add_field(name="Error ID", value=uuid, inline=False)
            await ctx.send(embed=embed)
            if not LOG_TO_FILE:
                raise err


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
