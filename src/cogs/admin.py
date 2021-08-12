# todo complete premium commands

import discord
from discord.ext import commands
from .utils.util import traceback_maker,clean_code
from .utils.emote import tick, error
import traceback
import io
from .utils.paginitators import Pag, TextPageSource,TeaPages
import contextlib
import textwrap
from .utils.formats import TabularData, plural
import time
from typing import Union, Optional
import copy
import asyncio
import subprocess
from .utils import menus
from .utils.util import GlobalChannel


class Owner_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
    
    async def run_process(self, command):
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, name: str):
        """Load any extension"""
        try:
            self.bot.load_extension(f"cogs.{name}")
            await ctx.send(f"{tick} | Loaded extension **{name}**")
        except Exception as e:
            return await ctx.send(traceback_maker(e))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, name: str):
        """Unload any extension"""
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(traceback_maker(e))
        await ctx.send(f"{tick} | Unloaded extension **{name}**")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, name: str):
        """Reload any loaded extension."""
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(traceback_maker(e))
        await ctx.send(f"{tick} | Reloaded extension **{name}**")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        await ctx.send(f"Shutting down the system ...")
        await self.bot.close()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def toogle(self, ctx, *, command):
        try:
            command = self.bot.get_command(command)

            if command is None:
                await ctx.send('I Cant Find The Command')
            elif ctx.command == command:
                await ctx.send('This Command Cannot Be Disabled')
            else:
                command.enabled = not command.enabled
                ternary = 'enabled' if command.enabled else "disabled"
                await ctx.send(f'The Command {command.qualified_name} Has Been  {ternary}')
        except Exception as e:
            return await ctx.send(traceback_maker(e))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sql(self, ctx, *, query: str):
        """Run some SQL."""
        

        query = self.cleanup_code(query)

        is_multistatement = query.count(';') > 1
        if is_multistatement:
            # fetch does not support multiple statements
            strategy = self.bot.db.execute
        else:
            strategy = self.bot.db.fetch

        try:
            start = time.perf_counter()
            results = await strategy(query)
            dt = (time.perf_counter() - start) * 1000.0
        except Exception:
            return await ctx.send(f'```py\n{traceback.format_exc()}\n```')

        rows = len(results)
        if is_multistatement or rows == 0:
            return await ctx.send(f'`{dt:.2f}ms: {results}`')

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()
        
        fmt = f'```sql\n{render}\n```\n*Returned {plural(rows):row} in {dt:.2f}ms*'
        if len(fmt) > 2000:
            fp = io.BytesIO(fmt.encode('utf-8'))
            await ctx.send('Too many results...', file=discord.File(fp, 'results.txt'))
        else:
            await ctx.send(fmt)

    @commands.command(name="eval", aliases=["exec"],hidden=True)
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        code = clean_code(code)

        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n-- {obj}\n"
        except Exception as e:
            result = "".join(traceback.format_exception(e, e, e.__traceback__))

        pager = Pag(
            timeout=100,
            entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```py\n",
            suffix="```",
            color=self.bot.color
        )

        await pager.start(ctx)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sql_table(self, ctx, *, table_name: str):
        """Runs a query describing the table schema."""
        from .utils.formats import TabularData

        query = """SELECT column_name, data_type, column_default, is_nullable
                   FROM INFORMATION_SCHEMA.COLUMNS
                   WHERE table_name = $1
                """

        results = await self.bot.db.fetch(query, table_name)

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()

        fmt = f'```sql\n{render}\n```'
        if len(fmt) > 2000:
            fp = io.BytesIO(fmt.encode('utf-8'))
            await ctx.send('Too many results...', file=discord.File(fp, 'results.txt'))
        else:
            await ctx.send(fmt)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sudo(self, ctx, channel: Optional[GlobalChannel], who: Union[discord.Member, discord.User], *, command: str):
        """Run a command as another user optionally in another channel."""
        msg = copy.copy(ctx.message)
        channel = channel or ctx.channel
        msg.channel = channel
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        new_ctx._db = self.bot.db
        await self.bot.invoke(new_ctx)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def do(self, ctx, times: int, *, command):
        """Repeats a command a specified number of times."""
        msg = copy.copy(ctx.message)
        msg.content = ctx.prefix + command

        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        new_ctx._db = self.bot.db

        for i in range(times):
            await new_ctx.reinvoke()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sh(self, ctx, *, command):
        """Runs a shell command."""
        async with ctx.typing():
            stdout, stderr = await self.run_process(command)

        if stderr:
            text = f'stdout:\n{stdout}\nstderr:\n{stderr}'
        else:
            text = stdout

        pages = TeaPages(TextPageSource(text))
        try:
            await pages.start(ctx)
        except menus.MenuError as e:
            await ctx.send(str(e))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def pm(self, ctx, user_id: int, *, content: str):
        user = self.bot.get_user(user_id) or (await self.bot.fetch_user(user_id))

        fmt = content + '\n\n**__This is a DM sent because you had previously requested feedback or I found a bug' \
                        ' in a command you used, I do not monitor this DM.__**'
        try:
            await user.send(fmt)
            await ctx.send(f'{tick} | PM successfully sent.')
        except:
            await ctx.send(f'{error} | Could not PM user by ID {user_id}.')
        
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def brodcast(self,ctx,*,args):
        """
        Brodcasts This Message To Guild Having Credo Setup
        """
        channel_id = []
        record = await self.bot.db.fetch('SELECT channel_id FROM public.brodcast')   
        for res in record:
            res = res['channel_id']
            channel_id.append(res)
        to_send = []
        success = 0
        for channels in channel_id:
            channel = self.bot.get_channel(channels)
            to_send.append(channel)
            start = time.time()
            em = discord.Embed(title = '📢 | Credo Announcement | 📢',description=args,color=self.bot.color)
            em.set_author(name="TierGamerpy#0252",icon_url=ctx.author.avatar_url)
            try:
                await channel.send(embed = em)
                success += 1
            except:
                continue
        delta = time.time() - start
        await ctx.send(f'Successfully sent to {success} channels (out of {len(to_send)}) in {delta:.2f}s.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def todo(self, ctx, *, args):
        channel = self.bot.get_channel(800772432608100352)
        em = discord.Embed(
            title='TO-DO', description=f'{args}', color=discord.Colour.green())
        await channel.send(embed=em)
        # await ctx.message.delete()
        await ctx.send(':thumbsup:')

def setup(bot):
    bot.add_cog(Owner_Commands(bot))