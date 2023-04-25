import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = discord.utils.get(member.guild.channels, id=896803126542229534)
        if channel is not None:
            embed = discord.Embed(
                title=f"Welcome to Seele Mains, {member.name}!",
                description=f"Please read <#1097760934090514523> to avoid any trouble, and <#898896680886370334> to familiarize yourself with the server.\n\n We wish you a pleasant stay; if you need help, DM <@902093847889313833> to start a Modmail ticket!",
                colour = discord.Colour.from_rgb(195, 177, 225)
            )

            embed.set_thumbnail(url=member.display_avatar)
            embed.set_image(url='https://media.discordapp.net/attachments/902836100261879818/1099532213990735952/ezgif.com-gif-maker_7.gif')
            embed.set_footer(text=f'Thanks to you, we now have {guild.member_count} members!', icon_url='https://media.discordapp.net/attachments/896803697223401522/1087555998434213978/seele_love.png')
            
            await channel.send(content=member.mention, embed = embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
