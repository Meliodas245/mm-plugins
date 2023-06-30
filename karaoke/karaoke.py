import discord
from discord.ext import commands


QUEUE_CHANNEL = 1120456979459080343
EVENT_STAFF = 1086023819073962086

class StupidButtons(discord.ui.View):

    def __init__(self, queue: list):
        self.queue = queue
        super().__init__()
    
    # JOIN
    @discord.ui.button(label = 'Join', style = discord.ButtonStyle.success, emoji = "<:lamesticker:1116535025098297426>")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        # Adds to the queue.

        if interaction.user.name not in self.queue:
            self.queue.append(interaction.user.name)
            q = '\n'.join(self.queue)

            embed = discord.Embed (
                title=':microphone: Karaoke',
                colour=discord.Colour.blue()
            )
            embed.add_field(name = "Queue List", value=f"{q}")
            
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message(content="You've already joined the queue!", ephemeral=True)

    # NEXT - STAFF ONLY
    @discord.ui.button(label = 'Next', style = discord.ButtonStyle.primary, emoji="<:seelejoy:1085986027115663481>")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        
        # Removes the first person from the queue as soon as it's their turn. 
        if member.get_role(EVENT_STAFF):
            if len(self.queue) >= 1:
                n = self.queue.pop(0)
                q = '\n'.join(self.queue)

                embed = discord.Embed (
                    title=':microphone: Karaoke',
                    colour=discord.Colour.blue()
                )
                embed.add_field(name = "Queue List", value=f"{q}")

                await interaction.response.edit_message(embed=embed)
                await interaction.channel.send(content=f"`{n}` is next!")
            
            else:
                await interaction.response.send_message(content=f"Nobody is next :yello:", ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Naurrrrr you cant lol", ephemeral=True)
    
    # LEAVE
    @discord.ui.button(label = 'Leave', style = discord.ButtonStyle.secondary, emoji="<:bruh:1089823209660092486>")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        # Yeets from the queue.

        if interaction.user.name in self.queue:
            self.queue.pop(self.queue.index(interaction.user.name))
            q = '\n'.join(self.queue)
            
            embed = discord.Embed (
                title=':microphone: Karaoke',
                colour=discord.Colour.blue()
            )
            embed.add_field(name = "Queue List", value=f"{q}")

            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message(content=f"You aren't even in the queue what yo doinnn", ephemeral=True)
    
    # RESET - STAFF ONLY
    @discord.ui.button(label = 'Reset', style = discord.ButtonStyle.danger, emoji= "<:seeleomg:1085605320065302630>")
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)

        if member.get_role(EVENT_STAFF):
        # Clears the queue list and Stops the interaction.
            self.queue.clear()
            
            embed = discord.Embed(description=f'Adios.', colour=discord.Colour.red())
            
            await interaction.response.edit_message(embed=embed, view=None)
            # Stops the interaction, forgor how to disable le buttons -jej
            self.stop()
        
        else:
            await interaction.response.send_message(content=f"Naurrrrr you cant lol", ephemeral=True)

queue = []

class Karaoke(commands.Cog):

    """Karaoke Queue command"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def queue_channel(ctx: commands.Context):
        return ctx.channel.id == QUEUE_CHANNEL
    
    @commands.command(aliases=['karaokeq', 'kq'])
    @commands.check(queue_channel)
    async def karaokequeue(self, ctx: commands.Context):
        global queue

        view = StupidButtons(queue)

        q = '\n'.join(queue)
        
        embed = discord.Embed(
            title=':microphone: Karaoke',
            colour=discord.Colour.blue()
        )

        embed.add_field(name = "Queue List", value=f"{q}")
        await ctx.reply(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Karaoke(bot))
