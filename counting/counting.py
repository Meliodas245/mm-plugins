import asyncio

import discord
from discord.ext import commands

COUNTING_CHANNEL = 1162804188800102501
DUPLICATE_GRACE = 0.75  # Time in seconds to be lenient to duplicate messages


class Counting(commands.Cog):
    """Counting Plugin"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_number = 0
        self.last_message = None  # For use in detecting notable message edits & deletes
        self.lock = asyncio.Lock()  # To prevent dual-processing edge-cases

    @commands.Cog.listener("on_message")
    async def counting_on_message(self, message: discord.Message):
        if not message.author or not message.author.guild or message.author.bot:  # Irrelevant
            return
        if message.channel.id != COUNTING_CHANNEL:  # Not the counting channel
            return

        # TODO: Implement detections & history searching to make absolute sure that self.last_number and
        #  self.last_message will always exist (and be accurate)
        async with self.lock:
            if message.content.strip().isdigit():  # Is a number
                current_number = int(message.content.strip())
                expected_number = self.last_number + 1

                if current_number == expected_number:  # They can count!
                    self.last_number = current_number
                    self.last_message = message
                    return await message.add_reaction('✅')
                else:  # They can't count :(
                    await message.add_reaction('❌')

                    # Grace period for when people send the same number at the same time
                    if current_number == self.last_number and message.author.id != self.last_message.author.id and (
                            message.created_at - self.last_message.created_at
                    ).total_seconds() <= DUPLICATE_GRACE:
                        return await message.reply(embed=discord.Embed(
                            title="That doesn't look right, but I'll give you a chance...",
                            description=f"{message.author.mention} sent a duplicate number, but within the grace period. "
                                        f"The count is still at **{self.last_number:,d}**.",
                            colour=discord.Colour.yellow()
                        ))

                    embed = discord.Embed(
                        title="That doesn't look right! Better luck next time :)",
                        description=f"{message.author.mention} ruined the count at **{self.last_number:,d}**. Next number is **1**.\n\n"
                                    "*If this detection appears incorrect, please report it to the bot development team.*",
                        colour=discord.Colour.red()
                    )
                    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                    embed.set_thumbnail(
                        url="https://img-os-static.hoyolab.com/communityWeb/upload/19dacf2bf7dad6cea3b4a1d8d68045a0.png"
                    )
                    self.last_number = 0
                    self.last_message = await message.channel.send(content="0", embed=embed)  # "0" content allows for count detection on restart
                    return
            else:  # Not a number
                # We are resending the message as our own embed to allow for the restatement of the number (so it doesn't get lost)
                embed = discord.Embed(description=message.content)
                embed.set_author(name=f"{message.author.display_name} ({message.author.id})", icon_url=message.author.display_avatar.url)
                embed.add_field(name="​", value=f"*The count is currently at: **`{self.last_number}`***")
                await message.delete()
                return await message.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Counting(bot))
