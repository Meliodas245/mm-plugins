import asyncio

import discord
from discord.ext import commands

COUNTING_CHANNEL = 1162804188800102501
DUPLICATE_GRACE = 0.75  # Time in seconds to be lenient to duplicate messages


def set_embed_author(embed: discord.Embed, member: discord.Member):
    """Sets the author field for an embed from a member object, following a predefined format.

    :param embed: Embed to set the author for
    :param member: Member object you want to get the data from
    """
    embed.set_author(name=f"{member.display_name} ({member.id})", icon_url=member.display_avatar.url)


class Counting(commands.Cog):
    """Counting Plugin"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_number = 0
        self.last_message = None  # For use in detecting notable message edits & deletes
        self.lock = asyncio.Lock()  # To prevent dual-processing edge-cases

    async def fail(self, title: str, message: discord.Message):
        """Method to send a count-failed message with a customizable title.

        :param title: Title to use for the count-failed embed
        :param message: Message that resulted in the count-fail
        """
        await message.add_reaction('❌')
        embed = discord.Embed(
            title=title,
            description=f"{message.author.mention} ruined the count at **{self.last_number:,d}**. Next number is **1**.\n\n"
                        "*If this detection appears incorrect, please report it to the bot development team.*",
            colour=discord.Colour.red()
        )
        embed.set_thumbnail(
            url="https://img-os-static.hoyolab.com/communityWeb/upload/19dacf2bf7dad6cea3b4a1d8d68045a0.png"
        )
        set_embed_author(embed, message.author)
        self.last_number = 0
        self.last_message = await message.channel.send(content="0", embed=embed)  # "0" content allows for count detection on restart
        return

    @commands.Cog.listener("on_message")
    async def counting_on_message(self, message: discord.Message):
        """on_message event handler to allow for detection and handling of counting messages"""
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

                if current_number != expected_number:  # They can't count :(
                    # Grace period for when people send the same number at the same time
                    if current_number == self.last_number and message.author.id != self.last_message.author.id and (
                            message.created_at - self.last_message.created_at
                    ).total_seconds() <= DUPLICATE_GRACE:
                        await message.add_reaction('❌')
                        return await message.reply(embed=discord.Embed(
                            title="That doesn't look right, but I'll give you a chance...",
                            description=f"{message.author.mention} sent a duplicate number, but within the grace period. "
                                        f"The count is still at **{self.last_number:,d}**.",
                            colour=discord.Colour.yellow()
                        ))
                    return await self.fail("That doesn't look right! Better luck next time :)", message)
                elif message.author.id == self.last_message.author.id:  # They're trying to count by themselves!
                    return await self.fail("You can't count twice in a row!", message)
                elif self.last_message.author.id == self.bot.user.id and len(self.last_message.embeds) > 0:
                    embed = self.last_message.embeds[0]
                    if ("editing" in embed.description or "deleting" in embed.description
                    ) and str(message.author.id) in embed.author.name:  # Not a edit/delete message resulting from them
                        await message.reply(
                            content="Don't try to edit or delete your messages to get around detections please.\n"
                                    "If you're seeing this by pure coincidence, don't worry about it.",
                            delete_after=10
                        )
                        return await self.fail("You can't count twice in a row!", message)

                # They can count!
                self.last_number = current_number
                self.last_message = message
                return await message.add_reaction('✅')
            else:  # Not a number
                # We are resending the message as our own embed to allow for the restatement of the number (so it doesn't get lost)
                embed = discord.Embed(description=message.content, colour=discord.Colour.light_gray())
                embed.add_field(name="​", value=f"*The count is currently at: **`{self.last_number}`***")
                set_embed_author(embed, message.author)
                await message.delete()
                return await message.channel.send(embed=embed)

    @commands.Cog.listener("on_message_edit")
    async def counting_on_message_edit(self, before: discord.Message, after: discord.Message):
        """on_message_edit event handler to allow for handling of counting message edits"""
        if not self.last_message or before.id != self.last_message.id:
            return

        embed = discord.Embed(
            description=f"{before.author.mention} tried editing their message...\n\n"
                        f"The count is currently at: **`{self.last_number}`**",
            colour=discord.Colour.green()
        )
        set_embed_author(embed, before.author)
        self.last_message = await before.channel.send(content=str(self.last_number), embed=embed)
        await before.delete()

    @commands.Cog.listener("on_message_delete")
    async def counting_on_message_delete(self, message: discord.Message):
        """on_message_delete event handler to allow for handling of counting message deletions"""
        if not self.last_message or message.id != self.last_message.id:
            return

        embed = discord.Embed(
            description=f"{message.author.mention} tried deleting their message...\n\n"
                        f"The count is currently at: **`{self.last_number}`**",
            colour=discord.Colour.dark_green()
        )
        set_embed_author(embed, message.author)
        self.last_message = await message.channel.send(content=str(self.last_number), embed=embed)


async def setup(bot):
    await bot.add_cog(Counting(bot))
