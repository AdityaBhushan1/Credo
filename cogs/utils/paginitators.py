#these all are not my paginitators
# some paginatators are wrriten by me and some are taken bye the following repos
# https://github.com/Rapptz/RoboDanny
# https://github.com/quotientbot/Quotient-Bot
# https://github.com/Gorialis/jishaku

import asyncio
import collections
import re
import discord
from .languagess import get_language
from discord.ext.buttons import Paginator
from discord.ext import commands,menus
from discord.ext.commands import Paginator as CommandPaginator
from . import emote



# ##########################################################################################################################
class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

__all__ = ('EmojiSettings', 'PaginatorInterface', 'PaginatorEmbedInterface',
           'WrappedPaginator', 'FilePaginator','TeaPages','FieldPageSource','TextPageSource','SimplePageSource','SimplePages')


# emoji settings, this sets what emoji are used for PaginatorInterface
EmojiSettings = collections.namedtuple('EmojiSettings', 'start back forward end close')

EMOJI_DEFAULT = EmojiSettings(
    start="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}",
    back="\N{BLACK LEFT-POINTING TRIANGLE}",
    forward="\N{BLACK RIGHT-POINTING TRIANGLE}",
    end="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}",
    close="\N{BLACK SQUARE FOR STOP}"
)


class PaginatorInterface:  # pylint: disable=too-many-instance-attributes
    """
    A message and reaction based interface for paginators.

    This allows users to interactively navigate the pages of a Paginator, and supports live output.

    An example of how to use this with a standard Paginator:

    .. code:: python3

        from discord.ext import commands

        from jishaku.paginators import PaginatorInterface

        # In a command somewhere...
            # Paginators need to have a reduced max_size to accommodate the extra text added by the interface.
            paginator = commands.Paginator(max_size=1900)

            # Populate the paginator with some information
            for line in range(100):
                paginator.add_line(f"Line {line + 1}")

            # Create and send the interface.
            # The 'owner' field determines who can interact with this interface. If it's None, anyone can use it.
            interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
            await interface.send_to(ctx)

            # send_to creates a task and returns control flow.
            # It will raise if the interface can't be created, e.g., if there's no reaction permission in the channel.
            # Once the interface has been sent, line additions have to be done asynchronously, so the interface can be updated.
            await interface.add_line("My, the Earth sure is full of things!")

            # You can also check if it's closed using the 'closed' property.
            if not interface.closed:
                await interface.add_line("I'm still here!")
    """

    def __init__(self, bot: commands.Bot, paginator: commands.Paginator, **kwargs):
        if not isinstance(paginator, commands.Paginator):
            raise TypeError('paginator must be a commands.Paginator instance')

        self._display_page = 0

        self.bot = bot

        self.message = None
        self.paginator = paginator

        self.owner = kwargs.pop('owner', None)
        self.emojis = kwargs.pop('emoji', EMOJI_DEFAULT)
        self.timeout = kwargs.pop('timeout', 7200)
        self.delete_message = kwargs.pop('delete_message', False)

        self.sent_page_reactions = False

        self.task: asyncio.Task = None
        self.send_lock: asyncio.Event = asyncio.Event()
        self.update_lock: asyncio.Lock = asyncio.Semaphore(value=kwargs.pop('update_max', 2))

        if self.page_size > self.max_page_size:
            raise ValueError(
                f'Paginator passed has too large of a page size for this interface. '
                f'({self.page_size} > {self.max_page_size})'
            )

    @property
    def pages(self):
        """
        Returns the paginator's pages without prematurely closing the active page.
        """
        # protected access has to be permitted here to not close the paginator's pages

        # pylint: disable=protected-access
        paginator_pages = list(self.paginator._pages)
        if len(self.paginator._current_page) > 1:
            paginator_pages.append('\n'.join(self.paginator._current_page) + '\n' + (self.paginator.suffix or ''))
        # pylint: enable=protected-access

        return paginator_pages

    @property
    def page_count(self):
        """
        Returns the page count of the internal paginator.
        """

        return len(self.pages)

    @property
    def display_page(self):
        """
        Returns the current page the paginator interface is on.
        """

        self._display_page = max(0, min(self.page_count - 1, self._display_page))
        return self._display_page

    @display_page.setter
    def display_page(self, value):
        """
        Sets the current page the paginator is on. Automatically pushes values inbounds.
        """

        self._display_page = max(0, min(self.page_count - 1, value))

    max_page_size = 2000

    @property
    def page_size(self) -> int:
        """
        A property that returns how large a page is, calculated from the paginator properties.

        If this exceeds `max_page_size`, an exception is raised upon instantiation.
        """
        page_count = self.page_count
        return self.paginator.max_size + len(f'\nPage {page_count}/{page_count}')

    @property
    def send_kwargs(self) -> dict:
        """
        A property that returns the kwargs forwarded to send/edit when updating the page.

        As this must be compatible with both `discord.TextChannel.send` and `discord.Message.edit`,
        it should be a dict containing 'content', 'embed' or both.
        """

        display_page = self.display_page
        page_num = f'\nPage {display_page + 1}/{self.page_count}'
        content = self.pages[display_page] + page_num
        return {'content': content}

    async def add_line(self, *args, **kwargs):
        """
        A proxy function that allows this PaginatorInterface to remain locked to the last page
        if it is already on it.
        """

        display_page = self.display_page
        page_count = self.page_count

        self.paginator.add_line(*args, **kwargs)

        new_page_count = self.page_count

        if display_page + 1 == page_count:
            # To keep position fixed on the end, update position to new last page and update message.
            self._display_page = new_page_count
            self.bot.loop.create_task(self.update())

    async def send_to(self, destination: discord.abc.Messageable):
        """
        Sends a message to the given destination with this interface.

        This automatically creates the response task for you.
        """

        self.message = await destination.send(**self.send_kwargs)

        # add the close reaction
        await self.message.add_reaction(self.emojis.close)

        self.send_lock.set()

        if self.task:
            self.task.cancel()

        self.task = self.bot.loop.create_task(self.wait_loop())

        # if there is more than one page, and the reactions haven't been sent yet, send navigation emotes
        if not self.sent_page_reactions and self.page_count > 1:
            await self.send_all_reactions()

        return self

    async def send_all_reactions(self):
        """
        Sends all reactions for this paginator, if any are missing.

        This method is generally for internal use only.
        """

        for emoji in filter(None, self.emojis):
            try:
                await self.message.add_reaction(emoji)
            except discord.NotFound:
                # the paginator has probably already been closed
                break
        self.sent_page_reactions = True

    @property
    def closed(self):
        """
        Is this interface closed?
        """

        if not self.task:
            return False
        return self.task.done()

    async def wait_loop(self):
        """
        Waits on a loop for reactions to the message. This should not be called manually - it is handled by `send_to`.
        """

        start, back, forward, end, close = self.emojis

        def check(payload: discord.RawReactionActionEvent):
            """
            Checks if this reaction is related to the paginator interface.
            """

            owner_check = not self.owner or payload.user_id == self.owner.id

            emoji = payload.emoji
            if isinstance(emoji, discord.PartialEmoji) and emoji.is_unicode_emoji():
                emoji = emoji.name

            tests = (
                owner_check,
                payload.message_id == self.message.id,
                emoji,
                emoji in self.emojis,
                payload.user_id != self.bot.user.id
            )

            return all(tests)

        try:
            while not self.bot.is_closed():
                payload = await self.bot.wait_for('raw_reaction_add', check=check, timeout=self.timeout)

                emoji = payload.emoji
                if isinstance(emoji, discord.PartialEmoji) and emoji.is_unicode_emoji():
                    emoji = emoji.name

                if emoji == close:
                    await self.message.delete()
                    return

                if emoji == start:
                    self._display_page = 0
                elif emoji == end:
                    self._display_page = self.page_count - 1
                elif emoji == back:
                    self._display_page -= 1
                elif emoji == forward:
                    self._display_page += 1

                self.bot.loop.create_task(self.update())

                try:
                    await self.message.remove_reaction(payload.emoji, discord.Object(id=payload.user_id))
                except discord.Forbidden:
                    pass

        except (asyncio.CancelledError, asyncio.TimeoutError):
            if self.delete_message:
                return await self.message.delete()

            for emoji in filter(None, self.emojis):
                try:
                    await self.message.remove_reaction(emoji, self.bot.user)
                except (discord.Forbidden, discord.NotFound):
                    pass

    async def update(self):
        """
        Updates this interface's messages with the latest data.
        """

        if self.update_lock.locked():
            return

        await self.send_lock.wait()

        async with self.update_lock:
            if self.update_lock.locked():
                # if this engagement has caused the semaphore to exhaust,
                # we are overloaded and need to calm down.
                await asyncio.sleep(1)

            if not self.message:
                # too fast, stagger so this update gets through
                await asyncio.sleep(0.5)

            if not self.sent_page_reactions and self.page_count > 1:
                self.bot.loop.create_task(self.send_all_reactions())
                self.sent_page_reactions = True  # don't spawn any more tasks

            try:
                await self.message.edit(**self.send_kwargs)
            except discord.NotFound:
                # something terrible has happened
                if self.task:
                    self.task.cancel()


class PaginatorEmbedInterface(PaginatorInterface):
    """
    A subclass of :class:`PaginatorInterface` that encloses content in an Embed.
    """

    def __init__(self, *args, **kwargs):
        self._embed = kwargs.pop('embed', None) or discord.Embed()
        super().__init__(*args, **kwargs)

    @property
    def send_kwargs(self) -> dict:
        display_page = self.display_page
        self._embed.description = self.pages[display_page]
        self._embed.set_footer(text=f'Page {display_page + 1}/{self.page_count}')
        return {'embed': self._embed}

    max_page_size = 2048

    @property
    def page_size(self) -> int:
        return self.paginator.max_size


class WrappedPaginator(commands.Paginator):
    """
    A paginator that allows automatic wrapping of lines should they not fit.

    This is useful when paginating unpredictable output,
    as it allows for line splitting on big chunks of data.

    Delimiters are prioritized in the order of their tuple.

    Parameters
    -----------
    wrap_on: tuple
        A tuple of wrapping delimiters.
    include_wrapped: bool
        Whether to include the delimiter at the start of the new wrapped line.
    force_wrap: bool
        If this is True, lines will be split at their maximum points should trimming not be possible
        with any provided delimiter.
    """

    def __init__(self, *args, wrap_on=('\n', ' '), include_wrapped=True, force_wrap=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrap_on = wrap_on
        self.include_wrapped = include_wrapped
        self.force_wrap = force_wrap

    def add_line(self, line='', *, empty=False):
        true_max_size = self.max_size - self._prefix_len - self._suffix_len - 2
        original_length = len(line)

        while len(line) > true_max_size:
            search_string = line[0:true_max_size - 1]
            wrapped = False

            for delimiter in self.wrap_on:
                position = search_string.rfind(delimiter)

                if position > 0:
                    super().add_line(line[0:position], empty=empty)
                    wrapped = True

                    if self.include_wrapped:
                        line = line[position:]
                    else:
                        line = line[position + len(delimiter):]

                    break

            if not wrapped:
                if self.force_wrap:
                    super().add_line(line[0:true_max_size - 1])
                    line = line[true_max_size - 1:]
                else:
                    raise ValueError(
                        f"Line of length {original_length} had sequence of {len(line)} characters"
                        f" (max is {true_max_size}) that WrappedPaginator could not wrap with"
                        f" delimiters: {self.wrap_on}"
                    )

        super().add_line(line, empty=empty)


class FilePaginator(commands.Paginator):
    """
    A paginator of syntax-highlighted codeblocks, read from a file-like.

    Parameters
    -----------
    fp
        A file-like (implements ``fp.read``) to read the data for this paginator from.
    line_span: Optional[Tuple[int, int]]
        A linespan to read from the file. If None, reads the whole file.
    language_hints: Tuple[str]
        A tuple of strings that may hint to the language of this file.
        This could include filenames, MIME types, or shebangs.
        A shebang present in the actual file will always be prioritized over this.
    """

    __encoding_regex = re.compile(br'coding[=:]\s*([-\w.]+)')

    def __init__(self, fp, line_span=None, language_hints=(), **kwargs):
        language = ''

        for hint in language_hints:
            language = get_language(hint)

            if language:
                break

        if not language:
            try:
                language = get_language(fp.name)
            except AttributeError:
                pass

        raw_content = fp.read()

        try:
            lines = raw_content.decode('utf-8').split('\n')
        except UnicodeDecodeError as exc:
            # This file isn't UTF-8.

            #  By Python and text-editor convention,
            # there may be a hint as to what the actual encoding is
            # near the start of the file.

            encoding_match = self.__encoding_regex.search(raw_content[:128])

            if encoding_match:
                encoding = encoding_match.group(1)
            else:
                raise exc

            try:
                lines = raw_content.decode(encoding.decode('utf-8')).split('\n')
            except UnicodeDecodeError as exc2:
                raise exc2 from exc

        del raw_content

        # If the first line is a shebang,
        if lines[0].startswith('#!'):
            # prioritize its declaration over the extension.
            language = get_language(lines[0]) or language

        super().__init__(prefix=f'```{language}', suffix='```', **kwargs)

        if line_span:
            line_span = sorted(line_span)

            if min(line_span) < 1 or max(line_span) > len(lines):
                raise ValueError("Linespan goes out of bounds.")

            lines = lines[line_span[0] - 1:line_span[1]]

        for line in lines:
            self.add_line(line)


class WrappedFilePaginator(FilePaginator, WrappedPaginator):
    """
    Combination of FilePaginator and WrappedPaginator.
    In other words, a FilePaginator that supports line wrapping.
    """


class TeaPages(menus.MenuPages):
    def __init__(self, source):
        super().__init__(source=source, check_embeds=True)

    async def finalize(self, timed_out):
        try:
            if timed_out:
                await self.message.clear_reactions()
            else:
                await self.message.delete()
        except discord.HTTPException:
            pass

    @menus.button(emote.info, position=menus.Last(3))
    async def show_help(self, payload):
        """shows this message"""
        embed = discord.Embed(title='Paginator help', description='Hello! Welcome to the help page.',color=0x4ca64c)
        messages = []
        for (emoji, button) in self.buttons.items():
            messages.append(f'{emoji}: {button.action.__doc__}')

        embed.add_field(name='What are these reactions for?', value='\n'.join(messages), inline=False)
        embed.set_footer(text=f'We were on page {self.current_page + 1} before this message.')
        await self.message.edit(content=None, embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_page(self.current_page)

        self.bot.loop.create_task(go_back_to_current_page())

    # @menus.button('\N{INPUT SYMBOL FOR NUMBERS}', position=menus.Last(1.5))
    # async def numbered_page(self, payload):
    #     """lets you type a page number to go to"""
    #     channel = self.message.channel
    #     author_id = payload.user_id
    #     to_delete = []
    #     to_delete.append(await channel.send('What page do you want to go to?'))

    #     def message_check(m):
    #         return m.author.id == author_id and \
    #                channel == m.channel and \
    #                m.content.isdigit()

    #     try:
    #         msg = await self.bot.wait_for('message', check=message_check, timeout=30.0)
    #     except asyncio.TimeoutError:
    #         to_delete.append(await channel.send('Took too long.'))
    #         await asyncio.sleep(5)
    #     else:
    #         page = int(msg.content)
    #         to_delete.append(msg)
    #         await self.show_checked_page(page - 1)

    #     try:
    #         await channel.delete_messages(to_delete)
    #     except Exception:
    #         pass

class FieldPageSource(menus.ListPageSource):
    """A page source that requires (field_name, field_value) tuple items."""
    def __init__(self, entries, *, per_page=12):
        super().__init__(entries, per_page=per_page)
        self.embed = discord.Embed(colour=discord.Colour.green())

    async def format_page(self, menu, entries):
        self.embed.clear_fields()
        self.embed.description = discord.Embed.Empty

        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            text = f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)'
            self.embed.set_footer(text=text)

        return self.embed

class TextPageSource(menus.ListPageSource):
    def __init__(self, text, *, prefix='```', suffix='```', max_size=2000):
        pages = CommandPaginator(prefix=prefix, suffix=suffix, max_size=max_size - 200)
        for line in text.split('\n'):
            pages.add_line(line)

        super().__init__(entries=pages.pages, per_page=1)

    async def format_page(self, menu, content):
        maximum = self.get_max_pages()
        if maximum > 1:
            return f'{content}\nPage {menu.current_page + 1}/{maximum}'
        return content

class SimplePageSource(menus.ListPageSource):
    def __init__(self, entries, *, per_page=12):
        super().__init__(entries, per_page=per_page)
        self.initial_page = True

    async def format_page(self, menu, entries):
        pages = []
        for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
            pages.append(f'{index + 1}. {entry}')

        maximum = self.get_max_pages()
        if maximum > 1:
            footer = f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)'
            menu.embed.set_footer(text=footer)

        if self.initial_page and self.is_paginating():
            pages.append('')
            pages.append('Confused? React with \N{INFORMATION SOURCE} for more info.')
            self.initial_page = False

        menu.embed.description = '\n'.join(pages)
        return menu.embed

class SimplePages(TeaPages):
    """A simple pagination session reminiscent of the old Pages interface.

    Basically an embed with some normal formatting.
    """

    def __init__(self, entries, *, per_page=12):
        super().__init__(SimplePageSource(entries, per_page=per_page))
        self.embed = discord.Embed(colour=discord.Colour.green())

class CannotPaginate(Exception):
    pass


class Pages:
    def __init__(
        self,
        ctx,
        *,
        entries,
        per_page=12,
        show_entry_count=True,
        embed_color=discord.Color.green(),
        title=None,
        thumbnail=None,
        footericon=None,
        embed_author=None,
        footertext=None,
        author=None,
        delete_after=None,
    ):
        self.bot = ctx.bot
        self.entries = entries
        self.message = ctx.message
        self.channel = ctx.channel
        self.author = author if author else ctx.author
        self.thumbnail = thumbnail
        self.embed_author = embed_author

        self.footericon = footericon
        self.footertext = footertext
        self.title = title
        self.delete_after = delete_after
        self.per_page = per_page
        pages, left_over = divmod(len(self.entries), self.per_page)
        if left_over:
            pages += 1
        self.maximum_pages = pages
        self.embed = discord.Embed(colour=embed_color)
        self.paginating = True
        self.show_entry_count = show_entry_count
        self.reaction_emojis = [
            ("\U000023ee\U0000fe0f", self.first_page),
            ("\N{BLACK LEFT-POINTING TRIANGLE}", self.previous_page),
            ("\U000023f9", self.stop_pages),
            ("\N{BLACK RIGHT-POINTING TRIANGLE}", self.next_page),
            ("\U000023ed\U0000fe0f", self.last_page),
        ]

        if ctx.guild is not None:
            self.permissions = self.channel.permissions_for(ctx.guild.me)
        else:
            self.permissions = self.channel.permissions_for(ctx.bot.user)

        if not self.permissions.embed_links:
            raise commands.BotMissingPermissions("I do not have permissions to embed links.")

        if not self.permissions.send_messages:
            raise commands.BotMissingPermissions("Bot cannot send messages.")

        if self.paginating:
            # verify we can actually use the pagination session
            if not self.permissions.add_reactions:
                raise commands.BotMissingPermissions("I do not have permissions to add reactions.")

            if not self.permissions.read_message_history:
                raise commands.BotMissingPermissions("I do not have permissions to Read Message History.")

    def get_page(self, page):
        base = (page - 1) * self.per_page
        return self.entries[base : base + self.per_page]

    def get_content(self, entries, page, *, first=False):
        return None

    def get_embed(self, entries, page, *, first=False):
        self.prepare_embed(entries, page, first=first)
        return self.embed

    def prepare_embed(self, entries, page, *, first=False):
        p = []
        for index, entry in enumerate(entries, 1 + ((page - 1) * self.per_page)):
            p.append(f"{entry}")

        if self.maximum_pages > 1 and not self.footertext:
            if self.show_entry_count:
                text = f"Showing page {page}/{self.maximum_pages} ({len(self.entries)} entries)"
            else:
                text = f"Showing page {page}/{self.maximum_pages}"

            self.embed.set_footer(text=text)

        if self.footertext:
            self.embed.set_footer(text=self.footertext)

        if self.paginating and first:
            p.append("")

        self.embed.description = "".join(p)
        self.embed.title = self.title or discord.Embed.Empty
        if self.thumbnail:
            self.embed.set_thumbnail(url=self.thumbnail)
        if self.embed_author:
            self.embed.set_author(icon_url=self.author.avatar_url, name=self.embed_author)

    async def show_page(self, page, *, first=False):
        self.current_page = page
        entries = self.get_page(page)
        content = self.get_content(entries, page, first=first)
        embed = self.get_embed(entries, page, first=first)

        if not first:
            await self.message.edit(content=content, embed=embed)
            return

        self.message = await self.channel.send(content=content, embed=embed)
        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ("\U000023ee\U0000fe0f", "\U000023ed\U0000fe0f"):
                continue
            if self.maximum_pages == 1 and reaction in (
                "\U000023ee\U0000fe0f",
                "\U000023ed\U0000fe0f",
                "\N{BLACK RIGHT-POINTING TRIANGLE}",
                "\N{BLACK LEFT-POINTING TRIANGLE}",
            ):
                continue

            await self.message.add_reaction(reaction)

    async def checked_show_page(self, page):
        if page != 0 and page <= self.maximum_pages:
            await self.show_page(page)

    async def first_page(self):
        """goes to the first page"""
        await self.show_page(1)

    async def last_page(self):
        """goes to the last page"""
        await self.show_page(self.maximum_pages)

    async def next_page(self):
        """goes to the next page"""
        await self.checked_show_page(self.current_page + 1)

    async def previous_page(self):
        """goes to the previous page"""
        await self.checked_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.paginating:
            await self.show_page(self.current_page)

    async def main_help(self):
        """Goes to the main page of help"""
        await self.stop_pages()
        await self.context.send_help()

    async def numbered_page(self):
        """lets you type a page number to go to"""
        to_delete = []
        to_delete.append(await self.channel.send("What page do you want to go to?"))

        def message_check(m):
            return m.author == self.author and self.channel == m.channel and m.content.isdigit()

        try:
            msg = await self.bot.wait_for("message", check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await self.channel.send("Took too long."))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            if page != 0 and page <= self.maximum_pages:
                await self.show_page(page)
            else:
                to_delete.append(await self.channel.send(f"Invalid page given. ({page}/{self.maximum_pages})"))
                await asyncio.sleep(5)

        try:
            await self.channel.delete_messages(to_delete)
        except Exception:
            pass

    async def stop_pages(self):
        """stops the interactive pagination session"""
        await self.message.delete()
        self.paginating = False

    def react_check(self, reaction, user):
        if user is None or user.id != self.author.id:
            return False

        if reaction.message.id != self.message.id:
            return False

        for (emoji, func) in self.reaction_emojis:
            if str(reaction.emoji) == emoji:
                self.match = func
                return True
        return False

    async def paginate(self):
        """Actually paginate the entries and run the interactive loop if necessary."""
        first_page = self.show_page(1, first=True)
        # allow us to react to reactions right away if we're paginating
        self.bot.loop.create_task(first_page)

        while self.paginating:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=self.react_check, timeout=self.delete_after
                )
            except asyncio.TimeoutError:
                self.paginating = False
                try:
                    await self.message.delete()
                except Exception:
                    pass
                finally:
                    break
            try:
                await self.message.remove_reaction(reaction, user)
            except Exception:
                pass

            await self.match()