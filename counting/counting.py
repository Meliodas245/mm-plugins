import ast
import asyncio
import math
import operator as op
import re
import warnings
from concurrent.futures import TimeoutError

import discord
import simpleeval
from discord.ext import commands
from pebble import concurrent

VERSION = "2.1.0"
COUNTING_CHANNEL = 1162804188800102501
DEVELOPER_ROLE = 1087928500893265991
EVALUATION_TIMEOUT = 2  # Time in seconds after which to timeout
DUPLICATE_GRACE = 0.75  # Time in seconds to be lenient to duplicate messages
CODE_BLOCK_REGEX = re.compile(
    r"(?P<delim>(?P<block>```)|``?)(?(block)(?:(?P<lang>[a-z]+)\n)?)(?:[ \t]*\n)*(?P<code>.*?)\s*(?P=delim)",
    re.DOTALL | re.IGNORECASE,
)  # Regex to detect and extra code from Discord code blocks

# Create and configure SimpleEval parser to handle expressions
s = simpleeval.SimpleEval()
del s.operators[
    ast.BitXor
]  # ^ symbol, which people may confuse for ** (would override, but syntax is slightly diff)
del s.operators[ast.BitOr]  # | symbol, which people may confuse for abs
del s.functions[
    "rand"
]  # Randomly generates numbers, would cause griefs more often than not
del s.functions[
    "randint"
]  # Randomly generates numbers, would cause griefs more often than not
s.functions.update(  # Add additional functions
    floor=math.floor,
    rounddown=math.floor,
    round_down=math.floor,
    ceil=math.ceil,
    roundup=math.ceil,
    round_up=math.ceil,
    round=round,
    sqrt=math.sqrt,
    sqroot=math.sqrt,
    squareroot=math.sqrt,
    sin=lambda x: math.sin(
        math.radians(x)
    ),  # sin takes radians, input as degrees is simpler, so convert deg -> rad
    cos=lambda x: math.cos(
        math.radians(x)
    ),  # cos takes radians, input as degrees is simpler, so convert deg -> rad
    tan=lambda x: math.tan(
        math.radians(x)
    ),  # tan takes radians, input as degrees is simpler, so convert deg -> rad
    degrees=math.degrees,  # Offer rad -> deg conversion
    radians=math.radians,  # Offer deg -> rad conversion
    abs=abs,
    bitxor=op.xor,  # Reimplement bitwise XOR (^), which was removed to curb symbol confusion
    bitor=op.or_,  # Reimplement bitwise OR (|), which was removed to curb symbol confusion,
    log=lambda x, base=10: math.log(x, base),  # Log with default base 10
    ln=math.log,  # Default math.log (base e)
)
s.names.update(  # Add additional variables
    pi=math.pi,
    e=math.e,
)
simpleeval.MAX_POWER = (
    10000  # We're never getting that far (prevents timely exponent operations)
)
simpleeval.MAX_STRING_LENGTH = (
    10000  # Shouldn't be using strings much anyway (prevents memory exhaustion)
)


def set_embed_author(embed: discord.Embed, member: discord.Member) -> discord.Embed:
    """Sets the author field for an embed from a member object, following a predefined format.

    :param embed: Embed to set the author for
    :param member: Member object you want to get the data from
    :return: Embed, to allow for quick-creations
    """
    embed.set_author(
        name=f"{member.display_name} ({member.id})", icon_url=member.display_avatar.url
    )
    return embed


def set_embed_footer(embed: discord.Embed, additional: str = None) -> discord.Embed:
    """Sets the footer field for an embed, following a predefined format.

    :param embed: Embed to set the footer for
    :param additional: Additional text to add to the end of the footer
    :return: Embed, to allow for quick-creations
    """
    text = f"Counting Plugin v{VERSION}"
    if additional:
        text += f"| {additional}"
    embed.set_footer(text=text)
    return embed


def set_embed_author_footer(
    embed: discord.Embed, member: discord.Member, additional: str = None
) -> discord.Embed:
    """Combination of set_embed_author and set_embed_footer, for quick-creations

    :param embed: Embed to set the author and footer for
    :param member: Member to use for set_embed_author
    :param additional: Additional text for set_embed_footer
    :return: Embed, to allow for quick-creations
    """
    return set_embed_footer(set_embed_author(embed, member), additional)


def get_exp_code(exp):
    """Place an expression into a code-block, escaping as needed."""
    return f"```py\n{exp.replace('`', '[backtick]')}\n```"


async def expression_reply(
    message: discord.Message, exp: str, content: str, delete_after=15, **kwargs
):
    """Send a reply to a message, including an expression at the top of the message. Commonly used for fail-evaluate notices.

    :param message: Message to reply to
    :param exp: Expression to include
    :param content: Additional message content
    :param delete_after: Relayed to message.reply(), default 15 seconds
    :param kwargs: kwargs to relay to message.reply()
    :return: Replied message object
    """
    return await message.reply(
        embed=set_embed_footer(
            discord.Embed(
                description=f"{get_exp_code(exp)}\n{content}",
                colour=discord.Colour.dark_grey(),
            ),
            f"This message will delete itself in {delete_after} seconds.",
        ),
        delete_after=delete_after,
        **kwargs,
    )


@concurrent.process(timeout=EVALUATION_TIMEOUT)
def safe_eval(string: str):
    """Safely run simpleeval's parser, with a backup timeout (via Pebble)

    :param string: String to evaluate (passed into simpleeval)
    :return: Result of expression, and any warnings raised if successful (tuple)
    :raises concurrent.futures.TimeoutError: Exception raised upon timeout
    :raises Exception: Any exceptions raised by the parser
    """
    with warnings.catch_warnings(record=True) as ws:
        return s.eval(string), ws


async def get_num(message: discord.Message, reply: bool = False):
    """Get a number from a user input, potentially containing mathematical expressions.

    :param message: Message to get the input from
    :param reply: Whether to reply to the user with details in select fail-evaluate circumstances
    :return: Number if successful, None if unsuccessful
    """
    simple_contents = message.content.strip().replace(",", "")
    if simple_contents.isdigit():
        return int(simple_contents)

    match = CODE_BLOCK_REGEX.match(message.content)
    if match:
        content = match.group("code")
    else:
        content = message.content
    fail_msg = None
    try:
        eval_output, ws = safe_eval(content).result()
        # Handle all warnings
        for w in ws:
            if w.category in [
                simpleeval.AssignmentAttempted,
                simpleeval.MultipleExpressions,
            ]:
                await expression_reply(
                    message,
                    content,
                    f"```py\n{w.message.replace('`', '[backtick]')}```",
                )

        if isinstance(eval_output, float):
            if eval_output.is_integer():  # Float type, but whole number
                eval_output = int(
                    eval_output
                )  # Convert to integer so it succeeds int check later
            else:  # Float type, not a whole number
                if reply:
                    await expression_reply(
                        message,
                        content,
                        f"= *`{eval_output}`*\n\nTo prevent unexpected behaviour, I do not automatically convert "
                        "decimal numbers to whole numbers. You can do this yourself with:\n"
                        "- `int(your content)`: Truncates (ignores all decimals)\n"
                        "- `floor(your content)`: Rounds down\n"
                        "- `ceil(your content)`: Rounds up\n"
                        "- `round(your content)`: Rounds (<= 0.5 down, > 0.5 up)\n"
                        "- `dividend//divisor`: Floor division, divides then rounds down (truncates)",
                        delete_after=30,
                    )
                return None

        if isinstance(eval_output, int):
            return eval_output
    except TimeoutError:
        fail_msg = (
            "Too much math!\n*(Something in your expression is taking too long to evaluate)*\n\n"
            "**If you are seeing this message, please report the expression you used to the bot development team.**"
        )
    except simpleeval.NumberTooHigh:
        fail_msg = (
            "Why don't you try and calculate that?\n*(A number in your expression is too big -- "
            "some operations have size limits to prevent time-expensive operations)*"
        )
    except simpleeval.IterableTooLong:
        fail_msg = (
            "An iterable in your expression is way too big -- there are size limits to prevent "
            "memory-expensive operations"
        )
    except simpleeval.FunctionNotDefined as e:
        fail_msg = f"The function `{getattr(e, 'func_name').replace('`', '[backtick]')}` does not exist."
    except simpleeval.OperatorNotDefined as e:
        try:
            op_name = e.attr.__class__.__name__
            fail_msg = f"The operator `{op_name}` does not exist."
            if op_name == "BitXor":
                fail_msg += "\nTo perform a power operation, use `**` instead of `^`."
            elif op_name == "BitOr":
                fail_msg += "\nTo get an absolute value, use `abs(content here)` instead of `|content here|`."
        except (Exception,):
            fail_msg = None
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError) as e:
        fail_msg = f"```py\n{repr(e).replace('`', '[backtick]')}\n```"
    except (Exception,):
        pass
    if reply and fail_msg is not None:
        await expression_reply(message, content, fail_msg)
    return None


class Counting(commands.Cog):
    """Counting Plugin"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel = bot.get_channel(COUNTING_CHANNEL)
        self.last_number = None
        self.last_message = (
            None  # DO NOT RELY ON FOR CURRENT #, use self.last_number instead
        )
        self.lock = asyncio.Lock()  # To prevent dual-processing edge-cases
        self.bot.loop.create_task(
            self.async_init()
        )  # Run async_init, which performs async setup tasks

    async def async_init(self):
        """Perform asynchronous actions when the Cog initializes"""
        async with self.lock:
            await self.assert_last(only_history=True)

    def get_representation(self):
        """Get a representation of the last number, returning the number itself by default, but a code block
        instead for expressions, escaped as needed."""
        assert self.last_number is not None and self.last_message is not None
        self.last_message: discord.Message
        if (
            self.last_message.author.bot
            or str(self.last_number) == self.last_message.content
        ):
            # If last_number is last_message, then it's not an expression. If it's a bot, it's likely us (we don't do expressions)
            return f"**`{self.last_number:,d}`**"
        else:
            match = CODE_BLOCK_REGEX.match(self.last_message.content)
            if match:
                content = match.group("code")
            else:
                content = self.last_message.content
            return f"\n{get_exp_code(content)}\n"

    async def fail(self, title: str, message: discord.Message):
        """Method to send a count-failed message with a customizable title.

        :param title: Title to use for the count-failed embed
        :param message: Message that resulted in the count-fail
        """
        await message.add_reaction("❌")

        embed = discord.Embed(
            title=title,
            description=f"{message.author.mention} ruined the count at **{self.last_number:,d}**. Next number is **1**.\n\n"
            "*If this detection appears incorrect, please report it to the bot development team.*",
            colour=discord.Colour.red(),
        )
        embed.set_thumbnail(
            url="https://img-os-static.hoyolab.com/communityWeb/upload/19dacf2bf7dad6cea3b4a1d8d68045a0.png"
        )
        set_embed_author_footer(embed, message.author)

        self.last_number = 0
        self.last_message = await message.channel.send(
            content="0", embed=embed
        )  # "0" content allows for count recovery
        return

    async def assert_last(
        self, default_message: discord.Message = None, only_history: bool = False
    ):
        """
        Ensure that self.last_number and self.last_message exist. If they don't exist, the following will be done in order:

        1. Search previous 100 messages for counts
        2. If number in optionally provided message, assume that number is valid, and set last_number to be 1 before it
        3. Reset count to 0

        If this method is run, it can be guaranteed that self.last_number and self.last_message will exist in some form
        (except using only_history).

        :param default_message: Message to attempt to default to if search fails. Will not be included in history search.
        :param only_history: Whether to only attempt a history recover, if this is True, self.last_number and self.last_message cannot be guaranteed to exist.
        """
        if (
            self.last_number is not None and self.last_message is not None
        ):  # If they already exist, return
            return

        # Search last 100 messages (in order of most recent -> oldest) for a valid count
        async for message in self.channel.history(limit=100, oldest_first=False):
            if (
                default_message and message.id == default_message.id
            ):  # Do not include message provided as default
                continue
            if (
                message.author.bot and message.author.id != self.bot.user.id
            ):  # Bot that isn't us
                continue
            num = await get_num(message)
            if num is not None:
                self.last_number = num
                self.last_message = message
                if not any([i.me and i.emoji == "✅" for i in message.reactions]):
                    await message.add_reaction("✅")
                return

        if (
            only_history
        ):  # If we only want to search history, abandon the recovery process
            return

        if default_message:  # Check the default_message, if provided, for a valid count
            num = await get_num(default_message)
            if num is not None:
                self.last_number = num - 1
                self.last_message = await self.channel.send(
                    content="*Count Recovered - Ignore This Message*"
                )  # So double-count doesn't kick in
                return

        # All recovery steps failed, reset count to 0
        self.last_number = 0
        self.last_message = await self.channel.send(
            content="0",
            embed=set_embed_footer(
                discord.Embed(
                    title="Count Reset to 0",
                    description="I was unable to find any previous counting data, through any recovery method. As a result, "
                    "the count has been reset to 0. This should almost never happen, please contact a bot "
                    "developer if you see this in normal operational circumstances.\n\nNext number is **1**.",
                    colour=discord.Colour.red(),
                )
            ),
        )

    @commands.Cog.listener("on_message")
    async def counting_on_message(self, message: discord.Message):
        """on_message event handler to allow for detection and handling of counting messages"""
        if (
            not message.author or not message.author.guild or message.author.bot
        ):  # Irrelevant
            return
        if message.channel.id != COUNTING_CHANNEL:  # Not the counting channel
            return

        # Special Messages
        if message.content.lower() == "help":
            pass

        async with self.lock:  # Utilize async lock to prevent parallel message processing edge cases
            await self.assert_last(
                message
            )  # Ensure self.last_number and self.last_message exists
            current_number = await get_num(message, reply=True)
            if current_number is not None:  # Is a number
                expected_number = self.last_number + 1

                if current_number != expected_number:  # They can't count :(
                    # Grace period for when people send the same number at the same time
                    if (
                        current_number == self.last_number
                        and message.author.id != self.last_message.author.id
                        and (
                            message.created_at - self.last_message.created_at
                        ).total_seconds()
                        <= DUPLICATE_GRACE
                    ):
                        await message.add_reaction("❌")
                        return await message.reply(
                            embed=set_embed_footer(
                                discord.Embed(
                                    title="That doesn't look right, but I'll give you a chance...",
                                    description=f"{message.author.mention} sent a duplicate number, but within the grace period. "
                                    f"The count is still at {self.get_representation()} "
                                    f"(by {self.last_message.author.mention}).",
                                    colour=discord.Colour.yellow(),
                                )
                            )
                        )

                    return await self.fail(
                        "That doesn't look right! Better luck next time :)", message
                    )
                elif (
                    message.author.id == self.last_message.author.id
                ):  # They're trying to count by themselves!
                    return await self.fail("You can't count twice in a row!", message)
                elif (
                    self.last_message.author.id == self.bot.user.id
                    and len(self.last_message.embeds) > 0
                ):  # Self-count, but they're trying to avoid detection
                    embed = self.last_message.embeds[0]
                    if (
                        "editing" in embed.description
                        or "deleting" in embed.description
                    ) and str(
                        message.author.id
                    ) in embed.author.name:  # Not a edit/delete message resulting from them
                        await message.reply(
                            content="Don't try to edit or delete your messages to get around detections please.\n"
                            "If you're seeing this by pure coincidence, don't worry about it.",
                            delete_after=10,
                        )
                        return await self.fail(
                            "You can't count twice in a row!", message
                        )

                # They can count! - make sure any previous failing checks end with a return, or this code will run on a fail
                self.last_number = current_number
                self.last_message = message
                return await message.add_reaction("✅")
            else:  # Not a number
                # We're allowing bot developers to explicitly specify that their message should be ignored, for
                #  circumstances where message resend is not ideal (e.g. when the feature is broken, or for important
                #  announcements requiring a normal message)
                if message.content.startswith("//") and DEVELOPER_ROLE in [
                    i.id for i in message.author.roles
                ]:
                    return

                # We are resending the message as our own embed to allow for the restatement of the number (so it doesn't get lost)
                embed = discord.Embed(
                    description=message.content, colour=discord.Colour.light_gray()
                )
                embed.add_field(
                    name="​",  # Zero-width space for an empty field name (using field as footer doesn't allow MD formatting)
                    value=f"*The count is currently at:* {self.get_representation()} (*by {self.last_message.author.mention}*)",
                )
                set_embed_author_footer(embed, message.author)
                files = []
                if len(message.attachments) > 0:
                    for attach in message.attachments:
                        if (
                            not attach.content_type
                            or not attach.content_type.startswith("image/")
                        ):
                            continue
                        files.append(await attach.to_file())
                await message.delete()
                msg = await message.channel.send(
                    embed=embed,
                    reference=message.reference,
                    mention_author=False,
                    files=files,
                )
                return await msg.add_reaction(
                    "🗑️"
                )  # Make message user-deletable (via react)

    @commands.Cog.listener("on_message_edit")
    async def counting_on_message_edit(
        self, before: discord.Message, after: discord.Message
    ):
        """on_message_edit event handler to allow for handling of counting message edits"""
        if (
            before.channel.id != COUNTING_CHANNEL
        ):  # Check if we're in counting channel first, to prevent excessive locks
            return

        async with self.lock:  # Utilize async lock to prevent parallel message processing edge cases
            if not self.last_message or before.id != self.last_message.id:
                return

            # Do not remove the "editing" portion of the embed, other segments of code look for that as a keyword
            self.last_message = await before.channel.send(
                content=str(self.last_number),
                embed=set_embed_author_footer(
                    discord.Embed(
                        description=f"{before.author.mention} tried editing their message...\n\n"
                        f"The count is currently at: {self.get_representation()}",
                        colour=discord.Colour.green(),
                    ),
                    before.author,
                ),
            )
            await before.delete()  # Delete original message after self.last_message is set, to prevent triggering deletion detection

    @commands.Cog.listener("on_message_delete")
    async def counting_on_message_delete(self, message: discord.Message):
        """on_message_delete event handler to allow for handling of counting message deletions"""
        if (
            message.channel.id != COUNTING_CHANNEL
        ):  # Check if we're in counting channel first, to prevent excessive locks
            return

        async with self.lock:  # Utilize async lock to prevent parallel message processing edge cases
            if not self.last_message or message.id != self.last_message.id:
                return

            # Do not remove the "deleting" portion of the embed, other segments of code look for that as a keyword
            self.last_message = await message.channel.send(
                content=str(self.last_number),
                embed=set_embed_author_footer(
                    discord.Embed(
                        description=f"{message.author.mention} tried deleting their message...\n\n"
                        f"The count is currently at: {self.get_representation()}",
                        colour=discord.Colour.dark_green(),
                    ),
                    message.author,
                ),
            )

    @commands.Cog.listener("on_reaction_add")
    async def counting_on_reaction_add(
        self, reaction: discord.Reaction, member: discord.Member
    ):
        """on_reaction_add event handler to allow for deletion of select messages (bot must react with 🗑️ for it to be deletable)"""
        message = reaction.message
        if (
            message.channel.id != COUNTING_CHANNEL
            or message.author.id != self.bot.user.id
        ):  # Not counting channel, or message not by us
            return
        if (
            reaction.emoji != "🗑️" or member.id == self.bot.user.id
        ):  # Not trash bin emoji, or our own reaction
            return
        if not reaction.me:  # We didn't react with 🗑️ (non-deletable message)
            return
        if (
            len(message.embeds) == 0
            or str(member.id) not in message.embeds[0].author.name
        ):  # Author must be user reacting
            # Thinking about this, technically if someone changes their nickname to someone else's user ID, that person
            # could delete because it would match the author.name field, but that's on the person who changed their nick...
            # - blank, at midnight

            # Removing reaction at this point because we're far enough in that it's likely an attempt to delete
            return await reaction.remove(member)
        await message.delete()

    @commands.command()
    @commands.has_role(DEVELOPER_ROLE)
    async def countingoverride(self, ctx: commands.Context, number: int):
        """Override the current count in counting"""
        self.last_number = number
        self.last_message = await self.channel.send(
            content=str(number),
            embed=set_embed_footer(
                discord.Embed(
                    title="Count Overridden!",
                    description=f"The current count has been set to: **`{number:,d}`** by {ctx.author.mention}.",
                    colour=discord.Colour.green(),
                )
            ),
        )


async def setup(bot):
    await bot.add_cog(Counting(bot))
