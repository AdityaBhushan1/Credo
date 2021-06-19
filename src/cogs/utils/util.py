import discord
from discord.ext import commands
import random
import math
import time
import contextlib
import traceback
import re
from PIL import ImageColor
from . import expectations,emote
from discord.ext.commands.converter import MessageConverter

def traceback_maker(err, advance: bool = True):
    _traceback = ''.join(traceback.format_tb(err.__traceback__))
    error = ('```py\n{1}{0}: {2}\n```').format(
        type(err).__name__, _traceback, err)
    return error if advance else f"{type(err).__name__}: {err}"

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content

async def get_or_fetch_member(guild, member_id):
        """Looks up a member in cache or fetches if not found.
        Parameters
            -----------
            guild: Guild
                The guild to look in.
            member_id: int
                The member ID to search for.
            Returns
            ---------
            Optional[Member]
                The member or None if not found.
            """

        member = guild.get_member(member_id)
        if member is not None:
            return member

        members = await guild.query_members(limit=1, user_ids=[member_id], cache=True)
        if not members:
            return None
        return members[0]


def date(target, clock=True):
    """ Clock format using datetime.strftime() """
    if not clock:
        return target.strftime("%d %B %Y")
    return target.strftime("%d %B %Y, %H:%M")

def timetext(name):
    """ Timestamp, but in text form """
    return f"{name}_{int(time.time())}.txt"


class ColorConverter(commands.Converter):
    async def convert(self, ctx, arg: str):
        with contextlib.suppress(AttributeError):
            match = re.match(r"\(?(\d+),?\s*(\d+),?\s*(\d+)\)?", arg)
            check = all(0 <= int(x) <= 255 for x in match.groups())

        if match and check:
            return discord.Color.from_rgb([int(i) for i in match.groups()])

        converter = commands.ColorConverter()
        try:
            result = await converter.convert(ctx, arg)
        except commands.BadColourArgument:
            try:
                color = ImageColor.getrgb(arg)
                result = discord.Color.from_rgb(*color)
            except ValueError:
                result = None

        if result:
            return result

        raise expectations.InvalidColor(arg)

class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise commands.BadArgument(f'{emote.error} | Reason is too long ({len(argument)}/{reason_max})')
        return ret

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument(f'This member has not been banned before.') from None

        ban_list = await ctx.guild.bans()
        entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument('This member has not been banned before.')
        return entity

def can_execute_action(ctx, user, target):
    return user.id == ctx.bot.owner_id or \
           user == ctx.guild.owner or \
           user.top_role > target.top_role
class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                member_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{emote.error} | {argument} is not a valid member or member ID.") from None
            else:
                m = await get_or_fetch_member(ctx.guild, member_id)
                if m is None:
                    # hackban case
                    return type('_Hackban', (), {'id': member_id, '__str__': lambda s: f'Member ID {s.id}'})()

        if not can_execute_action(ctx, ctx.author, m):
            raise commands.BadArgument(f'{emote.error} | You cannot do this action on this user due to role hierarchy.')
        return m

class GlobalChannel(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            # Not found... so fall back to ID + global lookup
            try:
                channel_id = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
            else:
                channel = ctx.bot.get_channel(channel_id)
                if channel is None:
                    raise commands.BadArgument(f'Could not find a channel by ID {argument!r}.')
                return channel

class WrappedMessageConverter(MessageConverter):
    """A converter that handles embed-suppressed links like <http://example.com>."""

    async def convert(self, ctx: discord.ext.commands.Context, argument: str) -> discord.Message:
        """Wrap the commands.MessageConverter to handle <> delimited message links."""
        # It's possible to wrap a message in [<>] as well, and it's supported because its easy
        if argument.startswith("[") and argument.endswith("]"):
            argument = argument[1:-1]
        if argument.startswith("<") and argument.endswith(">"):
            argument = argument[1:-1]

        return await super().convert(ctx, argument)


