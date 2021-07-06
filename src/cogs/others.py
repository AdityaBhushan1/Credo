import discord
from discord.ext import commands
import psutil
import platform
from .utils import emote
from .utils import context as Context
import os,inspect
from collections import Counter
from glob import glob



class Other(commands.Cog, name='Other'):
    def __init__(self, bot):
        self.bot = bot

    

    @commands.command()
    async def stats(self, ctx: commands.Context):
        async with ctx.channel.typing():
            pythonVersion = ('3.8.6')
            dpyVersion = discord.__version__
            serverCount = len(self.bot.guilds)
            memberCount = len(set(self.bot.get_all_members()))
            commandscount = (len(set(self.bot.commands)))
            cpu_usage =  psutil.cpu_percent(4)
            ram_usage = psutil.virtual_memory()[2]
            operatingsystem = platform.system()
            latency = round(self.bot.latency*1000)
            e = discord.Embed(title = 'Tea Bot Status', description = f'Bot Name : `Tea Bot#9256`\n`Bot ID: 782875333144870932`',color = self.bot.color,inline=True)
            e.add_field(name = 'General', value = f'```py\nSevers: {serverCount}\nUsers: {memberCount}\n```',inline=True)
            e.add_field(name = 'Other', value = f'```py\nPython Version: {pythonVersion}\nDiscord.Py Version: {dpyVersion}\nTea Bot Version: 3.4\nCommands: {commandscount}\nLatency: {latency}\n```',inline=True)
            e.add_field(name = 'System', value = f'```py\nOs: {operatingsystem}\nCPU Usage: {cpu_usage}%\nRam Usage: {ram_usage}%\n```',inline=True)
            e.add_field(name = 'Creator', value = f'```\nTier Gamer#0252 [749550694469599233]\n```',inline=True)
            e.set_thumbnail(url = self.bot.logo)
            await ctx.send(embed=e)

       # invite command
    @commands.command()
    async def invite(self, ctx):
        em = discord.Embed(title="**Wanna invite <:bot:784780560278224906> to your server? It's really very simple to do so :-**",
                           description="[Invite From Here](https://discord.com/oauth2/authorize?client_id=782867672626364456&permissions=2147483647&scope=bot)", color=discord.Colour.green())
        em.add_field(name='**You can also join our Support Server** <:discordserver:784780505048023080>',
                     value='[Click Here To Join](https://discord.gg/YSJVbxj9nw)')
        em.add_field(name='**Important Links** <:Link:784780662829088818>',
                     value='<:devloper:784780468440662016> [Devloper](https://github.com/aditya-9457) | [Vote](https://top.gg/bot/782867672626364456/vote)')
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def feedback(self, ctx, *, content: str):
        """Gives feedback about the bot.

        This is a quick way to request features or bug fixes
        without being in the bot's server.

        You can only request feedback once a minute.
        """

        e = discord.Embed(title='Feedback', colour=self.bot.color)
        channel = self.bot.get_channel(819571737510281222)
        if channel is None:
            return

        e.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        e.description = content
        e.timestamp = ctx.message.created_at

        if ctx.guild is not None:
            e.add_field(name='Server', value=f'{ctx.guild.name} (ID: {ctx.guild.id})', inline=False)

        e.add_field(name='Channel', value=f'{ctx.channel} (ID: {ctx.channel.id})', inline=False)
        e.set_footer(text=f'Author ID: {ctx.author.id}')

        await channel.send(embed=e)
        await ctx.send(f'{emote.tick} | Successfully sent feedback')

    @commands.command(aliases = ['src'])
    async def source(self, ctx: Context, *, search: str = None):
        """Refer to the source code of the bot commands."""
        source_url = "https://github.com/AQUATRIX-DEVELOPMENT/Tea-Bot"

        if search is None:
            return await ctx.send(source_url)

        command = ctx.bot.get_command(search)

        if not command:
            return await ctx.send("Couldn't find that command.")

        src = command.callback.__code__
        filename = src.co_filename
        lines, firstlineno = inspect.getsourcelines(src)

        location = os.path.relpath(filename).replace("\\", "/")

        final_url = f"<{source_url}/blob/main/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)

    @commands.command()
    async def ping(self, ctx):
        em = discord.Embed(
            description=f"Pong! **{round(self.bot.latency*1000)}** ms", color=discord.Colour.green())
        await ctx.send(embed=em)

    @commands.command(aliases=["cs"])
    async def codestats(self, ctx: Context):
        """See the code statictics of tea bot."""
        ctr = Counter()
        for ctr["files"], f in enumerate(glob("./**/*.py", recursive=True)):
            with open(f, encoding="UTF-8") as fp:
                for ctr["lines"], line in enumerate(fp, ctr["lines"]):
                    line = line.lstrip()
                    ctr["imports"] += line.startswith("import") + line.startswith("from")
                    ctr["classes"] += line.startswith("class")
                    ctr["comments"] += "#" in line
                    ctr["functions"] += line.startswith("def")
                    ctr["coroutines"] += line.startswith("async def")
                    ctr["docstrings"] += line.startswith('"""') + line.startswith("'''")

            embed=discord.Embed(
                title="Tea Bot Code Stats",
                description="\n".join([f"**{k.capitalize()}:** {v}" for k, v in ctr.items()]),
                color = self.bot.color
            )
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Other(bot))
