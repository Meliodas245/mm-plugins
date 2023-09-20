import discord
from discord.ext import commands


CHANNEL_ID = 1106794799199174686


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def welcome_on_member_join(self, member: discord.Member):
        guild = member.guild
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel is not None:
            embed = discord.Embed(
                title=f"Welcome to Ruan Mei Mains, {member.name}!",
                description=f"Please read <#1106786003777224804> to avoid any trouble, and <#1106794848117342280> to familiarize yourself with the server.\n\n We wish you a pleasant stay; if you need help, DM <@1148374427441049750> to start a Modmail ticket!",
                colour=discord.Colour.from_rgb(84, 140, 140)
            )

            embed.set_thumbnail(url=member.display_avatar)
            embed.set_image(
                url='https://cdn.discordapp.com/attachments/1099432790229004439/1153915275591294987/Ruan-Mei-Honkai-Star-Rail.png')
            embed.set_footer(text=f'Thanks to you, we now have {guild.member_count} members!',
                             icon_url='https://cdn.discordapp.com/attachments/1106792127268139119/1153168727701995620/ruanmei_flower.png')

            await channel.send(content=member.mention, embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
