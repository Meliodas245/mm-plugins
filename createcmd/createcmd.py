import json

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


class Custom(commands.Cog):
    """Custom Commands~"""

    def __init__(self, bot):
        self.bot = bot

    # Creating custom commands
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @commands.command()
    async def create(self, ctx, cmd, *, txt):
        """Creates a custom command"""
        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)

        # Check if the custom command doesn't exist
        if f'?{cmd}' not in custom_commands.keys():
            # Create the new command
            custom_commands[f'?{cmd}'] = txt

            # Save the new command
            with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
                json.dump(custom_commands, out, indent=4)

            embed = discord.Embed(description='Command created!', colour=discord.Colour.from_rgb(0, 255, 0))
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description='Command already exists!', colour=discord.Colour.from_rgb(255, 0, 0))
            await ctx.send(embed=embed)

    # Delete custom commands
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @commands.command()
    async def cdelete(self, ctx, cmd):
        """Deletes a custom command"""
        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)

        # Delete the custom command
        custom_commands.pop(f'?{cmd}', None)

        # Save the new list of commands
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
            json.dump(custom_commands, out, indent=4)

        embed = discord.Embed(description='Command deleted!', colour=discord.Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)

    # Update custom command
    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def cupdate(self, ctx, cmd, *, txt):
        """Updates a custom command"""
        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)

        # Check if the custom command exists
        if f'?{cmd}' in custom_commands.keys():
            # Update the command 
            custom_commands[f'?{cmd}'] = txt

            # Save the updated command
            with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
                json.dump(custom_commands, out, indent=4)

            embed = discord.Embed(description='Command updated!', colour=discord.Colour.random())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description='Command does not exist!', colour=discord.Colour.random())
            await ctx.send(embed=embed)

    # List custom commands
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command()
    async def clist(self, ctx):
        """List the custom commands"""
        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)

        commands = list(custom_commands.keys())

        # Sort the Commands Alphabetically
        commands.sort()

        # Embeds
        embeds = []

        for i in range(0, len(commands), 5):
            embed = discord.Embed(
                title='List of Custom Commands',
                description='\n'.join(commands[i:i + 10]),
                colour=discord.Colour.random()
            )
            embed.set_footer(text=f"Total of {len(commands)} custom commands")

            embeds.append(embed)

        # Customize Paginator
        PreviousButton = discord.ui.Button(emoji="<:bruh:1089823209660092486>", style=discord.ButtonStyle.secondary)
        NextButton = discord.ui.Button(emoji="<:yello:1086213035548479569>", style=discord.ButtonStyle.secondary)

        # Send Paginator
        await Paginator.Simple(PreviousButton=PreviousButton, NextButton=NextButton).start(ctx, pages=embeds)

    # Executing custom commands
    @commands.Cog.listener()
    async def on_message(self, message):
        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)

        # Get the custom command
        cmd = message.content.split(' ')[0]

        if cmd in custom_commands.keys():
            await message.channel.send(custom_commands[cmd])
            await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(Custom(bot))
