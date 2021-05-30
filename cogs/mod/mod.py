from discord.ext import commands
from disputils import BotConfirmation
from ..utils import emote
from collections import Counter, defaultdict
import argparse, shlex,enum,asyncio,re,discord


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
        

def can_execute_action(ctx, user, target):
    return user.id == ctx.bot.owner_id or \
           user == ctx.guild.owner or \
           user.top_role > target.top_role

class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)
class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise commands.BadArgument(f'{emote.error} | Reason is too long ({len(argument)}/{reason_max})')
        return ret
def safe_reason_append(base, to_append):
    appended = base + f'({to_append})'
    if len(appended) > 512:
        return base
    return appended

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

class plural:
    def __init__(self, value):
        self.value = value
    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'


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

class Mod(commands.Cog, name='Moderation'):
    def __init__(self,bot):
        self.bot = bot

    # kick command
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason:ActionReason = None):
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
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to kick `{member}`?")

        if confirmation.confirmed:
            try:
                await member.send(f"You Have Been kicked From {ctx.guild.name}, Because: " + reason)
            except:
                pass
            await ctx.send(f'{emote.tick} | Succefully Kicked {member}, Because: '+ reason)
            await member.kick(reason=reason)
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)


    # ban command
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: MemberID, *, reason:ActionReason = None):
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
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to ban `{member}`?")

        if confirmation.confirmed:
            try:
                await member.send(f"You Have Been Baned From {ctx.guild.name}, Because: " + reason)
            except:
                pass
            await ctx.send(f'{emote.tick} | Succefully Banned {member}, Because: '+ reason)
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
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to unban `{member}`?")

        if confirmation.confirmed:

            for banned_entry in banned_users:
                user = banned_entry.user

                if (user.name, user.discriminator) == (member_name, member_disc):

                    await ctx.guild.unban(user)
                    await ctx.send(member_name + "has been unbanned!")
                    return

            await ctx.send(member + " Was Not Found")
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)
    # mute
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def mute(self, ctx, member : discord.Member):
        '''
        Mutes A Member On Server
        '''
        if ctx.message.author.id == member.id:
            await ctx.send('You  Cannot Mute Yourself')
            return
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name= "Muted")

        if not mutedRole:
            mutedRole = await guild.create_role(name = "Muted")
                
            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak= False, send_messages= False)
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to mute `{member}`?")

        if confirmation.confirmed:
            await member.add_roles(mutedRole)
            await ctx.send("{} has been muted" .format(member.mention,))
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

    # unmute
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unmute(self, ctx,member : discord.Member):
        '''
        Unmutes A Member On Server
        '''
        guild = ctx.guild
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to unmute `{member}`?")

        if confirmation.confirmed:
            for role in guild.roles:
                if role.name == "Muted":
                    await member.remove_roles(role)
                    await ctx.send("{} has been unmuted" .format(member.mention,))
                    return 
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

    # create text channel
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def createtxt(self,ctx,channelName):
        '''
        Creates A Text Channel On Server
        '''
        guild = ctx.guild
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to create a channel named `{channelName}`?")

        if confirmation.confirmed:
            em = discord.Embed(title='success', description='{} has been created' .format(channelName),color=discord.Colour.green())
            await guild.create_text_channel(name='{}'.format(channelName))
            await ctx.send(embed=em)
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

    # delete textcahnnel
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def deletetxt(self,ctx,channel: discord.TextChannel):
        '''
        Deletes A Text Channel From Server
        '''
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to delete the channel named `{channel}`?")

        if confirmation.confirmed:
            em = discord.Embed(title='success', description=f'channel: {channel} has been deleted' , color=discord.Colour.red())
            await ctx.send(embed=em)
            await channel.delete()    
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)


    # create vc
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def createvc(self,ctx,channelName):
        '''
        Creates A Voice Channel On Server
        '''
        guild = ctx.guild
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to create a vc named `{channelName}`?")

        if confirmation.confirmed:
            em = discord.Embed(title='success', description=f'{channelName} Has Been Created',color=discord.Colour.green())
            await guild.create_voice_channel(name=channelName)
            await ctx.send(embed=em)
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

    # delete vccahnnel
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def deletevc(self,ctx,vc: discord.VoiceChannel):
        '''
        Deletes A Voice Channel From Server
        '''
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to delete the vc named `{vc}`?")

        if confirmation.confirmed:
            em = discord.Embed(title='success', description=f'{vc} has been deleted' , color=discord.Colour.red())
            await ctx.send(embed=em)
            await vc.delete()
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def addrole(self,ctx,role: discord.Role, user:MemberID):
        '''
        Adds A Role To A Member
        '''
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to add the this role `{role}` to `{user}`?")

        if confirmation.confirmed:
            await confirmation.update("Confirmed", color=0x55ff55)
            await user.add_roles(role)
            await ctx.send(f'Succefully Given {role.mention} To {user.mention}')
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)


    # remove role
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def removerole(self,ctx,role: discord.Role, user:MemberID):
        '''
        Removes A Role From A Member
        '''
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to remove the this role `{role}` from `{user}`?")

        if confirmation.confirmed:
            await confirmation.update("Confirmed", color=0x55ff55)
            await user.remove_roles(role)
            await ctx.send(f'Succefully Removed {role.mention} From {user.mention}')
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)
    

    # # warn
    # @commands.command()
    # @commands.has_permissions(administrator=True)
    # @commands.bot_has_guild_permissions(administrator=True)
    # async def warn(self, ctx, member : MemberID, *, reason:ActionReason = None):
    #     '''
    #     Warns A Member On Server
    #     '''
    #     if reason is None:
    #         reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'
    #     try:
    #         await member.send(f"You Have Been Warned <:1626_warning_1:786100068246749205> on **{ctx.guild.name}** Because:" + reason)
    #     except:
    #         pass
    #     await ctx.send(member.name + "Has Been Warned <:1626_warning_1:786100068246749205>, Because:" + reason)


    @commands.command(aliases=['smon'])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def slowmode_on(self, ctx, time):
        """
        Adds Slow Mode To Channel
        """
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to turn on slowmode for `{time}`seconds?")

        if confirmation.confirmed:
            await confirmation.update("Confirmed", color=0x55ff55)
            await ctx.channel.edit(slowmode_delay=time)
            await ctx.send(f'{time}s of slowmode was set on the current channel.')
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)


    @commands.command(aliases=['smoff'])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def slowmode_off(self, ctx):
        """
        Removes Slow Mode From Channel
        """
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm("Are you sure that you want to off slowmode?")

        if confirmation.confirmed:
            await confirmation.update("Confirmed", color=0x55ff55)
            await ctx.channel.edit(slowmode_delay=0)
            await ctx.send(f'Slowmode removed.')
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)
        
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason: ActionReason = None):
        """
        Soft bans a member from the server.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Are you sure that you want to Soft Ban `{member}`?")

        if confirmation.confirmed:
            await ctx.guild.ban(member, reason=reason)
            await ctx.guild.unban(member, reason=reason)
            await ctx.send(f'{emote.tick} | Succefully Soft Banned {member}')
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def multiban(self, ctx, members: commands.Greedy[MemberID], *, reason: ActionReason = None):
        """Bans multiple members from the server.

        This only works through banning via ID.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        total_members = len(members)
        if total_members == 0:
            return await ctx.send('Missing members to ban.')

        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"This will ban **{plural(total_members):member}**. Are you sure?")

        if confirmation.confirmed:

            failed = 0
            for member in members:
                try:
                    await ctx.guild.ban(member, reason=reason)
                except discord.HTTPException:
                    failed += 1

            await confirmation.update(f"{emote.tick} | Succefully Banned {total_members - failed}/{total_members} members.")

        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def multisoftban(self, ctx, members: commands.Greedy[MemberID], *, reason: ActionReason = None):
        """Soft Bans multiple members from the server.

        This only works through banning via ID.
        """

        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        total_members = len(members)
        if total_members == 0:
            return await ctx.send('Missing members to ban.')

        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"This will Soft Ban **{plural(total_members):member}**. Are you sure?")

        if confirmation.confirmed:

            failed = 0
            for member in members:
                try:
                    await ctx.guild.ban(member, reason=reason)
                    await ctx.guild.unban(member, reason=reason)
                except discord.HTTPException:
                    failed += 1

            await confirmation.update(f"{emote.tick} | Succefully Soft Banned {total_members - failed}/{total_members} members.")

        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

    async def _basic_cleanup_strategy(self, ctx, search):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me:
                await msg.delete()
                count += 1
        return { 'Bot': count }

    async def _complex_cleanup_strategy(self, ctx, search):
        prefixes = '*' # thanks startswith

        def check(m):
            return m.author == ctx.me or m.content.startswith(prefixes)

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel.

        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.

        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.
        """

        strategy = self._basic_cleanup_strategy
        if ctx.me.permissions_in(ctx.channel).manage_messages:
            strategy = self._complex_cleanup_strategy

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

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            await ctx.send(f'Successfully removed {deleted} messages.', delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

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
        else :
            await ctx.send(f'{emote.xmark} There aret banned people!')

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def lock(self,ctx, *, reason= "No Reason Provided."):
        '''
        Locks The Channel For Server Deafult Role
        '''
        channel = ctx.channel
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"This will Lock This Channel For {ctx.guild.default_role}. Are you sure?")
        if confirmation.confirmed:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            overwrite.view_channel = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(title = 'Channel Lock' , description = f'_ _\n**{ctx.author}** Locked the Channel {channel.mention}\n\n\nReason - {reason}' , color = discord.Color.red())
            await ctx.send(embed=embed)  
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def unlock(self,ctx):
        channel = ctx.channel
        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"This will UnLock This Channel For {ctx.guild.default_role}. Are you sure?")
        if confirmation.confirmed:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = True
            overwrite.view_channel = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(title = 'Channel Unlock' , description = f'_ _\n**{ctx.author}** Unlocked the Channel {channel.mention}', color = discord.Color.red())
            await ctx.send(embed=embed)
        else:
            await confirmation.update("Not confirmed", hide_author=True, color=0xff5555)
            
def setup(bot):
    bot.add_cog(Mod(bot))
    # bot.add_cog(ModEvents(bot))
