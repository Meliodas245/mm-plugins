import discord
import json
from discord.ext import commands, menus
from discord.ext.menus import button, First, Last
from core import checks
from core.models import PermissionLevel

# List of commands here:
# ?create
# ?cdelete
# ?clist
# ?cupdate

# Custom MenuPages
class CMenuPages(menus.MenuPages, inherit_buttons = False):
    @button('💀', position=First(0))
    async def go_to_first_page(self, payload):
        await self.show_page(0)
    
    @button(':skull:', position=First(1))
    async def go_to_previous_page(self, payload):
        await self.show_checked_page(self.current_page - 1)

    @button('<:next_check:754948796361736213>', position=Last(1))
    async def go_to_next_page(self, payload):
        await self.show_checked_page(self.current_page + 1)

    @button(':moyai:', position=Last(2))
    async def go_to_last_page(self, payload):
        max_pages = self._source.get_max_pages()
        last_page = max(max_pages - 1, 0)
        await self.show_page(last_page)

    @button(':rofl:', position=Last(0))
    async def stop_pages(self, payload):
        self.stop()

class MySource(menus.ListPageSource):
    async def format_page(self, menu, entries):
        embed = discord.Embed(
            description=f"This is number {entries}.", 
            color=discord.Colour.random()
        )
        embed.set_footer(text=f"Requested by {menu.ctx.author}")
        return embed

class Custom(commands.Cog):
    '''Custom Commands~'''

    def __init__(self, bot):
        self.bot = bot

    # Creating custom commands
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def create(self, ctx, cmd, *, txt):
        
        '''Creates a custom command'''

        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)
        
        # Check if the custom command doesnt exist
        if f'?{cmd}' not in custom_commands.keys():
            # Create the new command
            custom_commands[f'?{cmd}'] = txt
            
            # Save the new command
            with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
                json.dump(custom_commands, out, indent = 4)
            
            embed = discord.Embed(description = 'Command created!', colour = discord.Colour.from_rgb(0, 255, 0))
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description = 'Command already exists!', colour = discord.Colour.from_rgb(255, 0, 0))
            await ctx.send(embed=embed)

    # Delete custom commands
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def cdelete(self, ctx, cmd):
        
        '''Deletes a custom command'''

        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)
        
        # Delete the custom command
        custom_commands.pop(f'?{cmd}', None)
        
        # Save the new list of commands
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
            json.dump(custom_commands, out, indent = 4)

        embed = discord.Embed(description = 'Command deleted!', colour = discord.Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)
        
    # Update custom command
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def cupdate(self, ctx, cmd, *, txt):

        '''Updates a custom command'''

        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)
        
        # Check if the custom command exists
        if f'?{cmd}' in custom_commands.keys():
            
            # Update the command 
            custom_commands[f'?{cmd}'] = txt
            
            # Save the updated command
            with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json', 'w') as out:
                json.dump(custom_commands, out, indent = 4)

            embed = discord.Embed(description = 'Command updated!', colour = discord.Colour.random())
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description = 'Command does not exist!', colour = discord.Colour.random())
            await ctx.send(embed=embed)
    
    # List custom commands
    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command()
    async def clist(self, ctx):

        '''List the custom commands'''
        
        # Load the set of custom commands:
        with open('plugins/Meliodas245/mm-plugins/createcmd-master/commands.json') as f:
            custom_commands = json.load(f)
        
        commands = list(custom_commands.keys())
        
        # Embed

        embed = discord.Embed(
            title = 'List of Custom Commands',
            description = '\n'.join(commands),
            colour = discord.Colour.random()
        )

        embed.set_footer(text=f"Total of {len(commands)} custom commands")

        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        formatter = MySource(data, per_page=1)
        menu = CMenuPages(formatter)
        
        await menu.start(ctx)

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
            
async def setup(bot):
    await bot.add_cog(Custom(bot))
