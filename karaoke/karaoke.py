import json
import os

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel
from typing import Union

EVENT_STAFF = 1086023819073962086  # Event Staff Role
PERMISSION_LEVEL = PermissionLevel.SUPPORTER  # Alternate Permission Level
BAN_LIST_FILE = os.path.dirname(__file__) + "/banlist.json"


def role_or_perm(role: int, perm: PermissionLevel):
    """
    Decorator to check for either a role OR a PermissionLevel.
    Because apparently commands.check_any causes the default PermissionLevel check to break.

    As MM doesn't support local modules, copy this around as needed (I hate this too)
    """

    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author) or ctx.author.id == ctx.bot.user.id:
            # Bot owner(s) (and creator) has absolute power over the bot
            return True

        if ctx.author.get_role(role):
            return True

        if (
                perm is not PermissionLevel.OWNER
                and ctx.channel.permissions_for(ctx.author).administrator
                and ctx.guild == ctx.bot.modmail_guild
        ):
            # Administrators have permission to all non-owner commands in the Modmail Guild
            return True

        checkables = {*ctx.author.roles, ctx.author}
        level_permissions = ctx.bot.config["level_permissions"]

        for level in PermissionLevel:
            if level >= perm and level.name in level_permissions:
                # -1 is for @everyone
                if -1 in level_permissions[level.name] or any(
                        str(check.id) in level_permissions[level.name] for check in checkables
                ):
                    return True
        return False

    return commands.check(predicate)


def event_only(func: callable):
    """Decorator for button functions to check for event staff, equivalent, or higher permissions."""

    async def wrapper(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            member = interaction.user if isinstance(interaction.user, discord.Member) else interaction.guild.get_member(
                interaction.user.id)
        except (Exception,):
            return await interaction.channel.send("Something went wrong. Please try again.")
        has_perms = member.get_role(EVENT_STAFF) or await self.bot.is_owner(
            member) or member.id == self.bot.user.id or (
                            PERMISSION_LEVEL is not PermissionLevel.OWNER and
                            interaction.channel.permissions_for(member).administrator and
                            interaction.guild == self.bot.modmail_guild
                    )
        if not has_perms:
            checkables = {*member.roles, member}
            level_permissions = self.bot.config["level_permissions"]

            for level in PermissionLevel:
                if level >= PERMISSION_LEVEL and level.name in level_permissions:
                    # -1 is for @everyone
                    if -1 in level_permissions[level.name] or any(
                            str(check.id) in level_permissions[level.name] for check in checkables
                    ):
                        has_perms = True
                        break

        if has_perms:
            return await func(self, interaction, button)
        else:
            return await interaction.response.send_message(content="You do not have permission to use this.",
                                                           ephemeral=True)

    return wrapper


class KaraokeQueueView(discord.ui.View):
    def __init__(self, bot: commands.Bot, timeout: int, message: discord.Message, queue_list: dict, ban_list: list):
        super().__init__(timeout=timeout)
        self.bot = bot  # Bot instance
        self.message = message  # Message the view is attached to
        self.current: Union[discord.Member, None] = None  # Current singer
        self.queue_list = queue_list  # List of queues, so that we can remove ourselves from it
        self.ban_list = ban_list  # List of banned users

        # List of user IDs that have already gone and should be crossed out
        self.q_priority_history: list[int] = []
        self.q_requeue_history: list[int] = []

        # List of user IDs that are set to go next in their respective queues
        self.q_priority: list[int] = []
        self.q_requeue: list[int] = []

        # User ID will be added to this set if they have already had priority
        self.had_priority = set()

        # Generates row entries for the queue embed
        self._row_func = lambda id_, went: f"~~<@{id_}>~~" if went else f"<@{id_}>"

    def is_current(self, member_id: int) -> bool:
        return self.current is not None and member_id == self.current.id

    async def generate_queue(self):
        embed = discord.Embed(
            title=':microphone: Karaoke',
            colour=discord.Colour.blue()
        )

        embed.add_field(name="Priority Queue", value="\n".join(
            [self._row_func(i, True) for i in self.q_priority_history] +
            ([] if self.current is None or self.current.id in self.had_priority
             else [f"**{self.current.mention}** 🎤 "]) +
            [self._row_func(i, False) for i in self.q_priority]
        ))
        embed.add_field(name="Requeue", value="\n".join(
            [self._row_func(i, True) for i in self.q_requeue_history] +
            ([] if self.current is None or self.current.id not in self.had_priority
             else [f"**{self.current.mention}** 🎤 "]) +
            [self._row_func(i, False) for i in self.q_requeue]
        ))

        return embed

    async def _next(self, send_message: bool = True):
        """Go to the next singer in the queue, if none, removes current singer. Returns whether this was successful."""
        if self.current is not None:
            if self.current.id in self.had_priority:
                if self.current.id in self.q_requeue_history:
                    self.q_requeue_history.remove(self.current.id)
                self.q_requeue_history.append(self.current.id)
            else:
                self.q_priority_history.append(self.current.id)
                self.had_priority.add(self.current.id)

        if len(self.q_priority) > 0:
            self.current = self.q_priority.pop(0)
        elif len(self.q_requeue) > 0:
            self.current = self.q_requeue.pop(0)
        else:
            self.current = None
            return False

        try:
            self.current = self.message.guild.get_member(self.current)
        except (Exception,):
            self.current = None
            if send_message:
                await self.message.channel.send("An error occurred while getting the next singer, please try again.")
            return False
        if send_message:
            await self.message.channel.send(embed=discord.Embed(
                description=f"{self.current.mention} is now up!\n\n[Jump to Queue]({self.message.jump_url})",
                colour=discord.Colour.random()
            ))
        return True

    async def on_timeout(self):
        del self.queue_list[self.message.id]
        self.stop()
        await self.message.edit(view=None)

    # JOIN
    @discord.ui.button(label='Join', style=discord.ButtonStyle.blurple, emoji="<:lamesticker:1116535025098297426>")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a member to join the queue."""
        if interaction.user.id in self.ban_list:
            return await interaction.response.send_message(
                content="You have been banned from joining karaoke queues! Contact an event team member if you believe "
                        "this is a mistake.",
                ephemeral=True
            )
        elif interaction.user.id in self.q_priority or interaction.user.id in self.q_requeue or \
                self.is_current(interaction.user.id):
            return await interaction.response.send_message(content="You're already in the queue!", ephemeral=True)
        elif interaction.user.id in self.had_priority:
            self.q_requeue.append(interaction.user.id)
        else:
            self.q_priority.append(interaction.user.id)

        await interaction.response.send_message(content="You've been added to the queue!", ephemeral=True)
        await self.message.edit(embed=await self.generate_queue())

    # LEAVE
    @discord.ui.button(label='Leave', style=discord.ButtonStyle.danger, emoji="<:bruh:1089823209660092486>")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a member to leave the queue."""
        if self.is_current(interaction.user.id):
            await self._next()
        elif interaction.user.id in self.q_priority:
            self.q_priority.remove(interaction.user.id)
        elif interaction.user.id in self.q_requeue:
            self.q_requeue.remove(interaction.user.id)
        else:
            return await interaction.response.send_message(content="You're not in the queue!", ephemeral=True)

        await interaction.response.send_message(content="You've been removed from the queue!", ephemeral=True)
        await self.message.edit(embed=await self.generate_queue())

    # NEXT - STAFF ONLY
    @discord.ui.button(label='Next', style=discord.ButtonStyle.success, emoji="<:seelejoy:1085986027115663481>")
    @event_only
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Moves to the next person in the queue."""
        if not await self._next():
            await interaction.response.send_message(content="There's no one next in the queue!", ephemeral=True)
        await self.message.edit(embed=await self.generate_queue())
        await interaction.response.defer()

    @discord.ui.button(label='Reset', style=discord.ButtonStyle.grey, emoji="<:seeleomg:1085605320065302630>")
    @event_only
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reset button, clears the queue."""
        del self.queue_list[self.message.id]
        self.stop()
        await self.message.edit(view=None)
        await interaction.response.defer()


class Karaoke(commands.Cog):
    """Karaoke Queueing System"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_queues = {}

        if not os.path.isfile(BAN_LIST_FILE):
            with open(BAN_LIST_FILE, "w") as f:
                json.dump([], f)
            self.ban_list = []
        else:
            with open(BAN_LIST_FILE, "r") as f:
                self.ban_list = json.load(f)

    @commands.command(aliases=['karaokeq', 'kq'])
    @role_or_perm(role=EVENT_STAFF, perm=PERMISSION_LEVEL)
    async def karaokequeue(self, ctx: commands.Context, timeout: int = 86400):
        """Starts a karaoke queue in the current channel. Timeout is in seconds. Default is 24 hours."""
        message = await ctx.send("Generating queue...")
        view = KaraokeQueueView(self.bot, timeout, message, self.current_queues, self.ban_list)
        self.current_queues[message.id] = view
        await message.edit(content="", view=view, embed=await view.generate_queue())

    @commands.command(aliases=["kevict"])
    @role_or_perm(role=EVENT_STAFF, perm=PERMISSION_LEVEL)
    async def karaokeevict(self, ctx: commands.Context, member: discord.Member, queue_message: discord.Message = None):
        """Evicts a member from a queue. Either reply to the message, or pass the message ID. Passing takes priority."""
        if queue_message is None:
            if ctx.message.reference is not None:
                queue_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            else:
                return await ctx.reply("Please either reply to the message containing the queue, or pass in the "
                                       "message link or ID.")

        if queue_message is None or queue_message.author.id != self.bot.user.id or \
                queue_message.id not in self.current_queues:
            return await ctx.reply(
                "Invalid message, please ensure you are providing the message containing the queue in which you want "
                "the user evicted from.")

        view = self.current_queues[queue_message.id]

        changed = False
        if view.is_current(member.id):
            # noinspection PyProtectedMember
            await view._next()
            changed = True
        elif member.id in view.q_priority:
            view.q_priority.remove(member.id)
            changed = True
        elif member.id in view.q_requeue:
            view.q_requeue.remove(member.id)
            changed = True

        if not changed:
            return await ctx.reply("That user is not in the queue.")

        await view.message.edit(embed=await view.generate_queue())
        await ctx.reply(f"Evicted `{member.display_name}` from the queue.")

    @commands.command(aliases=["kcleanse"])
    @role_or_perm(role=EVENT_STAFF, perm=PERMISSION_LEVEL)
    async def karaokecleanse(self, ctx: commands.Context, member: discord.Member, queue_message: discord.Message = None):
        """
        Cleanses a member from the queue (removes from both history and next up).
        Either reply to the message, or pass the message ID. Passing takes priority
        """
        if queue_message is None:
            if ctx.message.reference is not None:
                queue_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            else:
                return await ctx.reply("Please either reply to the message containing the queue, or pass in the "
                                       "message link or ID.")

        if queue_message is None or queue_message.author.id != self.bot.user.id or \
                queue_message.id not in self.current_queues:
            return await ctx.reply(
                "Invalid message, please ensure you are providing the message containing the queue in which you want "
                "the user cleansed from.")

        view = self.current_queues[queue_message.id]

        changed = False
        if view.is_current(member.id):
            # noinspection PyProtectedMember
            await view._next()
            changed = True
        if member.id in view.q_priority_history:
            view.q_priority_history.remove(member.id)
            changed = True
        if member.id in view.q_requeue_history:
            view.q_requeue_history.remove(member.id)
            changed = True

        if member.id in view.q_priority:
            view.q_priority.remove(member.id)
            changed = True
        elif member.id in view.q_requeue:
            view.q_requeue.remove(member.id)
            changed = True

        if not changed:
            return await ctx.reply("That user is not in the queue.")

        await view.message.edit(embed=await view.generate_queue())
        await ctx.reply(f"Cleansed `{member.display_name}` from the queue.")

    @commands.command(aliases=["kban"])
    @role_or_perm(role=EVENT_STAFF, perm=PERMISSION_LEVEL)
    async def karaokeban(self, ctx: commands.Context, member: discord.Member):
        """Ban a user from joining queues."""
        if member.id in self.ban_list:
            return await ctx.reply("That user is already banned.")

        self.ban_list.append(member.id)
        with open(BAN_LIST_FILE, "w") as f:
            json.dump(self.ban_list, f)

        for queue in self.current_queues.values():
            changed = False

            if queue.is_current(member.id):
                # noinspection PyProtectedMember
                await queue._next()
                changed = True
            if member.id in queue.q_priority_history:
                queue.q_priority_history.remove(member.id)
                changed = True
            if member.id in queue.q_requeue_history:
                queue.q_requeue_history.remove(member.id)
                changed = True

            if member.id in queue.q_priority:
                queue.q_priority.remove(member.id)
                changed = True
            elif member.id in queue.q_requeue:
                queue.q_requeue.remove(member.id)
                changed = True

            if changed:
                await queue.message.edit(embed=await queue.generate_queue())

        await ctx.reply(f"Banned `{member.display_name}` from joining queues, and evicted from all current queues.")

    @commands.command(aliases=["kunban"])
    @role_or_perm(role=EVENT_STAFF, perm=PERMISSION_LEVEL)
    async def karaokeunban(self, ctx: commands.Context, member: discord.Member):
        """Unban a user from joining queues."""
        if member.id not in self.ban_list:
            return await ctx.reply("That user is not banned.")

        self.ban_list.remove(member.id)
        with open(BAN_LIST_FILE, "w") as f:
            json.dump(self.ban_list, f)

        await ctx.reply(f"Unbanned `{member.display_name}` from joining queues.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def karaokebanlistrefresh(self, ctx: commands.Context):
        """Refreshes the ban list from the file, only use if you know exactly what you're doing."""
        # Remove all entries from the current ban list, then re-add from file. This is because we are passing in
        # references to all the karaoke views, replacing the list will not update the references.
        self.ban_list.clear()
        with open(BAN_LIST_FILE, "r") as f:
            for i in json.load(f):
                self.ban_list.append(i)

        await ctx.reply("Ban list refreshed.")


async def setup(bot):
    await bot.add_cog(Karaoke(bot))
