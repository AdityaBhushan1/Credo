import discord
from discord.ext import commands
from discord.ext.commands import errors
from ..utils.emote import xmark,error
from ..utils.replies import NEGATIVE_REPLIES,ERROR_REPLIES
import random
from ..utils import expectations
class Error(commands.Cog,name='Error'):

    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
            
        elif isinstance(error, expectations.TeaBoterror):
            return await ctx.error(f'{error.__str__().format(ctx=ctx)}')
            
        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join(
                [f'> {permission}' for permission in error.missing_perms])
            message = f'{random.choice(ERROR_REPLIES)} | You Are missing **`{permissions}`** permissions to run the command.'
            
            await ctx.error(message)
        
        elif isinstance(error, errors.MissingRequiredArgument):
            await ctx.error(f'{random.choice(NEGATIVE_REPLIES)} | You missed the `{error.param.name}` argument.')
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(
                ctx.command)
            return await ctx.send_help(helper)

        elif isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join(
                [f'> {permission}' for permission in error.missing_perms])
            message = f'I am missing **`{permissions}`** permissions to run the command `{ctx.command}`.\n'
            try:
                await ctx.error(message)
            except discord.Forbidden:
                try:
                    await ctx.author.error(f"Hey It looks like, I can't error messages in that channel.\nAlso I am misssing **`{permissions}`** permissions to run the command.")
                except discord.Forbidden:
                    pass
            return

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.BadArgument):

            if isinstance(error, commands.MessageNotFound):
                await ctx.error(f'A message for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.MemberNotFound):
                await ctx.error(f'A member for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.UserNotFound):
                await ctx.error(f'A user for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.ChannelNotFound):
                await ctx.error(f'A channel/category for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.RoleNotFound):
                await ctx.error(f'A role for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.EmojiNotFound):
                await ctx.error(f'An emoji for the argument `{error.argument}` was not found.')
            elif isinstance(error, commands.ChannelNotReadable):
                await ctx.error(f'I do not have permission to read the channel `{error.argument}`')
            elif isinstance(error, commands.PartialEmojiConversionFailure):
                await ctx.error(f'The argument `{error.argument}` did not match the partial emoji format.')
            elif isinstance(error, commands.BadInviteArgument):
                await ctx.error(f'The invite that matched that argument was not valid or is expired.')
            elif isinstance(error, commands.BadBoolArgument):
                await ctx.error(f'The argument `{error.argument}` was not a valid True/False value.')
            elif isinstance(error, commands.BadColourArgument):
                await ctx.error(f'The argument `{error.argument}` was not a valid colour.')

            else:
                helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(
                    ctx.command)
                return await ctx.send_help(helper)

        elif isinstance(error, errors.CommandOnCooldown):
            await ctx.error(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
            return
        elif isinstance(error, commands.MissingRole):
            return await ctx.error(f"You need `{error.missing_role}` role to use this command.")
        elif isinstance(error, commands.MaxConcurrencyReached):
            return await ctx.error(f"This command is already running in this server. You have wait for it to finish.")

        elif isinstance(error, commands.CheckFailure):
            return

        # elif isinstance(error, discord.Forbidden):
        #     return

        # elif isinstance(error, errors.CommandInvokeError):
        #     return

        elif isinstance(error, commands.NoPrivateMessage):
            return
        

            
        elif isinstance(error, discord.ext.commands.errors.DisabledCommand):
            await ctx.error('Hey Man, The Command Is Disabled')

        else:
            raise error

def setup(bot):
    bot.add_cog(Error(bot))
    