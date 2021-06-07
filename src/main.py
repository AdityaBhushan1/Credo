import discord,sys,traceback,asyncpg,jishaku,asyncio
from discord.ext import commands
from cogs.utils import context
import config
from cogs.utils.jsonreaders import Config


intents = discord.Intents.default()
intents.members = True

def get_prefix(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append(config.prefix)
    else:
        base.extend(bot.prefixes.get(msg.guild.id,[config.prefix]))
    return base
class TeaBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=get_prefix,
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
        self.defaultprefix = config.prefix
        self.loop = asyncio.get_event_loop()
        self.prefixes = Config('prefixes.json')

    async def process_commands(self, message):
        ctx = await self.get_context(message,cls=context.Context)

        await self.invoke(ctx)

    def get_guild_prefixes(self, guild, *, local_inject=get_prefix):
        proxy_msg = discord.Object(id=0)
        proxy_msg.guild = guild
        return local_inject(self, proxy_msg)

    def get_raw_guild_prefixes(self, guild_id):
        return self.prefixes.get(guild_id, [config.prefix])

    async def set_guild_prefixes(self, guild, prefixes):
        if len(prefixes) == 0:
            await self.prefixes.put(guild.id, [])
        elif len(prefixes) > 10:
            raise RuntimeError('Cannot have more than 10 custom prefixes.')
        else:
            await self.prefixes.put(guild.id, sorted(set(prefixes), reverse=True))

bot = TeaBot()

# cogs
extensions = [
    'cogs.mod.mod',
    'cogs.fun',
    'cogs.utility',
    'cogs.events.error',
    'cogs.events.events',
    'cogs.others',
    # 'cogs.top',
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
