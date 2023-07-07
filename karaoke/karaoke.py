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
        member = interaction.user if isinstance(interaction.user, discord.Member) else interaction.guild.get_member(
            interaction.user.id)
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
            return await interaction.response.send_message(content="You do not have permissions to use this.",
                                                           ephemeral=True)

    return wrapper


class KaraokeQueueView(discord.ui.View):
    def __init__(self, bot: commands.Bot, timeout: int, message: discord.Message, queue_list: list, ban_list: list):
        super().__init__(timeout=timeout)
        self.bot = bot  # Bot instance
        self.message = message  # Message the view is attached to
        self.current: Union[discord.Member, None] = None  # Current singer
        self.queue_list = queue_list  # List of queues, so that we can remove ourselves from it
        self.ban_list = ban_list  # List of banned users

        # Sets of user IDs that have already gone and should be crossed out
        self.q_priority_history: set[int] = set()
        self.q_normal_history: set[int] = set()

        # Sets of user IDs that are set to go next in their respective queues
        self.q_priority: set[int] = set()
        self.q_normal: set[int] = set()

        # User ID will be added to this set if they have already had priority
        self.had_priority = set()

    def _row_func(self, id_: int, went: bool) -> str:
        """Returns a string for a row in the queue."""
        if self.is_current(id_):
            return f"🎙️ **<@{id_}>**"
        elif went:
            return f'~~<@{id_}>~~'
        else:
            return f"<@{id_}>"

    def is_current(self, member_id: int) -> bool:
        return self.current is not None and member_id == self.current.id

    async def generate_queue(self):
        embed = discord.Embed(
            title=':microphone: Karaoke',
            colour=discord.Colour.blue()
        )

        embed.add_field(name="Priority Queue", value="\n".join(
            [self._row_func(i, True) for i in self.q_priority_history] +
            [self._row_func(i, False) for i in self.q_priority]
        ))
        embed.add_field(name="Normal Queue", value="\n".join(
            [self._row_func(i, True) for i in self.q_normal_history] +
            [self._row_func(i, False) for i in self.q_normal]
        ))

        return embed

    async def _next(self):
        """Go to the next singer in the queue, if none, removes current singer. Returns whether this was successful."""
        if len(self.q_priority) > 0:
            new = self.q_priority.pop()
            self.q_priority_history.add(new)
        elif len(self.q_normal) > 0:
            new = self.q_normal.pop()
            if new in self.q_normal_history:
                self.q_normal_history.remove(new)
            self.q_normal_history.add(new)
        else:
            self.current = None
            return False

        self.current = self.message.guild.get_member(new)
        return True

    async def on_timeout(self):
        self.queue_list.remove(self)
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
        elif interaction.user.id in self.q_priority or interaction.user.id in self.q_normal:
            return await interaction.response.send_message(content="You're already in the queue!", ephemeral=True)
        elif interaction.user.id in self.had_priority:
            self.q_normal.add(interaction.user.id)
        else:
            self.q_priority.add(interaction.user.id)
            self.had_priority.add(interaction.user.id)

        await interaction.response.send_message(content="You've been added to the queue!", ephemeral=True)
        await self.message.edit(embed=await self.generate_queue())

    # LEAVE
    @discord.ui.button(label='Leave', style=discord.ButtonStyle.danger, emoji="<:bruh:1089823209660092486>")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a member to leave the queue."""
        if self.is_current(interaction.user.id):
            await self._next()

        if interaction.user.id in self.q_priority:
            self.q_priority.remove(interaction.user.id)
        elif interaction.user.id in self.q_normal:
            self.q_normal.remove(interaction.user.id)
        else:
            return await interaction.response.send_message(content="You're not in the queue!", ephemeral=True)

        await interaction.response.send_message(content="You've been removed from the queue!", ephemeral=True)
        await self.message.edit(embed=await self.generate_queue())

    # NEXT - STAFF ONLY
    @discord.ui.button(label='Next', style=discord.ButtonStyle.success, emoji="<:seelejoy:1085986027115663481>")
    @event_only
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Moves to the next person in the queue."""
        if await self._next():
            embed = discord.Embed(description=f"{self.current.mention} is now up!", colour=discord.Colour.random())
            embed.set_footer(text=f"[Jump to Queue]({self.message.jump_url})")
            await interaction.channel.send(embed=embed)
        else:
            await interaction.response.send_message(content="There's no one next in the queue!", ephemeral=True)
        await interaction.response.edit_message(embed=await self.generate_queue())

    @discord.ui.button(label='Reset', style=discord.ButtonStyle.grey, emoji="<:seeleomg:1085605320065302630>")
    @event_only
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reset button, clears the queue."""
        self.queue_list.remove(self)
        self.stop()
        await self.message.edit(view=None)
        await interaction.response.defer()


class Karaoke(commands.Cog):
    """Karaoke Queueing System"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_queues = []

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
        self.current_queues.append(view)
        await message.edit(content="", view=view, embed=await view.generate_queue())

    @commands.command(aliases=["kevict"])
    @role_or_perm(role=EVENT_STAFF, perm=PERMISSION_LEVEL)
    async def karaokeevict(self, ctx: commands.Context, member: discord.Member, queue_message: discord.Message = None):
        """Evicts a member from a queue. Either reply to the message, or pass the message ID. Passing takes priority."""
        if queue_message is None:
            if ctx.message.interaction is not None:
                queue_message = await ctx.channel.fetch_message(ctx.message.interaction.message.id)
            else:
                return await ctx.reply("Please either reply to the message containing the queue, or pass in the "
                                       "message link or ID.")

        if queue_message is None or queue_message.author.id != self.bot.user.id or queue_message.view is None \
                or not isinstance(queue_message.view, KaraokeQueueView):
            return await ctx.reply(
                "Invalid message, please ensure you are providing the message containing the queue in which you want "
                "the user evicted from.")

        view = queue_message.view

        changed = False
        if view.is_current(member.id):
            # noinspection PyProtectedMember
            await view._next()
            changed = True
        if member.id in view.q_priority_history:
            view.q_priority_history.remove(member.id)
            changed = True
        if member.id in view.q_normal_history:
            view.q_normal_history.remove(member.id)
            changed = True

        if member.id in view.q_priority:
            view.q_priority.remove(member.id)
            changed = True
        elif member.id in view.q_normal:
            view.q_normal.remove(member.id)
            changed = True

        if not changed:
            return await ctx.reply("That user is not in the queue.")

        await view.message.edit(embed=await view.generate_queue())
        await ctx.reply(f"Evicted `{member.display_name}` from the queue.")

    @commands.command(aliases=["kban"])
    @role_or_perm(role=EVENT_STAFF, perm=PERMISSION_LEVEL)
    async def karaokeban(self, ctx: commands.Context, member: discord.Member):
        """Ban a user from joining queues."""
        if member.id in self.ban_list:
            return await ctx.reply("That user is already banned.")

        self.ban_list.append(member.id)
        with open(BAN_LIST_FILE, "w") as f:
            json.dump(self.ban_list, f)

        for queue in self.current_queues:
            changed = False

            if queue.is_current(member.id):
                # noinspection PyProtectedMember
                await queue._next()
                changed = True
            if member.id in queue.q_priority_history:
                queue.q_priority_history.remove(member.id)
                changed = True
            if member.id in queue.q_normal_history:
                queue.q_normal_history.remove(member.id)
                changed = True

            if member.id in queue.q_priority:
                queue.q_priority.remove(member.id)
                changed = True
            elif member.id in queue.q_normal:
                queue.q_normal.remove(member.id)
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
    async def karaokebanlistrefresh(self):
        """Refreshes the ban list from the file, only use if you know exactly what you're doing."""
        # Remove all entries from the current ban list, then re-add from file. This is because we are passing in
        # references to all the karaoke views, replacing the list will not update the references.
        self.ban_list.clear()
        with open(BAN_LIST_FILE, "r") as f:
            for i in json.load(f):
                self.ban_list.append(i)


async def setup(bot):
    await bot.add_cog(Karaoke(bot))
