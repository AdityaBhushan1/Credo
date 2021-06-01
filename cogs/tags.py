from .utils import formats,emote
from .utils.paginitators import SimplePages

from discord.ext import commands
from .utils import menus
import io
import discord
import asyncio
import asyncpg
import argparse
import shlex

from disputils import BotConfirmation

class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)

class UnavailableTagCommand(commands.CheckFailure):
    def __str__(self):
        return 'Sorry. This command is unavailable in private messages.\n' \
               'Consider browsing or using the tag box instead.\nSee ?tag box for more info.'

class UnableToUseBox(commands.CheckFailure):
    def __str__(self):
        return f'{emote.error} | You do not have permissions to use the tag box. Manage Messages required!'

def suggest_box():
    """Custom commands.guild_only with different error checking."""
    def pred(ctx):
        if ctx.guild is None:
            raise UnavailableTagCommand()
        return True
    return commands.check(pred)

class TagPageEntry:
    __slots__ = ('id', 'name')
    def __init__(self, entry):
        self.id = entry['id']
        self.name = entry['name']

    def __str__(self):
        return f'{self.name} (ID: {self.id})'

class TagPages(SimplePages):
    def __init__(self, entries, *, per_page=12):
        converted = [TagPageEntry(entry) for entry in entries]
        super().__init__(converted, per_page=per_page)

def can_use_box():
    def pred(ctx):
        if ctx.guild is None:
            return True
        if ctx.author.id == ctx.bot.owner_id:
            return True

        has_perms = ctx.channel.permissions_for(ctx.author).manage_messages
        if not has_perms:
            raise UnableToUseBox()

        return True
    return commands.check(pred)

class TagName(commands.clean_content):
    def __init__(self, *, lower=False):
        self.lower = lower
        super().__init__()

    async def convert(self, ctx, argument):
        converted = await super().convert(ctx, argument)
        lower = converted.lower().strip()

        if not lower:
            raise commands.BadArgument( f'{emote.error} | Missing tag name.')

        if len(lower) > 100:
            raise commands.BadArgument( f'{emote.error} | Tag name is a maximum of 100 characters.')

        first_word, _, _ = lower.partition(' ')

        # get tag command.
        root = ctx.bot.get_command('tag')
        if first_word in root.all_commands:
            raise commands.BadArgument( f'{emote.error} | This tag name starts with a reserved word.')

        return converted if not self.lower else lower

class FakeUser(discord.Object):
    @property
    def avatar_url(self):
        return 'https://cdn.discordapp.com/embed/avatars/0.png'

    @property
    def display_name(self):
        return str(self.id)

    def __str__(self):
        return str(self.id)

class TagMember(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument as e:
            if argument.isdigit():
                return FakeUser(id=int(argument))
            raise e

class Tags(commands.Cog):
    """The tag related commands."""

    def __init__(self, bot):
        self.bot = bot

        # guild_id: set(name)
        self._reserved_tags_being_made = {}

    async def cog_command_error(self, ctx, error):
        if isinstance(error, (UnavailableTagCommand, UnableToUseBox)):
            await ctx.send(error)
        else:
            await ctx.send(error)

    async def get_possible_tags(self, guild, *, connection=None):
        """Returns a list of Records of possible tags that the guild can execute.
        If this is a private message then only the generic tags are possible.
        Server specific tags will override the generic tags.
        """

        con = connection or self.bot.db
        if guild is None:
            query = """SELECT name, content FROM tags WHERE location_id IS NULL;"""
            return await con.fetch(query)

        query = """SELECT name, content FROM tags WHERE location_id=$1;"""
        return con.fetch(query, guild.id)

    async def get_random_tag(self, guild, *, connection=None):
        """Returns a random tag."""

        con = connection or self.bot.db
        pred = 'location_id IS NULL' if guild is None else 'location_id=$1'
        query = f"""SELECT name, content
                    FROM tags
                    WHERE {pred}
                    OFFSET FLOOR(RANDOM() * (
                        SELECT COUNT(*)
                        FROM tags
                        WHERE {pred}
                    ))
                    LIMIT 1;
                 """

        if guild is None:
            return await con.fetchrow(query)
        else:
            return await con.fetchrow(query, guild.id)

    async def get_tag(self, guild_id, name, *, connection=None):
        def disambiguate(rows, query):
            if rows is None or len(rows) == 0:
                raise RuntimeError( f'{emote.error} | Tag not found.')

            names = '\n'.join(r['name'] for r in rows)
            raise RuntimeError(f'{emote.error} | Tag not found. Did you mean...\n{names}')

        con = connection or self.bot.db

        query = """SELECT tags.name, tags.content
                   FROM tag_lookup
                   INNER JOIN tags ON tags.id = tag_lookup.tag_id
                   WHERE tag_lookup.location_id=$1 AND LOWER(tag_lookup.name)=$2;
                """

        row = await con.fetchrow(query, guild_id, name)
        if row is None:
            query = """SELECT     tag_lookup.name
                       FROM       tag_lookup
                       WHERE      tag_lookup.location_id=$1 AND tag_lookup.name % $2
                       ORDER BY   similarity(tag_lookup.name, $2) DESC
                       LIMIT 3;
                    """

            return disambiguate(await con.fetch(query, guild_id, name), name)
        else:
            return row

    async def create_tag(self, ctx, name, content):
        # due to our denormalized design, I need to insert the tag in two different
        # tables, make sure it's in a transaction so if one of the inserts fail I
        # can act upon it
        query = """WITH tag_insert AS (
                        INSERT INTO tags (name, content, owner_id, location_id)
                        VALUES ($1, $2, $3, $4)
                        RETURNING id
                    )
                    INSERT INTO tag_lookup (name, owner_id, location_id, tag_id)
                    VALUES ($1, $3, $4, (SELECT id FROM tag_insert));
                """

        # since I'm checking for the exception type and acting on it, I need
        # to use the manual transaction blocks

        async with ctx.acquire():
            tr = ctx.db.transaction()
            await tr.start()

            try:
                await ctx.db.execute(query, name, content, ctx.author.id, ctx.guild.id)
            except asyncpg.UniqueViolationError:
                await tr.rollback()
                await ctx.send( f'{emote.error} | This tag already exists.')
            except:
                await tr.rollback()
                await ctx.send( f'{emote.error} | Could not create tag.')
            else:
                await tr.commit()
                await ctx.send(f'{emote.tick} | Tag {name} successfully created.')

    def is_tag_being_made(self, guild_id, name):
        try:
            being_made = self._reserved_tags_being_made[guild_id]
        except KeyError:
            return False
        else:
            return name.lower() in being_made

    def add_in_progress_tag(self, guild_id, name):
        tags = self._reserved_tags_being_made.setdefault(guild_id, set())
        tags.add(name.lower())

    def remove_in_progress_tag(self, guild_id, name):
        try:
            being_made = self._reserved_tags_being_made[guild_id]
        except KeyError:
            return

        being_made.discard(name.lower())
        if len(being_made) == 0:
            del self._reserved_tags_being_made[guild_id]

    @commands.group(invoke_without_command=True)
    @suggest_box()
    async def tag(self, ctx, *, name: TagName(lower=True)):
        """Allows you to tag text for later retrieval.
        
        If a subcommand is not called, then this will search the tag database
        for the tag requested.
        """

        try:
            tag = await self.get_tag(ctx.guild.id, name, connection=ctx.db)
        except RuntimeError as e:
            return await ctx.send(e)

        await ctx.send(tag['content'], reference=ctx.replied_reference)

        # update the usage
        query = "UPDATE tags SET uses = uses + 1 WHERE name = $1 AND (location_id=$2 OR location_id IS NULL);"
        await ctx.db.execute(query, tag['name'], ctx.guild.id)

    @tag.command(aliases=['add'])
    @suggest_box()
    async def create(self, ctx, name: TagName, *, content: commands.clean_content):
        """Creates a new tag owned by you.
        This tag is server-specific and cannot be used in other servers.
        For global tags that others can use, consider using the tag box.
        Note that server moderators can delete your tag.
        """

        if self.is_tag_being_made(ctx.guild.id, name):
            return await ctx.send( f'{emote.error} | This tag is currently being made by someone.')

        await self.create_tag(ctx, name, content)

    @tag.command()
    @suggest_box()
    async def alias(self, ctx, new_name: TagName, *, old_name: TagName):
        """Creates an alias for a pre-existing tag.
        You own the tag alias. However, when the original
        tag is deleted the alias is deleted as well.
        Tag aliases cannot be edited. You must delete
        the alias and remake it to point it to another
        location.
        """

        query = """INSERT INTO tag_lookup (name, owner_id, location_id, tag_id)
                   SELECT $1, $4, tag_lookup.location_id, tag_lookup.tag_id
                   FROM tag_lookup
                   WHERE tag_lookup.location_id=$3 AND LOWER(tag_lookup.name)=$2;
                """

        try:
            status = await ctx.db.execute(query, new_name, old_name.lower(), ctx.guild.id, ctx.author.id)
        except asyncpg.UniqueViolationError:
            await ctx.send(f'{emote.error} | A tag with this name already exists.')
        else:
            # The status returns INSERT N M, where M is the number of rows inserted.
            if status[-1] == '0':
                await ctx.send(f'{emote.error} | A tag with the name of "{old_name}" does not exist.')
            else:
                await ctx.send(f'{emote.tick} | Tag alias "{new_name}" that points to "{old_name}" successfully created.')

    @tag.command(ignore_extra=False)
    @suggest_box()
    async def make(self, ctx):
        """Interactive makes a tag for you.
        This walks you through the process of creating a tag with
        its name and its content. This works similar to the tag
        create command.
        """

        await ctx.send('Hello. What would you like the name tag to be?')

        converter = TagName()
        original = ctx.message

        def check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        # release the connection back to the db to wait for our user
        await ctx.release()

        try:
            name = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send( f'{emote.error} | You took long. Goodbye.')

        try:
            ctx.message = name
            name = await converter.convert(ctx, name.content)
        except commands.BadArgument as e:
            return await ctx.send(f'{e}. Redo the command "{ctx.prefix}tag make" to retry.')
        finally:
            ctx.message = original

        if self.is_tag_being_made(ctx.guild.id, name):
            return await ctx.send( f'{emote.error} | Sorry. This tag is currently being made by someone. ' \
                                 f'Redo the command "{ctx.prefix}tag make" to retry.')

        # reacquire our connection since we need the query
        await ctx.acquire()

        # it's technically kind of expensive to do two queries like this
        # i.e. one to check if it exists and then another that does the insert
        # while also checking if it exists due to the constraints,
        # however for UX reasons I might as well do it.

        query = """SELECT 1 FROM tags WHERE location_id=$1 AND LOWER(name)=$2;"""
        row = await ctx.db.fetchrow(query, ctx.guild.id, name.lower())
        if row is not None:
            return await ctx.send( f'{emote.error} | Sorry. A tag with that name already exists. ' \
                                 f'Redo the command "{ctx.prefix}tag make" to retry.')


        self.add_in_progress_tag(ctx.guild.id, name)
        await ctx.send(f'Neat. So the name is {name}. What about the tag\'s content? ' \
                       f'**You can type {ctx.prefix}abort to abort the tag make process.**')

        # release while we wait for response
        await ctx.release()

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
        except asyncio.TimeoutError:
            self.remove_in_progress_tag(ctx.guild.id, name)
            return await ctx.send( f'{emote.error} | You took too long. Goodbye.')

        if msg.content == f'{ctx.prefix}abort':
            self.remove_in_progress_tag(ctx.guild.id, name)
            return await ctx.send('Aborting.')
        elif msg.content:
            clean_content = await commands.clean_content().convert(ctx, msg.content)
        else:
            # fast path I guess?
            clean_content = msg.content

        if msg.attachments:
            clean_content = f'{clean_content}\n{msg.attachments[0].url}'

        try:
            await self.create_tag(ctx, name, clean_content)
        finally:
            self.remove_in_progress_tag(ctx.guild.id, name)

    @make.error
    async def tag_make_error(self, ctx, error):
        if isinstance(error, commands.TooManyArguments):
            await ctx.send(f'Please call just {ctx.prefix}tag make')


    @tag.command()
    @suggest_box()
    async def edit(self, ctx, name: TagName(lower=True), *, content: commands.clean_content):
        """Modifies an existing tag that you own.
        This command completely replaces the original text. If
        you want to get the old text back, consider using the
        tag raw command.
        """

        query = "UPDATE tags SET content=$1 WHERE LOWER(name)=$2 AND location_id=$3 AND owner_id=$4;"
        status = await ctx.db.execute(query, content, name, ctx.guild.id, ctx.author.id)

        # the status returns UPDATE <count>
        # if the <count> is 0, then nothing got updated
        # probably due to the WHERE clause failing

        if status[-1] == '0':
            await ctx.send( f'{emote.error} | Could not edit that tag. Are you sure it exists and you own it?')
        else:
            await ctx.send( f'{emote.tick} | Successfully edited tag.')

    @tag.command(aliases=['delete'])
    @suggest_box()
    async def remove(self, ctx, *, name: TagName(lower=True)):
        """Removes a tag that you own.
        The tag owner can always delete their own tags. If someone requests
        deletion and has Manage Server permissions then they can also
        delete it.
        Deleting a tag will delete all of its aliases as well.
        """

        bypass_owner_check = ctx.author.id == self.bot.owner_id or ctx.author.guild_permissions.manage_messages
        clause = 'LOWER(name)=$1 AND location_id=$2'

        if bypass_owner_check:
            args = [name, ctx.guild.id]
        else:
            args = [name, ctx.guild.id, ctx.author.id]
            clause = f'{clause} AND owner_id=$3'

        query = f'DELETE FROM tag_lookup WHERE {clause} RETURNING tag_id;'
        deleted = await ctx.db.fetchrow(query, *args)

        if deleted is None:
            await ctx.send('Could not delete tag. Either it does not exist or you do not have permissions to do so.')
            return

        args.append(deleted[0])
        query = f'DELETE FROM tags WHERE id=${len(args)} AND {clause};'
        status = await ctx.db.execute(query, *args)

        # the status returns DELETE <count>, similar to UPDATE above
        if status[-1] == '0':
            # this is based on the previous delete above
            await ctx.send( f'{emote.tick} | Tag alias successfully deleted.')
        else:
            await ctx.send( f'{emote.tick} | Tag and corresponding aliases successfully deleted.')

    @tag.command(aliases=['delete_id'])
    @suggest_box()
    async def remove_id(self, ctx, tag_id: int):
        """Removes a tag by ID.
        The tag owner can always delete their own tags. If someone requests
        deletion and has Manage Server permissions then they can also
        delete it.
        Deleting a tag will delete all of its aliases as well.
        """

        bypass_owner_check = ctx.author.id == self.bot.owner_id or ctx.author.guild_permissions.manage_messages
        clause = 'id=$1 AND location_id=$2'

        if bypass_owner_check:
            args = [tag_id, ctx.guild.id]
        else:
            args = [tag_id, ctx.guild.id, ctx.author.id]
            clause = f'{clause} AND owner_id=$3'

        query = f'DELETE FROM tag_lookup WHERE {clause} RETURNING tag_id;'
        deleted = await ctx.db.fetchrow(query, *args)

        if deleted is None:
            await ctx.send( f'{emote.error} | Could not delete tag. Either it does not exist or you do not have permissions to do so.')
            return


        if bypass_owner_check:
            clause = 'id=$1 AND location_id=$2'
            args = [deleted[0], ctx.guild.id]
        else:
            clause = 'id=$1 AND location_id=$2 AND owner_id=$3'
            args = [deleted[0], ctx.guild.id, ctx.author.id]

        query = f'DELETE FROM tags WHERE {clause};'
        status = await ctx.db.execute(query, *args)

        # the status returns DELETE <count>, similar to UPDATE above
        if status[-1] == '0':
            # this is based on the previous delete above
            await ctx.send( f'{emote.tick} | Tag alias successfully deleted.')
        else:
            await ctx.send( f'{emote.error} | Tag and corresponding aliases successfully deleted.')

    async def _send_alias_info(self, ctx, record):
        embed = discord.Embed(colour=self.bot.color)

        owner_id = record['lookup_owner_id']
        embed.title = record['lookup_name']
        embed.timestamp = record['lookup_created_at']
        embed.set_footer(text='Alias created at')

        user = self.bot.get_user(owner_id) or (await self.bot.fetch_user(owner_id))
        embed.set_author(name=str(user), icon_url=user.avatar_url)

        embed.add_field(name='Owner', value=f'<@{owner_id}>')
        embed.add_field(name='Original', value=record['name'])
        await ctx.send(embed=embed)

    async def _send_tag_info(self, ctx, record):
        embed = discord.Embed(colour=self.bot.color)

        owner_id = record['owner_id']
        embed.title = record['name']
        embed.timestamp = record['created_at']
        embed.set_footer(text='Tag created at')

        user = self.bot.get_user(owner_id) or (await self.bot.fetch_user(owner_id))
        embed.set_author(name=str(user), icon_url=user.avatar_url)

        embed.add_field(name='Owner', value=f'<@{owner_id}>')
        embed.add_field(name='Uses', value=record['uses'])

        query = """SELECT (
                       SELECT COUNT(*)
                       FROM tags second
                       WHERE (second.uses, second.id) >= (first.uses, first.id)
                         AND second.location_id = first.location_id
                   ) AS rank
                   FROM tags first
                   WHERE first.id=$1
                """

        rank = await ctx.db.fetchrow(query, record['id'])

        if rank is not None:
            embed.add_field(name='Rank', value=rank['rank'])

        await ctx.send(embed=embed)

    @tag.command( aliases=['owner'])
    @suggest_box()
    async def info(self, ctx, *, name: TagName(lower=True)):
        """Retrieves info about a tag.
        The info includes things like the owner and how many times it was used.
        """

        query = """SELECT
                       tag_lookup.name <> tags.name AS "Alias",
                       tag_lookup.name AS lookup_name,
                       tag_lookup.created_at AS lookup_created_at,
                       tag_lookup.owner_id AS lookup_owner_id,
                       tags.*
                   FROM tag_lookup
                   INNER JOIN tags ON tag_lookup.tag_id = tags.id
                   WHERE LOWER(tag_lookup.name)=$1 AND tag_lookup.location_id=$2
                """

        record = await ctx.db.fetchrow(query, name, ctx.guild.id)
        if record is None:
            return await ctx.send( f'{emote.error} | Tag not found.')

        if record['Alias']:
            await self._send_alias_info(ctx, record)
        else:
            await self._send_tag_info(ctx, record)

    @tag.command(pass_context=True)
    @suggest_box()
    async def raw(self, ctx, *, name: TagName(lower=True)):
        """Gets the raw content of the tag.
        This is with markdown escaped. Useful for editing.
        """

        try:
            tag = await self.get_tag(ctx.guild.id, name, connection=ctx.db)
        except RuntimeError as e:
            return await ctx.send(e)

        first_step = discord.utils.escape_markdown(tag['content'])
        await ctx.safe_send(first_step.replace('<', '\\<'), escape_mentions=False)

    @tag.command(name='list')
    @suggest_box()
    async def _list(self, ctx, *, member: TagMember = None):
        """Lists all the tags that belong to you or someone else."""

        member = member or ctx.author

        query = """SELECT name, id
                   FROM tag_lookup
                   WHERE location_id=$1 AND owner_id=$2
                   ORDER BY name
                """

        rows = await ctx.db.fetch(query, ctx.guild.id, member.id)
        await ctx.release()

        if rows:
            try:
                p = TagPages(entries=rows)
                p.embed.set_author(name=member.display_name, icon_url=member.avatar_url)
                await p.start(ctx)
            except menus.MenuError as e:
                await ctx.send(e)
        else:
            await ctx.send(f'{member} has no tags.')

    @commands.command()
    @suggest_box()
    async def tags(self, ctx, *, member: TagMember = None):
        """An alias for tag list command."""
        await ctx.invoke(self._list, member=member)

    @staticmethod
    def _get_tag_all_arguments(args):
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--text', action='store_true')
        if args is not None:
            return parser.parse_args(shlex.split(args))
        else:
            return parser.parse_args([])

    async def _tag_all_text_mode(self, ctx):
        query = """SELECT tag_lookup.id,
                          tag_lookup.name,
                          tag_lookup.owner_id,
                          tags.uses,
                          $2 OR $3 = tag_lookup.owner_id AS "can_delete",
                          LOWER(tag_lookup.name) <> LOWER(tags.name) AS "is_alias"
                   FROM tag_lookup
                   INNER JOIN tags ON tags.id = tag_lookup.tag_id
                   WHERE tag_lookup.location_id=$1
                   ORDER BY tags.uses DESC;
                """

        bypass_owner_check = ctx.author.id == self.bot.owner_id or ctx.author.guild_permissions.manage_messages
        rows = await ctx.db.fetch(query, ctx.guild.id, bypass_owner_check, ctx.author.id)
        if not rows:
            return await ctx.send( f'{emote.error} | This server has no server-specific tags.')

        table = formats.TabularData()
        table.set_columns(list(rows[0].keys()))
        table.add_rows(list(r.values()) for r in rows)
        fp = io.BytesIO(table.render().encode('utf-8'))
        await ctx.send(file=discord.File(fp, 'tags.txt'))

    @tag.command(name='all')
    @suggest_box()
    async def _all(self, ctx, *, args: str = None):
        """Lists all server-specific tags for this server.
        You can pass specific flags to this command to control the output:
        `--text`: Dumps into a text file
        """

        try:
            args = self._get_tag_all_arguments(args)
        except RuntimeError as e:
            return await ctx.send(e)

        if args.text:
            return await self._tag_all_text_mode(ctx)

        query = """SELECT name, id
                   FROM tag_lookup
                   WHERE location_id=$1
                   ORDER BY name
                """

        rows = await ctx.db.fetch(query, ctx.guild.id)
        await ctx.release()

        if rows:
            # PSQL orders this oddly for some reason
            try:
                p = TagPages(entries=rows, per_page=20)
                await p.start(ctx)
            except menus.MenuError as e:
                await ctx.send(e)
        else:
            await ctx.send( f'{emote.error} | This server has no server-specific tags.')

    @tag.command()
    @suggest_box()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, member: TagMember):
        """Removes all server-specific tags by a user.
        You must have server-wide Manage Messages permissions to use this.
        """

        # Though inefficient, for UX purposes we should do two queries

        query = "SELECT COUNT(*) FROM tags WHERE location_id=$1 AND owner_id=$2;"
        count = await ctx.db.fetchrow(query, ctx.guild.id, member.id)
        count = count[0] # COUNT(*) always returns 0 or higher

        if count == 0:
            return await ctx.send(f'{member} does not have any tags to purge.')

        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"This will delete {count} tags are you sure? **This action cannot be reversed**.")
        if confirmation.confirmed:
            await confirmation.update(f"{emote.tick} | Successfully removed all {count} tags that belong to {member}.", color=self.bot.color)
            query = "DELETE FROM tags WHERE location_id=$1 AND owner_id=$2;"
            await ctx.db.execute(query, ctx.guild.id, member.id)
        else:
            await confirmation.update("Cancelling tag purge request.", hide_author=True, color=0xff5555)

    @tag.command()
    @suggest_box()
    async def search(self, ctx, *, query: commands.clean_content):
        """Searches for a tag.
        The query must be at least 3 characters.
        """

        if len(query) < 3:
            return await ctx.send(f'{emote.error} | The query length must be at least three characters.')

        sql = """SELECT name, id
                 FROM tag_lookup
                 WHERE location_id=$1 AND name % $2
                 ORDER BY similarity(name, $2) DESC
                 LIMIT 100;
              """

        results = await ctx.db.fetch(sql, ctx.guild.id, query)

        if results:
            try:
                p = TagPages(entries=results, per_page=20)
            except menus.MenuError as e:
                await ctx.send(e)
            else:
                await ctx.release()
                await p.start(ctx)
        else:
            await ctx.send(f'{emote.error} | No tags found.')

    @tag.command()
    @suggest_box()
    async def claim(self, ctx, *, tag: TagName):
        """Claims an unclaimed tag.
        An unclaimed tag is a tag that effectively
        has no owner because they have left the server.
        """

        alias = False
        # requires 2 queries for UX
        query = "SELECT id, owner_id FROM tags WHERE location_id=$1 AND LOWER(name)=$2;"
        row = await ctx.db.fetchrow(query, ctx.guild.id, tag.lower())
        if row is None:
            alias_query = "SELECT tag_id, owner_id FROM tag_lookup WHERE location_id = $1 and LOWER(name) = $2;"
            row = await ctx.db.fetchrow(alias_query, ctx.guild.id, tag.lower())
            if row is None:
                return await ctx.send(f'{emote.error} | A tag with the name of "{tag}" does not exist.')
            alias = True

        member = await self.bot.get_or_fetch_member(ctx.guild, row[1])
        if member is not None:
            return await ctx.send(f'{emote.error} | Tag owner is still in server.')

        async with ctx.acquire():
            async with ctx.db.transaction():
                if not alias:
                    query = "UPDATE tags SET owner_id=$1 WHERE id=$2;"
                    await ctx.db.execute(query, ctx.author.id, row[0])
                query = "UPDATE tag_lookup SET owner_id=$1 WHERE tag_id=$2;"
                await ctx.db.execute(query, ctx.author.id, row[0])

            await ctx.send(f'{emote.tick} | Successfully transferred tag ownership to you.')

    @tag.command()
    @suggest_box()
    async def transfer(self, ctx, member: discord.Member, *, tag: TagName):
        """Transfers a tag to another member.
        You must own the tag before doing this.
        """

        if member.bot:
            return await ctx.send('You cannot transfer a tag to a bot.')
        query = "SELECT id FROM tags WHERE location_id=$1 AND LOWER(name)=$2 AND owner_id=$3;"
        row = await ctx.db.fetchrow(query, ctx.guild.id, tag.lower(), ctx.author.id)
        if row is None:
            return await ctx.send(f'{emote.error} | A tag with the name of "{tag}" does not exist or is not owned by you.')

        async with ctx.acquire():
            async with ctx.db.transaction():
                query = "UPDATE tags SET owner_id=$1 WHERE id=$2;"
                await ctx.db.execute(query, member.id, row[0])
                query = "UPDATE tag_lookup SET owner_id=$1 WHERE tag_id=$2;"
                await ctx.db.execute(query, member.id, row[0])

        await ctx.send(f'{emote.tick} | Successfully transferred tag ownership to {member}.')

def setup(bot):
    bot.add_cog(Tags(bot))