import discord
from discord.ext import commands
import asyncio
import random
import sys
import traceback
import jishaku
import asyncpg
from cogs.utils import context
import config


intents = discord.Intents.default()
intents.members = True

class TeaBot(commands.Bot):
    def __init__(self, **kwargs):
        kwargs["command_prefix"] = config.prefix
        super().__init__(**kwargs)
        self.OWNER = config.owner
        self.color = config.color
        self.guild = config.guild
        self.logo = config.logo
        self.client_id = config.client_id
        self.omdbapi_key = config.omdbapi_key
        self.weather_api_key = config.weather_api_key
        self.api_alexflipnote = config.api_alexflipnote
        self.top_gg = config.top_gg
        self.ksoft_api_key = config.ksoft_api_key
        self.tenor_apikey = config.tenor_apikey
        self.config = config

    async def process_commands(self, message):
        ctx = await self.get_context(message,cls=context.Context)

        await self.invoke(ctx)

bot = TeaBot(case_insensitive=True, intents=intents)

async def ch_pr():
    await bot.wait_until_ready()

    statuses = [f'on {len(bot.guilds)}', 'With *help | *setup']

    while not bot.is_closed():

        status = random.choice(statuses)
        await bot.change_presence(activity=discord.Game(name=status))

        await asyncio.sleep(10)
bot.loop.create_task(ch_pr())

# cogs
extensions = [
    'cogs.mod.mod',
    'cogs.fun',
    'cogs.utility',
    'cogs.events.error',
    'cogs.events.events',
    'cogs.others',
    'cogs.top',
    'cogs.help',
    'cogs.admin',
    'cogs.image',
    'cogs.nsfw',
    'cogs.bot_settings',
    'cogs.tasks',
    'cogs.smanager.smanager',
    'cogs.tags',
    'cogs.events.autoevents',
    'cogs.events.botevents'
]

if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Error Loading {extension}', file=sys.stderr)
            traceback.print_exc()

bot.load_extension("jishaku")

@bot.command(hidden=True)
@commands.is_owner()
async def licog(ctx):
    await ctx.send(extensions)

async def create_db_pool():
    bot.db = await asyncpg.create_pool(database=config.postgresqldb, 
    user=config.postgresqlusername, 
    password=config.postgresqlpass,
    host=config.postgresqlhost)
    print('-------------------------------------')
    print('Conected With Databse')
bot.loop.create_task(create_db_pool())


bot.run(config.token)
