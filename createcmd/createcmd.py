import json
from os.path import dirname, exists

import Paginator
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


# List of commands here:
# ?create
# ?cdelete
# ?clist
# ?cupdate
# ?creload


COMMANDS_FILE = dirname(__file__) + "/commands.json"


class Custom(commands.Cog):
    """Custom Commands~"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.custom_commands = {}
        self.load_config()

    # Creating custom commands
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @commands.command()
    async def create(self, ctx: commands.Context, cmd: str, *, txt: str):
        """Creates a custom command"""
        # Check if the custom command doesn't exist
        if f'?{cmd}' not in self.custom_commands.keys():
            # Create the new command
            self.custom_commands[f'?{cmd}'] = txt

            # Save the new command
            with open(COMMANDS_FILE, 'w') as out:
                json.dump(self.custom_commands, out, indent=4)

            embed = discord.Embed(description='Command created!', colour=discord.Colour.green())
        else:
            embed = discord.Embed(description='Command already exists!', colour=discord.Colour.red())
        await ctx.send(embed=embed)

    # Delete custom commands
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @commands.command()
    async def cdelete(self, ctx: commands.Context, cmd: str):
        """Deletes a custom command"""
        if f"?{cmd}" not in self.custom_commands.keys():
            embed = discord.Embed(description="Command does not exist", colour=discord.Colour.red())
        else:
            # Delete the custom command
            self.custom_commands.pop(f'?{cmd}', None)

            # Save the new list of commands
            with open(COMMANDS_FILE, 'w') as out:
                json.dump(self.custom_commands, out, indent=4)

            embed = discord.Embed(description='Command deleted!', colour=discord.Colour.red())
        await ctx.send(embed=embed)

    # Update custom command
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def cupdate(self, ctx: commands.Context, cmd: str, *, txt: str):
        """Updates a custom command"""
        # Check if the custom command exists
        if f'?{cmd}' in self.custom_commands.keys():
            # Update the command 
            self.custom_commands[f'?{cmd}'] = txt

            # Save the updated command
            with open(COMMANDS_FILE, 'w') as out:
                json.dump(self.custom_commands, out, indent=4)

            embed = discord.Embed(description='Command updated!', colour=discord.Colour.green())
        else:
            embed = discord.Embed(description='Command does not exist!', colour=discord.Colour.red())
        await ctx.send(embed=embed)

    # List custom commands
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command()
    async def clist(self, ctx: commands.Context):
        """List the custom commands"""
        custom_commands = list(self.custom_commands.keys())

        # Sort the Commands Alphabetically
        custom_commands.sort()

        # Embeds
        embeds = []

        for i in range(0, len(custom_commands), 5):
            embed = discord.Embed(
                title='List of Custom Commands',
                description='\n'.join(custom_commands[i:i + 10]),
                colour=discord.Colour.random()
            )
            embed.set_footer(text=f"Total of {len(custom_commands)} custom commands")

            embeds.append(embed)

        # Customize Paginator
        PreviousButton = discord.ui.Button(emoji="<:bruh:1089823209660092486>", style=discord.ButtonStyle.secondary)
        NextButton = discord.ui.Button(emoji="<:yello:1086213035548479569>", style=discord.ButtonStyle.secondary)

        # Send Paginator
        await Paginator.Simple(PreviousButton=PreviousButton, NextButton=NextButton).start(ctx, pages=embeds)

    # Reload commands from file
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def creload(self, ctx: commands.Context):
        """
        Reloads the custom commands from file.
        This should only ever be used if a modification was done directly to the file (rather than through the bot)
        """
        self.load_config()
        await ctx.send(embed=discord.Embed(description="Commands successfully reloaded", colour=discord.Colour.green()))

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def carchive(self, ctx: commands.Context):
        """Archives the custom commands"""
        await ctx.reply(file=discord.File(COMMANDS_FILE))

    # Executing custom commands
    @commands.Cog.listener("on_message")
    async def create_cmd_on_message(self, message: discord.Message):
        # Get the custom command
        cmd = message.content.split(' ')[0]

        if cmd in self.custom_commands.keys():
            await message.channel.send(self.custom_commands[cmd])

    def load_config(self):
        if not exists(COMMANDS_FILE):
            with open(COMMANDS_FILE, 'w') as out:
                json.dump({}, out, indent=4)
        else:
            with open(COMMANDS_FILE) as f:
                self.custom_commands = json.load(f)


async def setup(bot):
    await bot.add_cog(Custom(bot))
