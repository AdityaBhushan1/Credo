import asyncio
import re
import dateparser
from datetime import datetime
from discord.ext.commands.converter import RoleConverter, TextChannelConverter
import pytz
import discord
from . import emote

IST = pytz.timezone("Asia/Kolkata")
class InputError:
    ...

async def safe_delete(message):
    try:
        await message.delete()
    except (discord.Forbidden, discord.NotFound):
        return


async def channel_input(ctx, check, timeout=120, delete_after=False):
    try:
        message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
        channel = await TextChannelConverter().convert(ctx, message.content)
    except asyncio.TimeoutError:
        return await ctx.send(f"{emote.error} | You failed to select a channel in time. Try again!")

    else:
        if len(message.channel_mentions) == 0:
            return await message.channel.send(f'{emote.error} | Thats Not A Channel')
        if not channel.permissions_for(ctx.me).read_messages:
            return await ctx.send(
                f"{emote.error} | Unfortunately, I don't have read messages permissions in {channel.mention}."
            )
            
        if not channel.permissions_for(ctx.me).send_messages:
            return await ctx.send(
                f"{emote.error} | Unfortunately, I don't have send messages permissions in {channel.mention}."
            )    


        if delete_after:
            await safe_delete(message)

        return channel


async def role_input(ctx, check, timeout=120, hierarchy=True, delete_after=False):
    try:
        message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
        role = await RoleConverter().convert(ctx, message.content)
    except asyncio.TimeoutError:
        raise InputError(f"{emote.error} | You failed to select a role in time. Try again!")

    else:
        if len(message.role_mentions) == 0:
            return await ctx.send(f'{emote.error} | Thats Not A Role')

        if hierarchy is True:
            if role > ctx.me.top_role:
                return await ctx.send(
                    f"{emote.error} | The position of {role.mention} is above my top role. So I can't give it to anyone.\nKindly move {ctx.me.top_role.mention} above {role.mention} in Server Settings."
                )

            if ctx.author.id != ctx.guild.owner_id:
                if role > ctx.author.top_role:
                    return await ctx.send(
                        f"{emote.error} | The position of {role.mention} is above your top role {ctx.author.top_role.mention}."
                    )

        if delete_after:
            await safe_delete(message)

        return role


async def integer_input(
    ctx, check, timeout=120, limits=(None, None), delete_after=False
):
    def new_check(message):
        if not check(message):
            return False

        try:
            if limits[1] is not None:
                if len(message.content) > len(
                    str(limits[1])
                ):  # This is for safe side, memory errors u know :)
                    return False

            digit = int(message.content)

        except ValueError:
            return False
        else:
            if not any(limits):  # No Limits
                return True

            low, high = limits

            if all(limits):
                return low <= digit <= high
            else:
                if low is not None:
                    return low <= digit
                else:
                    return high <= digit

    try:
        message = await ctx.bot.wait_for("message", check=new_check, timeout=timeout)
    except asyncio.TimeoutError:
        raise InputError(f"{emote.error} | You failed to select a number in time. Try again!")
    else:
        if delete_after:
            await safe_delete(message)

        return int(message.content)


async def time_input(ctx, check, timeout=120, delete_after=False):
    try:
        message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        return await ctx.send(f"{emote.error} | Timeout, You have't responsed in time. Try again!")
    else:
        match = re.match(r"\d+:\d+", message.content)
        if not match:
            return await ctx.send(f'{emote.error} | Thats Not A Valid Time')
        match = match.group(0) 
        hour, minute = match.split(":")
        str_time = f'{hour}:{minute}'
        converting = datetime.strptime(str_time,'%H:%M')
        final_time = converting.time()

        return final_time


# async def time_input(ctx, check, timeout=120, delete_after=False):
#     try:
#         message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
#     except asyncio.TimeoutError:
#         raise InputError("Timeout, You have't responsed in time. Try again!")
#     else:
#         try:
#             parsed = dateparser.parse(
#                 message.content,
#                 settings={
#                     "RELATIVE_BASE": datetime.now(tz=IST),
#                     "TIMEZONE": "Asia/Kolkata",
#                     "RETURN_AS_TIMEZONE_AWARE": True,
#                 },
#             )

#             if delete_after:
#                 await safe_delete(message)

#             return parsed
#         except TypeError:
#             raise InputError("This isn't valid time format.")


async def string_input(ctx, check, timeout=120, delete_after=False):
    try:
        message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
    except asyncio.TimeoutError:
        raise InputError("Response timed out!")
    else:
        if delete_after:
            await safe_delete(message)

        return message.content
