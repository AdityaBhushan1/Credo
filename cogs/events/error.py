import discord
from discord.ext import commands
from discord.ext.commands import errors
from ..utils.emote import xmark
from ..utils.replies import NEGATIVE_REPLIES,ERROR_REPLIES
import random
class Error(commands.Cog,name='Error'):

    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join(
                [f'> {permission}' for permission in error.missing_perms])
            message = f'{xmark} | {random.choice(ERROR_REPLIES)} | You Are missing **`{permissions}`** permissions to run the command.'
            
            await ctx.send(message)
        
        elif isinstance(error, errors.MissingRequiredArgument):
            await ctx.send(f'{xmark} | {random.choice(NEGATIVE_REPLIES)} | You missed the `{error.param.name}` argument.')
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(
                ctx.command)
            return await ctx.send_help(helper)

        elif isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join(
                [f'> {permission}' for permission in error.missing_perms])
            message = f'{xmark} | I am missing **`{permissions}`** permissions to run the command `{ctx.command}`.\n'
            try:
                await ctx.send(message)
            except discord.Forbidden:
                try:
                    await ctx.author.send(f"Hey It looks like, I can't send messages in that channel.\nAlso I am misssing **`{permissions}`** permissions to run the command.")
                except discord.Forbidden:
                    pass
            return

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.BadArgument):

            if isinstance(error, commands.MessageNotFound):
                await ctx.send(f'{xmark} | A message for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.MemberNotFound):
                await ctx.send(f'{xmark} | A member for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.UserNotFound):
                await ctx.send(f'{xmark} | A user for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.ChannelNotFound):
                await ctx.send(f'{xmark} | A channel/category for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.RoleNotFound):
                await ctx.send(f'{xmark} | A role for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.EmojiNotFound):
                await ctx.send(f'{xmark} | An emoji for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.ChannelNotReadable):
                await ctx.send(f'{xmark} | I do not have permission to read the channel `{error.argument}`')
            elif isinstance(error, commands.PartialEmojiConversionFailure):
                await ctx.send(f'{xmark} | The argument `{error.argument}` did not match the partial emoji format.')
            elif isinstance(error, commands.BadInviteArgument):
                await ctx.send(f'{xmark} | The invite that matched that argument was not valid or is expired.')
            elif isinstance(error, commands.BadBoolArgument):
                await ctx.send(f'{xmark} | The argument `{error.argument}` was not a valid True/False value.')
            elif isinstance(error, commands.BadColourArgument):
                await ctx.send(f'{xmark} | The argument `{error.argument}` was not a valid colour.')

            else:
                helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(
                    ctx.command)
                return await ctx.send_help(helper)

        elif isinstance(error, errors.CommandOnCooldown):
            await ctx.send(f"{xmark} | This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
            return

        elif isinstance(error, commands.CheckFailure):
            return

        # elif isinstance(error, discord.Forbidden):
        #     return

        # elif isinstance(error, errors.CommandInvokeError):
        #     return

        elif isinstance(error, commands.NoPrivateMessage):
            return
        

            
        elif isinstance(error, discord.ext.commands.errors.DisabledCommand):
            await ctx.send('Hey Man, The Command Is Disabled')

        else:
            raise error

def setup(bot):
    bot.add_cog(Error(bot))
    