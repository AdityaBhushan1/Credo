import discord,sys,traceback,asyncpg,jishaku,asyncio
from discord.ext import commands
from cogs.utils import context
import config


intents = discord.Intents.default()
intents.members = True

class TeaBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            strip_after_prefix=True,
            case_insensitive=True,
            chunk_guilds_at_startup=False,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, replied_user=True, users=True),
            activity=discord.Activity(type=discord.ActivityType.listening, name="*setup | *help"),
            fetch_offline_members=True,
            **kwargs,
        )
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
        self.loop = asyncio.get_event_loop()

    async def process_commands(self, message):
        ctx = await self.get_context(message,cls=context.Context)

        await self.invoke(ctx)

bot = TeaBot()

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
    'cogs.bot_settings',
    'cogs.tasks',
    'cogs.smanager.smanager',
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
