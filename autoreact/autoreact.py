import json
import os
from re import compile
from typing import Union
from uuid import uuid4

import Paginator
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

CONFIG_FILE = os.path.dirname(__file__) + "/autoreact.json"


class AutoReact(commands.Cog):
    """Automatically react to messages."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.compiled_regexes = {}
        self.config = {}
        self.load_config()

    @commands.command(aliases=["aradd"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autoreactadd(self, ctx: commands.Context, emoji: Union[discord.Emoji, str], *,
                           phrase: str):
        """Adds an autoreact based on a phrase match to the message, case-insensitive."""
        if isinstance(emoji, discord.Emoji) and not emoji.is_usable():
            return await ctx.reply("That emoji is not available to me.")
        elif isinstance(emoji, str):
            try:
                await ctx.message.add_reaction(emoji)
            except (TypeError, discord.errors.HTTPException):
                return await ctx.reply("Invalid emoji.")
        uuid = str(uuid4())
        self.config[uuid] = {
            "type": "phrase",
            "trigger": phrase,
            "emoji": emoji if isinstance(emoji, str) else emoji.id
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f)

        await ctx.reply(f"Added an autoreact for `{phrase}` with {emoji}, ID: *`{uuid}`*")

    @commands.command(aliases=["araddregex", "araddre"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autoreactaddregex(self, ctx: commands.Context, emoji: Union[discord.Emoji, str], *,
                                regex: str):
        """
        Adds an autoreact based on a regex match to the message, case-sensitive. This is done via partial match.
        Hope you know what you're doing...
        """
        if isinstance(emoji, discord.Emoji) and not emoji.is_usable():
            return await ctx.reply("That emoji is not available to me.")
        elif isinstance(emoji, str):
            try:
                await ctx.message.add_reaction(emoji)
            except (TypeError, discord.errors.HTTPException):
                return await ctx.reply("Invalid emoji.")
        uuid = str(uuid4())
        try:
            self.compiled_regexes[uuid] = compile(regex)
        except Exception as e:
            return await ctx.reply(f"Invalid regex: `{repr(e)}`")
        self.config[uuid] = {
            "type": "regex",
            "trigger": regex,
            "emoji": emoji if isinstance(emoji, str) else emoji.id
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f)

        await ctx.reply(f"Added a regex autoreact for `{regex}` with {emoji}, ID: *`{uuid}`*")

    @commands.command(aliases=["arremove", "ardelete"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autoreactremove(self, ctx: commands.Context, uuid):
        """Remove an autoreact based on its ID, obtainable via ?autoreactlist <emoji>"""
        del self.config[uuid]
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f)

        await ctx.reply(f"Removed autoreact with ID `{uuid}`")

    @commands.command(aliases=["arrefresh"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autoreactrefresh(self, ctx: commands.Context):
        """Refreshes the autoreact list from file"""
        self.load_config()
        await ctx.reply("Refreshed autoreact list from file.")

    @commands.command(aliases=["arlist"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def autoreactlist(self, ctx: commands.Context):
        """Lists all autoreacts"""
        await self.send_list(ctx, self.config)

    @commands.command(aliases=["arsearch"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def autoreactsearch(self, ctx: commands.Context, *, query: Union[discord.Emoji, str]):
        """Searches for an autoreact based on any field"""
        if isinstance(query, discord.Emoji):
            query = str(query.id)

        matches = {}
        for uuid, data in self.config.items():
            if query in uuid:
                matches[uuid] = data
                continue
            for field in data.values():
                if query in str(field):
                    matches[uuid] = data
                    break

        await self.send_list(ctx, matches)

    @commands.command(aliases=["ararchive"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def autoreactarchive(self, ctx: commands.Context):
        """Archives the autoreact config file"""
        await ctx.reply(file=discord.File(CONFIG_FILE))

    @commands.Cog.listener("on_message")
    async def auto_react_on_message(self, message: discord.Message):
        if not message.author.guild or message.author.bot:
            return
        content = message.content
        for uuid, data in self.config.items():
            if (data["type"] == "phrase" and data["trigger"].lower() in content.lower()) or \
                    (data["type"] == "regex" and self.compiled_regexes[uuid].search(content)):
                emoji = data["emoji"] if isinstance(data["emoji"], str) else self.bot.get_emoji(data["emoji"])
                if emoji is not None:
                    await message.add_reaction(emoji)

    @staticmethod
    async def send_list(ctx: commands.Context, autoreact: dict):
        if len(autoreact) == 0:
            return await ctx.reply("No autoreacts found.")
        embeds = []
        for i in range(0, len(autoreact), 15):
            embed = discord.Embed(
                title="Autoreact List",
                description="\n".join(
                    f"`{uuid}`: `{data['trigger']}` - {data['emoji'] if isinstance(data['emoji'], str) else ctx.bot.get_emoji(data['emoji'])}"
                    for uuid, data in list(autoreact.items())[i:i + 15]
                ),
                color=discord.Color.blurple()
            )
            embeds.append(embed)

        await Paginator.Simple(
            PreviousButton=discord.ui.Button(emoji="⬅️", style=discord.ButtonStyle.secondary),
            NextButton=discord.ui.Button(emoji="➡️", style=discord.ButtonStyle.secondary)
        ).start(ctx, embeds)

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        else:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                self.config: dict = json.load(f)
            for uuid, data in self.config.items():
                if data["type"] == "regex":
                    self.compiled_regexes[uuid] = compile(data["trigger"])


async def setup(bot):
    await bot.add_cog(AutoReact(bot))
