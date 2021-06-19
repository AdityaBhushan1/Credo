import discord
from discord.ext import commands
from .utils import menus
import asyncio
from .utils.paginitators import TeaPages
from .utils import emote

class Prefix(commands.Converter):
    async def convert(self, ctx, argument):
        user_id = ctx.bot.user.id
        if argument.startswith((f'<@{user_id}>', f'<@!{user_id}>')):
            raise commands.BadArgument('That is a reserved prefix already in use.')
        return argument

class BotHelpPageSource(menus.ListPageSource):
    def __init__(self, help_command, commands):
        super().__init__(entries=sorted(commands.keys(), key=lambda c: c.qualified_name), per_page=6)
        self.commands = commands
        self.help_command = help_command
        self.prefix = help_command.clean_prefix

    def format_commands(self, cog, commands):
        # A field can only have 1024 characters so we need to paginate a bit
        # just in case it doesn't fit perfectly
        # However, we have 6 per page so I'll try cutting it off at around 800 instead
        # Since there's a 6000 character limit overall in the embed
        # if cog.description:
        #     short_doc = cog.description.split('\n', 1)[0] + '\n'
        # else:
        #     short_doc = f'> No help found...\n'

        # current_count = len(short_doc)
        ending_note = '+%d not shown'

        page = []
        for command in commands:
            value = f'`{self.prefix}{command.name}` '
            count = len(value) + 1 # The space
            if count < 800:
                page.append(value)
            else:
                break

        if len(page) == len(commands):
            # We're not hiding anything so just return it as-is
            return ' '.join(page)

        hidden = len(commands) - len(page)
        return ' '.join(page) + '\n' + (ending_note % hidden)


    async def format_page(self, menu, cogs):
        prefix = menu.ctx.prefix
        description = f'> Use `{prefix}help command` for more info on a command.\n' \
                    f'> Use `{prefix}help category` for more info on a category.\n' \
                    '> For more help, join the official bot [Support server](https://discord.gg/YSJVbxj9nw)'

        embed = discord.Embed(title='Bot Help Page', description=description, colour=discord.Colour.green())

        for cog in cogs:
            commands = self.commands.get(cog)
            if commands:
                value = self.format_commands(cog, commands)
                embed.add_field(name=cog.qualified_name, value=value, inline=False)

        maximum = self.get_max_pages()
        embed.set_footer(text=f'Page {menu.current_page + 1}/{maximum}')
        return embed

class GroupHelpPageSource(menus.ListPageSource):
    def __init__(self, group, commands, *, prefix):
        super().__init__(entries=commands, per_page=6)
        self.group = group
        self.prefix = prefix
        self.title = f'{self.group.qualified_name} Commands'
        self.description = self.group.description

    async def format_page(self, menu, commands):
        embed = discord.Embed(title=self.title, description=f'{self.description}', colour=discord.Colour.green())

        for command in commands:
            signature = f'`{self.prefix}{command.qualified_name} {command.signature}`'
            embed.add_field(name=signature, value=f'> {command.short_doc}' or f'> No help given...', inline=False)
            

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)')

        embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')
        return embed

class HelpMenu(TeaPages):
    def __init__(self, source):
        super().__init__(source)

    @menus.button(emote.questionmark, position=menus.Last(5))
    async def show_bot_help(self, payload):
        """shows how to use the bot"""

        embed = discord.Embed(title='Using the bot', colour= 0x4ca64c)
        embed.title = 'Using the bot'
        embed.description = '> Hello! Welcome to the tea bot help page.'

        entries = (
            ('<argument>', '> This means the argument is **required**.'),
            ('[argument]', '> This means the argument is **optional**.'),
            ('[A|B]', '> This means that it can be **either A or B**.'),
            ('[argument...]', '> This means you can have multiple arguments.\n' \
                            '> Now that you know the basics, it should be noted that...\n' \
                            '> **You do not type in the brackets!**')
        )

        embed.add_field(name='How do I use this bot?', value='> Reading the bot signature is pretty simple.')

        for name, value in entries:
            embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=f'We were on page {self.current_page + 1} before this message.')
        await self.message.edit(embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_page(self.current_page)

        self.bot.loop.create_task(go_back_to_current_page())

class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'cooldown': commands.Cooldown(1, 3.0, commands.BucketType.member),
            'help': 'Shows help about the bot, a command, or a category'
        })

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True)

        all_commands = {}
        for command in entries:
            if command.cog is None:
                continue
            try:
                all_commands[command.cog].append(command)
            except KeyError:
                all_commands[command.cog] = [command]


        menu = HelpMenu(BotHelpPageSource(self, all_commands))
        # await self.context.release()
        await menu.start(self.context)

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        menu = HelpMenu(GroupHelpPageSource(cog, entries, prefix=self.clean_prefix))
        # await self.context.release()
        await menu.start(self.context)

    def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        embed_like.description = f'{command.description}\n\n> {command.help}' or f'> No help found...'
        
    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour.green())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        if len(entries) == 0:
            return await self.send_command_help(group)

        source = GroupHelpPageSource(group, entries, prefix=self.clean_prefix)
        self.common_command_formatting(source, group)
        menu = HelpMenu(source)
        # await self.context.release()
        await menu.start(self.context)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self.old_help_command



def setup(bot):
    bot.add_cog(Help(bot))
