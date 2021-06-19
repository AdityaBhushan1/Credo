from discord.ext import commands
from ..utils.confirmater import ConfirmationPrompt
from ..utils import (
    emote,
    util
)
import shlex,re,discord
from .utils import (
    role_checker,
    plural,
    Arguments,
    do_removal,
    _basic_cleanup_strategy,
    _complex_cleanup_strategy,
    Category
)
from contextlib import suppress
from typing import Optional

class Mod(commands.Cog, name='Moderation'):
    def __init__(self,bot):
        self.bot = bot
        self.confirmater_title = 'Are You Sure?'
        self.do_removal = do_removal

    # kick command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason:util.ActionReason = None):
        '''
        Kicks A Member From Server
        '''
        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
        else:
            pass
        if ctx.message.author.id == member.id:
            await ctx.send('You  Cannot Kick Yourself')
            return
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title,description = f"Are you sure that you want to kick `{member}`?")

        if confirmation.confirmed:
            try:
                await member.send(f"You Have Been kicked From {ctx.guild.name}, Because: " + reason)
            except:
                pass
            await confirmation.update(description = f'{emote.tick} | Succefully Kicked {member}, Because: '+ reason)
            await member.kick(reason=reason)
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)


    # ban command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: util.MemberID, *, reason:util.ActionReason = None):
        '''
        Bans A Member From Server
        '''
        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
        else:
            pass
        if ctx.message.author.id == member.id:
            await ctx.send('You  Cannot Ban Yourself')
            return
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title,description= f"Are you sure that you want to ban `{member}`?")

        if confirmation.confirmed:
            try:
                await member.send(f"You Have Been Baned From {ctx.guild.name}, Because: " + reason)
            except:
                pass
            await confirmation.update(description = f'{emote.tick} | Succefully Banned {member}, Because: '+ reason)
            await member.ban(reason=reason)
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)


    # unban command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        '''
        Unbans A Member From Server
        '''
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split('#')
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title,description =  f"Thsi Will Unban `{member}`.")
        if confirmation.confirmed:
            for banned_entry in banned_users:
                user = banned_entry.user
                if (user.name, user.discriminator) == (member_name, member_disc):
                    await ctx.guild.unban(user)
                    await confirmation.update(description = f"{member_name} has been unbanned!")
                    return

            await confirmation.updated(description = f"{member} Was Not Found")
        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)
# #todo fix confirmater
#     @commands.command()
#     @commands.has_permissions(ban_members=True)
#     @commands.bot_has_guild_permissions(ban_members=True)
#     async def mute(self, ctx, member : discord.Member):
#         '''
#         Mutes A Member On Server
#         '''
#         if ctx.message.author.id == member.id:
#             await ctx.send('You  Cannot Mute Yourself')
#             return
#         guild = ctx.guild
#         mutedRole = discord.utils.get(guild.roles, name= "Muted")

#         if not mutedRole:
#             mutedRole = await guild.create_role(name = "Muted")
                
#             for channel in guild.channels:
#                 await channel.set_permissions(mutedRole, speak= False, send_messages= False)
#         confirmation = ConfirmationPrompt(ctx, self.bot.color)
#         await confirmation.confirm(f"Are you sure that you want to mute `{member}`?")

#         if confirmation.confirmed:
#             await member.add_roles(mutedRole)
#             await ctx.send("{} has been muted" .format(member.mention,))
#         else:
#             await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)
# #todo fix confirmater
#     # unmute
#     @commands.command()
#     @commands.has_permissions(ban_members=True)
#     @commands.bot_has_guild_permissions(ban_members=True)
#     async def unmute(self, ctx,member : discord.Member):
#         '''
#         Unmutes A Member On Server
#         '''
#         guild = ctx.guild
#         confirmation = ConfirmationPrompt(ctx, self.bot.color)
#         await confirmation.confirm(f"Are you sure that you want to unmute `{member}`?")

#         if confirmation.confirmed:
#             for role in guild.roles:
#                 if role.name == "Muted":
#                     await member.remove_roles(role)
#                     await ctx.send("{} has been unmuted" .format(member.mention,))
#                     return 
#         else:
#             await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

# #todo fix confirmater
#     # create text channel
#     @commands.command()
#     @commands.has_permissions(manage_channels=True)
#     @commands.bot_has_guild_permissions(manage_channels=True)
#     async def createtxt(self,ctx,channelName):
#         '''
#         Creates A Text Channel On Server
#         '''
#         guild = ctx.guild
#         confirmation = ConfirmationPrompt(ctx, self.bot.color)
#         await confirmation.confirm(f"Are you sure that you want to create a channel named `{channelName}`?")

#         if confirmation.confirmed:
#             em = discord.Embed(title='success', description='{} has been created' .format(channelName),color=discord.Colour.green())
#             await guild.create_text_channel(name='{}'.format(channelName))
#             await ctx.send(embed=em)
#         else:
#             await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)
# #todo fix confirmater
#     # delete textcahnnel
#     @commands.command()
#     @commands.has_permissions(manage_channels=True)
#     @commands.bot_has_guild_permissions(manage_channels=True)
#     async def deletetxt(self,ctx,channel: discord.TextChannel):
#         '''
#         Deletes A Text Channel From Server
#         '''
#         confirmation = ConfirmationPrompt(ctx, self.bot.color)
#         await confirmation.confirm(f"Are you sure that you want to delete the channel named `{channel}`?")

#         if confirmation.confirmed:
#             em = discord.Embed(title='success', description=f'channel: {channel} has been deleted' , color=discord.Colour.red())
#             await ctx.send(embed=em)
#             await channel.delete()    
#         else:
#             await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

# #todo fix confirmater
#     # create vc
#     @commands.command()
#     @commands.has_permissions(manage_channels=True)
#     @commands.bot_has_guild_permissions(manage_channels=True)
#     async def createvc(self,ctx,channelName):
#         '''
#         Creates A Voice Channel On Server
#         '''
#         guild = ctx.guild
#         confirmation = ConfirmationPrompt(ctx, self.bot.color)
#         await confirmation.confirm(f"Are you sure that you want to create a vc named `{channelName}`?")

#         if confirmation.confirmed:
#             em = discord.Embed(title='success', description=f'{channelName} Has Been Created',color=discord.Colour.green())
#             await guild.create_voice_channel(name=channelName)
#             await ctx.send(embed=em)
#         else:
#             await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)
# #todo fix confirmater
#     # delete vccahnnel
#     @commands.command()
#     @commands.has_permissions(manage_channels=True)
#     @commands.bot_has_guild_permissions(manage_channels=True)
#     async def deletevc(self,ctx,vc: discord.VoiceChannel):
#         '''
#         Deletes A Voice Channel From Server
#         '''
#         confirmation = ConfirmationPrompt(ctx, self.bot.color)
#         await confirmation.confirm(f"Are you sure that you want to delete the vc named `{vc}`?")

#         if confirmation.confirmed:
#             em = discord.Embed(title='success', description=f'{vc} has been deleted' , color=discord.Colour.red())
#             await ctx.send(embed=em)
#             await vc.delete()
#         else:
#             await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

# #todo fix confirmater
#     @commands.command(aliases=['smon'])
#     @commands.has_permissions(manage_channels=True)
#     @commands.bot_has_guild_permissions(manage_channels=True)
#     async def slowmode_on(self, ctx, time):
#         """
#         Adds Slow Mode To Channel
#         """
#         confirmation = ConfirmationPrompt(ctx, self.bot.color)
#         await confirmation.confirm(f"Are you sure that you want to turn on slowmode for `{time}`seconds?")

#         if confirmation.confirmed:
#             await confirmation.update("Confirmed", color=0x55ff55)
#             await ctx.channel.edit(slowmode_delay=time)
#             await ctx.send(f'{time}s of slowmode was set on the current channel.')
#         else:
#             await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

# #todo fix confirmater
#     @commands.command(aliases=['smoff'])
#     @commands.has_permissions(manage_channels=True)
#     @commands.bot_has_guild_permissions(manage_channels=True)
#     async def slowmode_off(self, ctx):
#         """
#         Removes Slow Mode From Channel
#         """
#         confirmation = ConfirmationPrompt(ctx, self.bot.color)
#         await confirmation.confirm(title = self.confirmater_title,description = "Are you sure that you want to off slowmode?")

#         if confirmation.confirmed:
#             await confirmation.update("Confirmed", color=0x55ff55)
#             await ctx.channel.edit(slowmode_delay=0)
#             await ctx.send(f'Slowmode removed.')
#         else:
#             await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason: util.ActionReason = None):
        """
        Soft bans a member from the server.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title,description = f"Are you sure that you want to Soft Ban `{member}`?")

        if confirmation.confirmed:
            await ctx.guild.ban(member, reason=reason)
            await ctx.guild.unban(member, reason=reason)
            await ctx.send(description = f'{emote.tick} | Succefully Soft Banned {member}')
        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def multiban(self, ctx, members: commands.Greedy[util.MemberID], *, reason: util.ActionReason = None):
        """Bans multiple members from the server.

        This only works through banning via ID.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        total_members = len(members)
        if total_members == 0:
            return await ctx.send('Missing members to ban.')

        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title,description = f"This will ban **{plural(total_members):member}")

        if confirmation.confirmed:

            failed = 0
            for member in members:
                try:
                    await ctx.guild.ban(member, reason=reason)
                except discord.HTTPException:
                    failed += 1

            await confirmation.update(description = f"{emote.tick} | Succefully Banned {total_members - failed}/{total_members} members.")

        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def multisoftban(self, ctx, members: commands.Greedy[util.MemberID], *, reason: util.ActionReason = None):
        """Soft Bans multiple members from the server.

        This only works through banning via ID.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        total_members = len(members)
        if total_members == 0:
            return await ctx.send('Missing members to ban.')

        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title,description = f"This will Soft Ban **{plural(total_members):member}**.")

        if confirmation.confirmed:

            failed = 0
            for member in members:
                try:
                    await ctx.guild.ban(member, reason=reason)
                    await ctx.guild.unban(member, reason=reason)
                except discord.HTTPException:
                    failed += 1

            await confirmation.update(description = f"{emote.tick} | Succefully Soft Banned {total_members - failed}/{total_members} members.")

        else:
            await confirmation.update(description="Not confirmed", hide_author=True, color=0xff5555)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel.
        """

        strategy = _basic_cleanup_strategy
        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = _complex_cleanup_strategy

        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'- **{author}**: {count}' for author, count in spammers)

        await ctx.send('\n'.join(messages), delete_after=10)


    @commands.group(aliases=['purge'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def remove(self, ctx):
        """Removes messages that meet a criteria.

        In order to use this command, you must have Manage Messages permissions.
        Note that the bot needs Manage Messages as well. These commands cannot
        be used in a private message.

        When the command is done doing its work, you will get a message
        detailing which users got removed and how many messages got removed.
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @remove.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @remove.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @remove.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @remove.command(name='all')
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @remove.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @remove.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.

        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @remove.command(name='bot', aliases=['bots'])
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @remove.command(name='emoji', aliases=['emojis'])
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<a?:[a-zA-Z0-9\_]+:([0-9]+)>')
        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @remove.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f'Successfully removed {total_reactions} reactions.')

    @remove.command()
    async def custom(self, ctx, *, args: str):
        """A more advanced purge command.

        This command uses a powerful "command line" syntax.
        Most options support multiple values to indicate 'any' match.
        If the value has spaces it must be quoted.

        The messages are only deleted if all options are met unless
        the `--or` flag is passed, in which case only if any is met.

        The following options are valid.

        `--user`: A mention or name of the user to remove.
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.

        Flag options (no arguments):

        `--bot`: Check if it's a bot user.
        `--embeds`: Check if the message has embeds.
        `--files`: Check if the message has attachments.
        `--emoji`: Check if the message has custom emoji.
        `--reactions`: Check if the message has reactions
        `--or`: Use logical OR for all options.
        `--not`: Use logical NOT for all options.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--reactions', action='store_const', const=lambda m: len(m.reactions))
        parser.add_argument('--search', type=int)
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any
        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        if args.after:
            if args.search is None:
                args.search = 2000

        if args.search is None:
            args.search = 100

        args.search = max(0, min(2000, args.search)) # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)
        
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban_list(self,ctx) :
        'Gets a list of all banned users '
        users = await ctx.guild.bans()
        if len(users) > 0 :
            msg = f'`{"ID":21}{"Name":25} Reason\n'
            for entry in users :
                userID = entry.user.id
                userName = str(entry.user)
                if entry.user.bot :
                    username = '🤖' + userName  #:robot: emoji
                reason = str(entry.reason)  # Could be None
                msg += f'{userID:<21}{userName:25} {reason}\n'
            embed = discord.Embed(color=0xe74c3c)  # Red
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(text=f'Server: {ctx.guild.name}')
            embed.add_field(name='Bans', value=msg + '`', inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{emote.xmark} There aret banned people!')


####################################################################################################################
#================================================ Role Commands ===================================================#
####################################################################################################################

    @commands.group(invoke_without_command=True, aliases=["addrole", "giverole"])
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role(self, ctx, role: discord.Role, members: commands.Greedy[discord.Member]):
        """
        Add a role to one or multiple users.
        """
        if await role_checker(ctx, role):
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
            failed = []
            for m in members:
                if not role in m.roles:
                    try:
                        await m.add_roles(role, reason=reason)
                    except:
                        failed.append(str(m))
                        continue

            if len(failed) > 0:
                return await ctx.error(f"I couldn't add roles to:\n{', '.join(failed)}")
            else:
                await ctx.success(f'Successfully Added Roles To {len(members)}')

    @role.command(name="humans")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_humans(self, ctx, *, role: discord.Role):
        """Add a role to all human users."""
        if await role_checker(ctx, role):
            confirmation = ConfirmationPrompt(ctx, self.bot.color)
            await confirmation.confirm(title = self.confirmater_title, description = f"{role.mention} will be added to all human users in the server.")    
            if confirmation.confirmed:
                members = list(filter(lambda x: not x.bot and role not in x.roles, ctx.guild.members))
                await confirmation.update(description = f"{emote.loading} | Adding role to {len(members)} humans...")
                reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
                failed = 0
                for m in members:
                    try:
                        await m.add_roles(role, reason=reason)
                    except:
                        failed += 1
                        continue

                if failed > 0:
                    return await confirmation.update(description = f"I couldn't add roles to {failed} members.")

                else:
                    await confirmation.update(description = f"{emote.tick} | Successfully added role to {len(members)} members.")
            else:
                await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @role.command(name="bots")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_bots(self, ctx, *, role: discord.Role):
        """Add a role to all bot users."""
        if await role_checker(ctx, role):
            confirmation = ConfirmationPrompt(ctx, self.bot.color)
            await confirmation.confirm(title = self.confirmater_title,description= f"{role.mention} will be added to all bots in the server.")    
            if confirmation.confirmed:
                members = list(filter(lambda x: x.bot and role not in x.roles, ctx.guild.members))
                await confirmation.update(description = f"{emote.loading} | Adding role to {len(members)} bots...")
                reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
                failed = 0
                for m in members:
                    try:
                        await m.add_roles(role, reason=reason)
                    except:
                        failed += 1
                        continue

                if failed > 0:
                    return await confirmation.update(description = f"I couldn't add roles to {failed} bots.")

                else:
                    await confirmation.update(description = f"{emote.tick} | Successfully added role to {len(members)} bots.")
            else:
                await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @role.command(name="all")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def role_all(self, ctx, *, role: discord.Role):
        """Add a role to everyone on the server"""
        if await role_checker(ctx, role):
            confirmation = ConfirmationPrompt(ctx, self.bot.color)
            await confirmation.confirm(title = self.confirmater_title, description = f"{role.mention} will be added to everyone in the server.")    
            if confirmation.confirmed:
                members = list(filter(lambda x: role not in x.roles, ctx.guild.members))
                await confirmation.update(description = f"{emote.loading} | Adding role to {len(members)} members...")
                reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
                failed = 0
                for m in members:
                    try:
                        await m.add_roles(role, reason=reason)
                    except:
                        failed += 1
                        continue

                if failed > 0:
                    return await confirmation.update(description = f"I couldn't add roles to {failed} members.")

                else:
                    await confirmation.update(description = f"{emote.tick} | Successfully added role to {len(members)} members.")
            else:
                await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)


    @commands.group(invoke_without_command=True, aliases=["removerole", "takerole"])
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole(self, ctx, role: discord.Role, members: commands.Greedy[discord.Member]):
        """Remove a role from one or multiple users."""
        if await role_checker(ctx, role):
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
            failed = []
            for m in members:
                if role in m.roles:
                    try:
                        await m.remove_roles(role, reason=reason)
                    except:
                        failed.append(str(m))
                        continue

            if len(failed) > 0:
                return await ctx.error(f"I couldn't remove roles from:\n{', '.join(failed)}")
            else:
                await ctx.success(f'Successfully Removed Roles To {len(members)}')

    @rrole.command(name="humans")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole_humans(self, ctx, *, role: discord.Role):
        """Remove a role from all human users."""
        if await role_checker(ctx, role):
            confirmation = ConfirmationPrompt(ctx, self.bot.color)
            await confirmation.confirm(title =self.confirmater_title, description = f"{role.mention} will be removed from all human users in the server.")    
            if confirmation.confirmed:
                members = list(filter(lambda x: not x.bot and role in x.roles, ctx.guild.members))
                await confirmation.update(description = f"{emote.loading} | Removing role from {len(members)} humans...")
                reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
                failed = 0
                for m in members:
                    try:
                        await m.remove_roles(role, reason=reason)
                    except:
                        failed += 1
                        continue

                if failed > 0:
                    return await confirmation.update(description = f"I couldn't remove roles to {failed} members.")

                else:
                    await confirmation.update(description = f"{emote.tick} | Successfully removed role to {len(members)} members.")
            else:
                await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @rrole.command(name="bots")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole_bots(self, ctx, *, role: discord.Role):
        """Remove a role from all the bots."""
        if await role_checker(ctx, role):
            confirmation = ConfirmationPrompt(ctx, self.bot.color)
            await confirmation.confirm(title = self.confirmater_title, description = f"{role.mention} will be removed from all bot users in the server.")    
            if confirmation.confirmed:
                members = list(filter(lambda x: x.bot and role in x.roles, ctx.guild.members))
                await confirmation.update(description = f"{emote.loading} | Removing role from {len(members)} bots...")
                reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
                failed = 0
                for m in members:
                    try:
                        await m.remove_roles(role, reason=reason)
                    except:
                        failed += 1
                        continue

                if failed > 0:
                    return await confirmation.update(description = f"I couldn't remove roles to {failed} members.")

                else:
                    await confirmation.update(description = f"{emote.tick} | Successfully removed role to {len(members)} members.")
            else:
                await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)
    @rrole.command(name="all")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def rrole_all(self, ctx, *, role: discord.Role):
        """Remove a role from everyone on the server."""
        if await role_checker(ctx, role):
            confirmation = ConfirmationPrompt(ctx, self.bot.color)
            await confirmation.confirm(title = self.confirmater_title, description = f"{role.mention} will be removed from everyone in the server.")    
            if confirmation.confirmed:
                members = list(filter(lambda x: role in x.roles, ctx.guild.members))
                await confirmation.update(description = f"{emote.loading} | Removing role from {len(members)} members...")
                reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
                failed = 0
                for m in members:
                    try:
                        await m.remove_roles(role, reason=reason)
                    except:
                        failed += 1
                        continue

                if failed > 0:
                    return await confirmation.update(description = f"I couldn't remove roles to {failed} members.")

                else:
                    await confirmation.update(description = f"{emote.tick} | Successfully removed role to {len(members)} members.")
            else:
                await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

####################################################################################################################
#================================================ Category Commands ===================================================#
####################################################################################################################

    @commands.group(invoke_without_command=True)
    async def category(self, ctx):
        """handle a category in you server"""
        await ctx.send_help(ctx.command)

    @category.command(name="delete")
    @commands.has_permissions(manage_channels=True, manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def category_delete(self, ctx, *, category: Category):
        """Delete a category and all the channels under it."""
        if not len(category.channels):
            return await ctx.error(f"**{category}** doesn't have any channels.")
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title, description = f"All channels under the category `{category}` will be deleted.")    
        if confirmation.confirmed:
            await confirmation.update(description = f"{emote.loading} | Deleteing {len(category.channels)} Channels")
            failed, success = 0, 0
            for channel in category.channels:
                try:
                    await channel.delete()
                    success += 1
                except:
                    failed += 1
                    continue

            await category.delete()

            with suppress(
                discord.Forbidden, commands.ChannelNotFound, discord.NotFound, commands.CommandInvokeError
            ):  # yes all these will be raised if the channel is from ones we deleted earlier.
                await confirmation.update(description = f"Successfully deleted **{category}**. (Deleted: `{success}`, Failed: `{failed}`)")

        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @category.command(name="hide")
    @commands.has_permissions(manage_channels=True, manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def category_hide(self, ctx, *, category: Category):
        """Hide a category and all its channels"""
        if not len(category.channels):
            return await ctx.error(f"**{category}** doesn't have any channels.")
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title, description = f"All channels under the category `{category}` will be hidden.")    
        if confirmation.confirmed:
            await confirmation.update(description = f"{emote.loading} | Hideing {len(category.channels)} Channels")
            failed, success = 0, 0

            for channel in category.channels:
                try:
                    perms = channel.overwrites_for(ctx.guild.default_role)
                    perms.read_messages = False
                    await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
                    success += 1
                except:
                    failed += 1
                    continue

            await confirmation.update(description = f"Successfully hidden category. (Hidden: `{success}`, Failed: `{failed}`)")

        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @category.command(name="unhide")
    @commands.has_permissions(manage_channels=True, manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def category_unhide(self, ctx, *, category: Category):
        """Unhide a hidden category and all its channels."""
        if not len(category.channels):
            return await ctx.error(f"**{category}** doesn't have any channels.")
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title, description = f"All channels under the category `{category}` will be unhidden.")    
        if confirmation.confirmed:
            await confirmation.update(description = f"{emote.loading} | UnHideing {len(category.channels)} Channels")
            failed, success = 0, 0

            for channel in category.channels:
                try:
                    perms = channel.overwrites_for(ctx.guild.default_role)
                    perms.read_messages = True
                    await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
                    success += 1
                except:
                    failed += 1
                    continue

            await confirmation.update(description = f"Successfully unhidden **{category}**. (Unhidden: `{success}`, Failed: `{failed}`)")

        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @category.command(name="recreate")
    @commands.has_permissions(manage_channels=True, manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def category_recreate(self, ctx, *, category: Category):
        """
        Delete a category completely and create a new one
        This will delete all the channels under the category and will make a new one with same perms and channels.
        """
        if not len(category.channels):
            return await ctx.error(f"**{category}** doesn't have any channels.")
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title, description = f"All channels under the category `{category}` will be cloned and deleted.")    
        if confirmation.confirmed:
            await confirmation.update(description = f"{emote.loading} | ReCreating {len(category.channels)} Channels")
            failed, success = 0, 0
            for channel in category.channels:
                if channel.permissions_for(ctx.me).manage_channels:
                    try:
                        position = channel.position
                        clone = await channel.clone(reason=f"Action done by {ctx.author}")
                        await channel.delete()
                        await clone.edit(position=position)
                        success += 1

                    except:
                        failed += 1
                        continue

            await confirmation.update(description = f"Successfully nuked **{category}**. (Cloned: `{success}`, Failed: `{failed}`)")

        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @category.command(name="lock")
    @commands.has_permissions(manage_channels=True, manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def category_lock(self, ctx, *, category: Category):
        '''
        Locks All The Channel Under The Category 
        '''
        if not len(category.channels):
            return await ctx.error(f"**{category}** doesn't have any channels.")
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title, description = f"All channels under the category `{category}` will be locked.")    
        if confirmation.confirmed:
            await confirmation.update(description = f"{emote.loading} | Locking {len(category.channels)} Channels")
            failed, success = 0, 0

            for channel in category.channels:
                try:
                    perms = channel.overwrites_for(ctx.guild.default_role)
                    perms.send_messages = False
                    await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
                    success += 1
                except:
                    failed += 1
                    continue

            await confirmation.update(description = f"Successfully locked category. (Hidden: `{success}`, Failed: `{failed}`)")

        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @category.command(name="unlock")
    @commands.has_permissions(manage_channels=True, manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def category_unlock(self, ctx, *, category: Category):
        '''Unlocks All The Channels Under Category'''
        if not len(category.channels):
            return await ctx.error(f"**{category}** doesn't have any channels.")
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title, description = f"All channels under the category `{category}` will be unlocked.")    
        if confirmation.confirmed:
            await confirmation.update(description = f"{emote.loading} | Unlocking {len(category.channels)} Channels")
            failed, success = 0, 0

            for channel in category.channels:
                try:
                    perms = channel.overwrites_for(ctx.guild.default_role)
                    perms.send_messages = True
                    await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
                    success += 1
                except:
                    failed += 1
                    continue

            await confirmation.update(description = f"Successfully unlocked category. (Hidden: `{success}`, Failed: `{failed}`)")

        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)


    @commands.group(invoke_without_command=True)
    async def maintenance(self, ctx):
        """Maintenance ON/ OFF for the server."""
        await ctx.send_help(ctx.command)

    @maintenance.command(name="on")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def maintenace_on(self, ctx, *, role: discord.Role = None):
        """
        Turn ON maintenance mode.
        You can turn on maintenance for a specific role too , the default role is everyone.
        This will hide all the channels where `role` has `read_messages` permission enabled.
        """
        role = role or ctx.guild.default_role
        
        channels = list(filter(lambda x: x.overwrites_for(role).read_messages, ctx.guild.channels))
        mine = sum(1 for i in filter(lambda x: x.permissions_for(ctx.me).manage_channels, (channels)))


        if not (len(channels)):
            return await ctx.error(f"**{role}** doesn't have `read_messages` enabled in any channel.")

        elif not mine:
            return await ctx.error(
                f"`{sum(1 for i in channels)} channels` have read messages enabled. But unfortunately I don't permission to edit any of them."
            )
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title, description = f"This Will Lock All The Channel in this Server")    
        if confirmation.confirmed:
            await confirmation.update(description = f"{emote.loading} | locking {len(channels)} Channels")
            success, failed = [], 0
            reason = f"Action done by -> {str(ctx.author)} ({ctx.author.id})"
            for channel in channels:
                overwrite = channel.overwrites_for(role)
                overwrite.read_messages = False 
                try:
                    await channel.set_permissions(role, overwrite=overwrite, reason=reason)
                    success.append(channel.id)
                except:
                    failed += 1
                    continue    
            await confirmation.update(description = f"Updated settings for `{len(success)} channels`.(`{failed}` failed)")
            channels_create_confirmation = ConfirmationPrompt(ctx, self.bot.color)
            await channels_create_confirmation.confirm(title = self.confirmater_title, description = f"This Will Create Maintainence Channels")    
            if channels_create_confirmation.confirmed:
                await channels_create_confirmation.update(description = f"{emote.loading} | Creating Maintainence Channels")
                overwrites = {
                    role: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
                    ctx.guild.me: discord.PermissionOverwrite(
                        read_messages=True, send_messages=True, read_message_history=True
                    ),
                }
                await ctx.guild.create_text_channel(f"maintenance-chat", overwrites=overwrites, reason=reason)
                await ctx.guild.create_voice_channel(f"maintenance-vc", overwrites=overwrites, reason=reason)
                await channels_create_confirmation.update(f"Done")
            else:
                return await channels_create_confirmation.update(description = f"Ok! Not Creating Channels")
        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)
            


    @maintenance.command(name="off")
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_permissions(administrator=True)
    async def maintenance_off(self, ctx, *, role: discord.Role = None):
        """
        Turn OFF maintenance mode.
        If you turned ON maintenance mode for a specific role , you need to mention it here too.
        """
        role = role or ctx.guild.default_role
        editable = await ctx.send(f'{emote.loading} | Unocking The Server')

        success = 0
        for channel in ctx.guild.channels:
            if channel != None and channel.permissions_for(channel.guild.me).manage_channels:

                perms = channel.overwrites_for(role)
                perms.read_messages = True
                await channel.set_permissions(role, overwrite=perms, reason="Lockdown timer complete!")
                success += 1

        await editable.edit(
            content = f"{emote.tick} | Successfully changed settings for `{success}` channels. (`{sum(1 for i in ctx.guild.channels)}` were hidden.)"
        )

        tc = discord.utils.get(ctx.guild.channels, name=f"maintenance-chat")
        vc = discord.utils.get(ctx.guild.channels, name=f"maintenance-vc")

        if tc and vc:
            await tc.delete()
            await vc.delete()
            await ctx.success(f"Deleted Maintainence Channels")

def setup(bot):
    bot.add_cog(Mod(bot))
    # bot.add_cog(ModEvents(bot))

'''
####################################################################################################################
#======================================== Lock, Unlock Commands ===================================================#
####################################################################################################################

    @commands.group(invoke_without_command=True, aliases=("lockdown",))
    async def lock(self, ctx, channel: Optional[discord.TextChannel]):
        """Lock a channel , category or the whole server."""
        channel = channel or ctx.channel

        if not channel.permissions_for(ctx.me).manage_channels:
            return await ctx.error(f"I need `manage_channels` permission in **{channel}**")

        elif not channel.permissions_for(ctx.author).manage_channels:
            return await ctx.error(f"You need `manage channels` permission in **{channel}** to use this.")

        perms = channel.overwrites_for(ctx.guild.default_role)
        perms.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=perms)

        await ctx.success(f"Locked **{channel}** By: {ctx.author.mention}")

    @lock.command(name="server", aliases=("guild",))
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_permissions(manage_guild=True)
    async def lock_server(self, ctx):
        channels = list(filter(lambda x: x.overwrites_for(ctx.guild.default_role).send_messages, ctx.guild.channels))
        mine = sum(1 for i in filter(lambda x: x.permissions_for(ctx.me).manage_channels, (channels)))

        if not (len(channels)):
            return await ctx.error(f"@everyone doesn't have `send_messages` enabled in any channel.")

        elif not mine:
            return await ctx.error(
                f"`{sum(1 for i in channels)} channels` have send messages enabled. But I don't permission to edit any of them."
            )
        confirmation = ConfirmationPrompt(ctx, self.bot.color)
        await confirmation.confirm(title = self.confirmater_title,description= f"This Will Set Send Messages To False For Everyone")    
        if confirmation.confirmed:
            await confirmation.update(description = f"{emote.loading} Locking Guild",)
            success, failed = [], 0
            reason = f"Action done by -> {str(ctx.author)} ({ctx.author.id})"
            for channel in channels:
                overwrite = channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False

                try:
                    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
                    success.append(channel.id)
                except:
                    failed += 1
                    continue

            await confirmation.update(
                description = f"Locked down `{len(success)} channels` (Failed: `{failed}`)"
            )
        else:
            await confirmation.update(description = "Not confirmed", hide_author=True, color=0xff5555)

    @commands.group(aliases=("unlockdown",), invoke_without_command=True)
    async def unlock(self, ctx, *, channel: Optional[discord.TextChannel]):
        channel = channel or ctx.channel

        if not channel.permissions_for(ctx.me).manage_channels:
            return await ctx.error(f"I need `manage_channels` permission in **{channel}**")

        elif not channel.permissions_for(ctx.author).manage_channels:
            return await ctx.error(f"You need `manage channels` permission in **{channel}** to use this.")

        perms = channel.overwrites_for(ctx.guild.default_role)
        perms.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=perms)

        await ctx.success(f"Unlocked **{channel}**")


    @unlock.command(name="server", aliases=("guild",))
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def unlock_guild(self, ctx):
        success = 0
        for channel in ctx.guild.channels:
            if channel != None and channel.permissions_for(ctx.me).manage_channels:
                perms = channel.overwrites_for(channel.guild.default_role)
                perms.send_messages = True
                await channel.set_permissions(
                    channel.guild.default_role, overwrite=perms
                )
                success += 1
        await ctx.success(
            f"Successfully unlocked `{success}` channels.)"
        )

    
'''