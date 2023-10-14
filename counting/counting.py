import discord
from discord.ext import commands

class Counting(commands.Cog):
    """Counting Plugin"""

    def __init__(self, bot):
        self.bot = bot
        self.lastnumber = 0
        
        
    @commands.Cog.listener("on_message")
    async def check_number(self, message: discord.Message):
        if message.channel.id == 1162804188800102501 and message.author.id != 902093847889313833:
            if message.content.isdigit():
                expected_number = self.lastnumber + 1
                if int(message.content) == expected_number:
                    await message.add_reaction('✅')
                    self.lastnumber = expected_number
                else:
                    dumb = message.author.display_name
                    await message.add_reaction('❌')
                    embed = discord.Embed(
                        title=f"{dumb} doesn't know how to count",
                        colour=discord.Colour.red()
                    )
                    embed.add_field(name="Highest number reached", value=self.lastnumber)
                    embed.add_field(name="The Count has been reset to 0", value="Good luck next time")
                    embed.set_thumbnail(
                        url="https://img-os-static.hoyolab.com/communityWeb/upload/19dacf2bf7dad6cea3b4a1d8d68045a0.png"
                    )
                    await message.channel.send(embed=embed)
                    self.lastnumber = 0
            else:
                await message.channel.send("please refrain from typing in this channel")

async def setup(bot):
    await bot.add_cog(Counting(bot))

