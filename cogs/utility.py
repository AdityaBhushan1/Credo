import discord
from discord.ext import commands,menus
import random
import asyncio
import datetime
from datetime import datetime, timedelta
import requests
import re
from .utils.util import date
import requests
import mystbin
import time
from .utils import emote
from collections import Counter
from .utils import times
from .utils import formats
from disputils import BotEmbedPaginator
import zipfile
from io import BytesIO
import aiohttp
from .utils.paginitators import TeaPages
from discord.ext.commands.converter import MessageConverter
from.utils.replies import *
import pyfiglet

class WrappedMessageConverter(MessageConverter):
    """A converter that handles embed-suppressed links like <http://example.com>."""

    async def convert(self, ctx: discord.ext.commands.Context, argument: str) -> discord.Message:
        """Wrap the commands.MessageConverter to handle <> delimited message links."""
        # It's possible to wrap a message in [<>] as well, and it's supported because its easy
        if argument.startswith("[") and argument.endswith("]"):
            argument = argument[1:-1]
        if argument.startswith("<") and argument.endswith(">"):
            argument = argument[1:-1]

        return await super().convert(ctx, argument)

def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)

starttime = datetime.utcnow()

colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    # "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
color_list = [c for c in colors.values()]

class UrbanDictionaryPageSource(menus.ListPageSource):
    BRACKETED = re.compile(r'(\[(.+?)\])')
    def __init__(self, data):
        super().__init__(entries=data, per_page=1)

    def cleanup_definition(self, definition, *, regex=BRACKETED):
        def repl(m):
            word = m.group(2)
            return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'

        ret = regex.sub(repl, definition)
        if len(ret) >= 2048:
            return ret[0:2000] + ' [...]'
        return ret

    async def format_page(self, menu, entry):
        maximum = self.get_max_pages()
        title = f'{entry["word"]}: {menu.current_page + 1} out of {maximum}' if maximum else entry['word']
        embed = discord.Embed(title=title, colour=0x4ca64c)
        embed.set_footer(text=f'by {entry["author"]}')
        embed.description = self.cleanup_definition(entry['definition'])

        # try:
        #     up, down = entry['thumbs_up'], entry['thumbs_down']
        # except KeyError:
        #     pass
        # else:
        #     embed.add_field(name='Votes', value=f'\N{THUMBS UP SIGN} {up} \N{THUMBS DOWN SIGN} {down}', inline=False)

        try:
            date = discord.utils.parse_time(entry['written_on'][0:-1])
        except (ValueError, KeyError):
            pass
        else:
            embed.timestamp = date

        return embed
class Utility(commands.Cog, name='Utility'):
    def __init__(self, bot):
        self.bot = bot

    # avatar commands
    @commands.command()
    async def avatar(self, ctx, *, user: discord.Member = None):
        """Gives Avatar Of Memeber"""
        if user is None:
            user = ctx.message.author
        em = discord.Embed(color=random.choice(color_list))
        em.add_field(name=user.name, value=f'[Download]({user.avatar_url})')
        em.set_image(url=user.avatar_url)
        em.set_footer(
            text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    # server icon commands
    @commands.command(aliases=['sicon'])
    async def servericon(self, ctx):
        """Gives Server Icon Of Server"""
        em = discord.Embed(color=random.choice(color_list))
        em.set_image(url=ctx.guild.icon_url)
        em.set_footer(
            text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    # pingcommand
    @commands.command()
    async def ping(self, ctx):
        em = discord.Embed(
            description=f"Pong! **{round(self.bot.latency*1000)}** ms", color=discord.Colour.green())
        await ctx.send(embed=em)

    @commands.command(aliases=['cs'])
    async def channelstats(self, ctx):
        """Gives Stats Of Channel"""
        channel = ctx.channel
        embed = discord.Embed(
            title=f"Stats for **{channel.name}**", description=f"{'Category: {}'.format(channel.category.name) if channel.category else 'This channel is not in a category'}", color=discord.Colour.green())
        embed.add_field(name="Channel Guild",
                        value=ctx.guild.name, inline=False)
        embed.add_field(name="Channel Id", value=channel.id, inline=False)
        embed.add_field(name="Channel Topic",
                        value=f"{channel.topic if channel.topic else 'No topic.'}", inline=False)
        embed.add_field(name="Channel Position",
                        value=channel.position, inline=False)
        embed.add_field(name="Channel Slowmode Delay",
                        value=channel.slowmode_delay, inline=False)
        embed.add_field(name="Channel is nsfw?",
                        value=channel.is_nsfw(), inline=False)
        embed.add_field(name="Channel is news?",
                        value=channel.is_news(), inline=False)
        embed.add_field(name="Channel Creation Time",
                        value=channel.created_at, inline=False)
        embed.add_field(name="Channel Permissions Synced",
                        value=channel.permissions_synced, inline=False)
        embed.add_field(name="Channel Hash", value=hash(channel), inline=False)

        await ctx.send(embed=embed)

     # embed command
    @commands.command(aliases=['em'])
    @commands.has_permissions(manage_guild=True)
    async def embed(self, ctx):
        """Embeds Your Message"""
        await ctx.send("Hello, what do you want the title to be")

        def check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel
        try:
            name = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send( f'{emote.error} | You took long. Goodbye.')
        
        if len(name.content) >= 250:
            return await ctx.send(f'{emote.error} | Title Must Be Less Than 250 Chracters')
        await ctx.send(f'Sweat. So the name is {name.content}. What about the content? ' \
                       f'**You can type {ctx.prefix}abort to abort the embed make process.**')

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=300.0)
        except asyncio.TimeoutError:
            return await ctx.send( f'{emote.error} | You took too long. Goodbye.')
        
        if msg.content == f'{ctx.prefix}abort':
            return await ctx.send('Aborting.')
        elif msg.content:
            clean_content = await commands.clean_content().convert(ctx, msg.content)
        else:
            # fast path I guess?
            clean_content = msg.content

        if len(clean_content) >= 2000:
            return await ctx.send(f'{emote.error} | Description Must Be Less Than 2000 Chracters')

        em = discord.Embed(title=name.content, description=clean_content,color=self.bot.color)
        await ctx.send(embed=em)

    # server info
    @commands.command(aliases=['guildinfo'], usage='')
    @commands.guild_only()
    async def serverinfo(self, ctx, *, guild_id: int = None):
        """Shows info about the current server."""

        if guild_id is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await ctx.send(f'Invalid Guild ID given.')
        else:
            guild = ctx.guild

        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        if not guild.chunked:
            async with ctx.typing():
                await guild.chunk(cache=True)

        # figure out what channels are 'secret'
        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions(
                (everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1

        e = discord.Embed(color=self.bot.color)
        e.title = guild.name
        e.description = f'**ID**: {guild.id}\n**Owner**: {guild.owner}'
        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        channel_info = []
        key_to_emoji = {
            discord.TextChannel: f'{emote.text_channel}',
            discord.VoiceChannel: f'{emote.voice_channel}',
        }
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f'{emoji} {total} ({secrets} locked)')
            else:
                channel_info.append(f'{emoji} {total}')

        info = []
        features = set(guild.features)
        all_features = {
            'PARTNERED': 'Partnered',
            'VERIFIED': 'Verified',
            'DISCOVERABLE': 'Server Discovery',
            'COMMUNITY': 'Community Server',
            'FEATURABLE': 'Featured',
            'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            'INVITE_SPLASH': 'Invite Splash',
            'VIP_REGIONS': 'VIP Voice Servers',
            'VANITY_URL': 'Vanity Invite',
            'COMMERCE': 'Commerce',
            'LURKABLE': 'Lurkable',
            'NEWS': 'News Channels',
            'ANIMATED_ICON': 'Animated Icon',
            'BANNER': 'Banner'
        }

        for feature, label in all_features.items():
            if feature in features:
                info.append(f'{emote.tick}: {label}')

        if info:
            e.add_field(name='Features', value='\n'.join(info))

        e.add_field(name='Channels', value='\n'.join(channel_info))
        e.add_field(name="**Created On:**", value=f" {ctx.guild.created_at}")
        e.add_field(name='**Region:**', value=f" {ctx.guild.region}")
        e.add_field(name="**Verification Level:**",
                    value=f" {ctx.guild.verification_level}")

        if guild.premium_tier != 0:
            boosts = f'Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts'
            last_boost = max(
                guild.members, key=lambda m: m.premium_since or guild.created_at)
            if last_boost.premium_since is not None:
                boosts = f'{boosts}\nLast Boost: {last_boost} ({times.human_timedelta(last_boost.premium_since, accuracy=2)})'
            e.add_field(name='Boosts', value=boosts, inline=False)

        bots = sum(m.bot for m in guild.members)
        fmt = f'Total: {guild.member_count} ({formats.plural(bots):bot})'

        e.add_field(name='Members', value=fmt, inline=False)
        e.add_field(name='Roles', value=', '.join(roles)
                    if len(roles) < 10 else f'{len(roles)} roles')

        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats['animated'] += 1
                emoji_stats['animated_disabled'] += not emoji.available
            else:
                emoji_stats['regular'] += 1
                emoji_stats['disabled'] += not emoji.available

        fmt = f'Regular: {emoji_stats["regular"]}/{guild.emoji_limit}\n' \
              f'Animated: {emoji_stats["animated"]}/{guild.emoji_limit}\n' \

        if emoji_stats['disabled'] or emoji_stats['animated_disabled']:
            fmt = f'{fmt}Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

        fmt = f'{fmt}Total Emoji: {len(guild.emojis)}/{guild.emoji_limit*2}'
        e.add_field(name='Emoji', value=fmt, inline=False)
        e.set_footer(text='Created').timestamp = guild.created_at
        await ctx.send(embed=e)

    # role info
    @commands.command(aliases=['ri'])
    async def roleinfo(self, ctx, role: discord.Role):
        perms = iter(role.permissions)
        tp = []
        fp = []
        for x in perms:
            if "True" in str(x):
                tp.append(str(x).split('\'')[1])
            else:
                fp.append(str(x).split('\'')[1])
        em = discord.Embed(color=discord.Colour.green(),
                           timestamp=ctx.message.created_at, inline=True)
        em.add_field(name=f'__**Role Info**__', value=f'''**Role Name:** \n{role.name}\n
**Role Id:** \n{role.id}\n 
**Role Postion:** \n{role.position}\n 
**Colour:** \n{role.color}\n 
**Created At:** \n{role.created_at}\n 
**Is Mentionable** \n{role.mentionable}\n
**Managed** \n{role.managed}\n
**Permissions:** \n**valid:** {', '.join(tp)}\n 
**Invalid:** {', '.join(fp)}
''')
        em.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

     # Embeds whois asking about member

    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx, member: discord.Member = None):
        """Gives Info Of Member"""
        member = ctx.author if not member else member
        roles = [role for role in member.roles]
        embed = discord.Embed(color=member.color.green(),
                              timestamp=ctx.message.created_at)
        embed.set_author(name=f"UserInfo For {member}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="**Name:**", value=member.name)
        embed.add_field(name="**ID:**", value=member.id)
        embed.add_field(name='**NickName:**', value=member.nick)
        # embed.add_field(name='**Activity:**',value=member.activities)
        embed.add_field(name='**Is Bot?:**', value=member.bot)
        embed.add_field(name='**Is On Mobile?**', value=member.is_on_mobile())
        embed.add_field(name="**Created at:**",
                        value=member.created_at.strftime("%a, %d %B %Y, %H:%M GMT"))
        embed.add_field(name="**Joined at**:",
                        value=member.joined_at.strftime("%a, %d %B %Y, %H:%M GMT"))
        embed.add_field(
            name=f"**Roles:** \n ({len(roles)})", value=" " .join([role.mention for role in roles]))
        embed.add_field(name="Top role:", value=member.top_role.mention)

        await ctx.send(embed=embed)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def emojilist(self, ctx):
        """Gives You Emojis List Of Server"""
        emojis = sorted([e for e in ctx.guild.emojis if len(
            e.roles) == 0 and e.available], key=lambda e: e.name.lower())
        paginator = commands.Paginator(suffix='', prefix='')
        channel = ctx.channel

        for emoji in emojis:
            paginator.add_line(f'{emoji} -- `{emoji}`')

        for page in paginator.pages:
            await channel.send(page)

    @commands.command()
    async def gen_pass(self, ctx):
        """Generates A Password For You"""
        url = "https://www.passwordrandom.com/query?command=password&format=json&count=1"
        json_data = requests.get(url).json()
        password = json_data['char'][0]
        try:
            await ctx.send('Your Passwor Has Been Sent Your DM')
            await ctx.author.send(password)
        except:
            await ctx.send('Your Dm Is Closed Cannot Send Here')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def todo(self, ctx, *, args):
        channel = self.bot.get_channel(800772432608100352)
        em = discord.Embed(
            title='TO-DO', description=f'{args}', color=discord.Colour.green())
        await channel.send(embed=em)
        # await ctx.message.delete()
        await ctx.send(':thumbsup:')

    @commands.command(aliases=['hex_info'])
    async def color_info(self, ctx, hexvalue: str):
        """Give You Info About Hex Color Code"""
        if hexvalue[:1] == "#":
            hexvalue = hexvalue[1:]

        if not re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', hexvalue):
            return await ctx.send("You're only allowed to enter HEX (0-9 & A-F)")

        url = f"https://api.alexflipnote.dev/colour/{hexvalue}"

        headers = {
            "Authorization": self.bot.api_alexflipnote
        }

        r = requests.request("GET", url, headers=headers).json()
        int = r['int']
        image = r['image']
        image_gradient = r['image_gradient']
        hex = r['hex']
        rgb = r['rgb']
        brightness = r['brightness']
        name = r['name']

        embed = discord.Embed(title=f'Hex Value Info For:',
                              description=f'`{name}`', colour=int)
        embed.set_thumbnail(url=image)
        embed.set_image(url=image_gradient)

        embed.add_field(name="HEX", value=hex, inline=True)
        embed.add_field(name="RGB", value=rgb, inline=True)
        embed.add_field(name="Int", value=int, inline=True)
        embed.add_field(name="Brightness", value=brightness, inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def mods(self, ctx):
        """ Gives You A list Mods"""
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"

        await ctx.send(f"Mods in **{ctx.guild.name}**\n{message}")

    @commands.command()
    @commands.guild_only()
    async def joinedate(self, ctx, *, user: discord.Member = None):
        """ Check when a user joined the current server """
        user = user or ctx.author

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar_url)
        embed.description = f'**{user}** joined **{ctx.guild.name}**\n{date(user.joined_at)}'
        await ctx.send(embed=embed)

    @commands.command()
    async def country_info(self, ctx, country):
        """Gives You Info About Country"""
        try:
            url = f"https://restcountries.eu/rest/v2/name/"+country+"?fullText=true"
            json_data = requests.get(url).json()
            name = json_data[0]['name']
            capital = json_data[0]['capital']
            region = json_data[0]['region']
            subregion = json_data[0]['subregion']
            population = json_data[0]['population']
            timezone = json_data[0]['timezones'][0]
            currency = json_data[0]['currencies'][0]['name']
            currency_symbol = json_data[0]['currencies'][0]['symbol']
            flag = json_data[0]['flag']
            languages = json_data[0]['languages'][0]['name']

            em = discord.Embed(title=f'Country Name : ',
                               description=f'`{name}`', color=ctx.author.color)
            em.add_field(name='Capital', value=f'`{capital}`')
            em.add_field(name='Region', value=f'`{region}`')
            em.add_field(name='Subregion', value=f'`{subregion}`')
            em.add_field(name='Population', value=f'`{population}`')
            em.add_field(name='Time Zone', value=f'`{timezone}`')
            em.add_field(name='Currency', value=f'`{currency}`')
            em.add_field(name='Currency Symabol', value=f'`{currency_symbol}`')
            em.add_field(name='National Language', value=f'`{languages}`')
            em.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            em.set_thumbnail(url=flag)
            await ctx.send(embed=em)
        except:
            await ctx.send('could not find it sorry')

    @commands.command(aliases=['weain'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather(self, ctx, *, city):
        """Gives You Weather Condition Of City"""
        try:
            city = city
            api = "http://api.openweathermap.org/data/2.5/weather?q=" + \
                city + "&appid=" + self.bot.weather_api_key
            json_data = requests.get(api).json()
            weather = json_data['weather'][0]['main']
            temp = int(json_data['main']['temp'] - 273.15)
            min_temp = int(json_data['main']['temp_min'] - 273.15)
            max_temp = int(json_data['main']['temp_max'] - 273.15)
            pressure = json_data['main']['pressure']
            humidity = json_data['main']['humidity']
            wind_speed = json_data['wind']['speed']
            sunrise_time = time.strftime("%I:%M:%S", time.gmtime(
                json_data['sys']['sunrise'] - 21600))
            sunset_time = time.strftime("%I:%M:%S", time.gmtime(
                json_data['sys']['sunset'] - 21600))

            em = discord.Embed(
                title=f'**City : {city}**', color=ctx.author.color, timestamp=ctx.message.created_at)
            em.add_field(name='**Weather: **', value=f'{weather}')
            em.add_field(name='**Temprature: **', value=f'`{temp}`')
            em.add_field(name='**Maximum Temprature: **',
                         value=f'`{min_temp}`')
            em.add_field(name='**Minimum Temprature: **',
                         value=f'`{max_temp}`')
            em.add_field(name='**Pressure: **', value=f'`{pressure}`')
            em.add_field(name='**Humidity: **', value=f'`{humidity}`')
            em.add_field(name='**Wind Speed: **', value=f'`{wind_speed}`')
            em.add_field(name='**Sunrises Time: **', value=f'`{sunrise_time}`')
            em.add_field(name='**Sunset Time: **', value=f'`{sunset_time}`')
            em.set_author(name='Weather Info')
            em.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)
        except:
            await ctx.send('Cannot Find The City You Are Looking For')

    @commands.command()
    async def lyrics(self, ctx, *, songname):
        """Give You Lyrics Of Song"""
        try:
            titel = songname
            api = 'https://some-random-api.ml/lyrics?title='+titel
            json_data = requests.get(api).json()
            song_titel = json_data['title']
            lyrics = json_data['lyrics']
            author = json_data['author']
            if len(lyrics) > 1024:
                mystbin_client = mystbin.Client()
                paste = await mystbin_client.post(lyrics)
                em = discord.Embed(
                    description=f'The Lyrics Is More Than discord Character limt So I HAve Posted It On BIN \n [Click Me To See]({str(paste)})')
                await ctx.send(embed=em)
            else:
                em = discord.Embed(
                    title='Lyrics For : ', description=f'{song_titel}', color=ctx.author.color)
                em.add_field(name='Author : ', value=f'{author}')
                em.add_field(name='Lyrics : ', value=f'{lyrics}', inline=False)
                em.set_footer(
                    text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=em)
        except:
            await ctx.send('cannot find anything')

    @commands.command()
    async def movie_info(self, ctx, *, mvoiename):
        """Gives You Info About Movie"""
        try:
            url = f'http://www.omdbapi.com/?apikey={self.bot.omdbapi_key}&t={mvoiename}'
            data = requests.get(url).json()
            title = data['Title']
            rated = data['Rated']
            Released_date = data['Released']
            Runtime = data['Runtime']
            Genre = data['Genre']
            Director = data['Director']
            Writer = data['Writer']
            Actors = data['Actors']
            imdbRating = data['imdbRating']
            imdbVotes = data['imdbVotes']
            BoxOffice = data['BoxOffice']
            Production = data['Production']
            # poster = data['Poster']
            em = discord.Embed(title='Movie Name',
                               description=f'{title}', color=ctx.author.color)
            em.add_field(name='Director', value=f'{Director}')
            em.add_field(name='Writers', value=f'{Writer}')
            em.add_field(name='Actors', value=f'{Actors}')
            em.add_field(name='Production', value=f'{Production}')
            em.add_field(name='Genre', value=f'{Genre}')
            em.add_field(name='Released Date', value=f'{Released_date}')
            em.add_field(name='Rated', value=f'{rated}')
            em.add_field(name='Runtime', value=f'{Runtime}')
            em.add_field(name='IMDB Rating', value=f'{imdbRating}')
            em.add_field(name='IMDB Votes', value=f'{imdbVotes}')
            em.add_field(name='Box Office', value=f'{BoxOffice}')
            em.set_footer(
                text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            # em.set_thumbnail
            await ctx.send(embed=em)
        except:
            await ctx.send("Couldn't Find Anything")

    @commands.command()
    async def enlarge(self, ctx, Emoji: discord.Emoji):
        """
        Enlarges a Custom Emoji or Animated Emoji
        """
        embed = discord.Embed(
            title=f"{Emoji} has been enlarged", color=self.bot.color)
        embed.set_image(url=Emoji.url)
        embed.set_author(name=f"{ctx.author.name}",
                         icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['ei'])
    async def emoji_info(self, ctx, emoji: discord.Emoji):
        """
        Gives You Info About A Emoji
        """
        try:
            emoji = await emoji.guild.fetch_emoji(emoji.id)
        except discord.NotFound:
            await ctx.send('Could not find the emoji you are looking for')

        is_managed = 'Yes' if emoji.managed else 'No'
        is_animated = 'Yes' if emoji.animated else 'No'
        requires_colons = 'Yes' if emoji.require_colons else 'No'
        creation_time = emoji.created_at.strftime('%I:%M %p %B %d, %Y')
        can_use_emoji = 'Everyone' if not emoji.roles else " ".join(
            role.name for role in emoji.roles)

        description = f"""
        **General:**
        **- Name:** {emoji.name}
        **- Id:** {emoji.id}
        **- URL:** [Link To Emoji]({emoji.url})
        **- Author:** {emoji.user}
        **- Time Created:** {creation_time}
        **- Usable By:** {can_use_emoji}

        **Others:**
        **- Animated:** {is_animated}
        **- Managed:** {is_managed}
        **- Requires Colons:** {requires_colons}
        **- Guild Name:** {emoji.guild.name}
        **- Guild Id:** {emoji.guild.id}

        """
        embed = discord.Embed(title=f"**Emoji Information For:** `{emoji.name}`",
                              description=description,
                              colour=self.bot.color
                              )
        embed.set_thumbnail(url=emoji.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def encode_msg(self, ctx, *, message):
        """Encodes You Message"""
        try:
            api = 'https://some-random-api.ml/base64?encode='+message
            json_data = requests.get(api).json()
            encoded_msg = json_data['base64']
            if len(encoded_msg) > 1024:
                mystbin_client = mystbin.Client()
                paste = await mystbin_client.post(encoded_msg)
                em = discord.Embed(
                    description=f'The Encoded Msg Is More Than discord Character limt So I HAve Posted It On BIN \n [Click Me To See]({str(paste)})')
                await ctx.send(embed=em)
            else:
                await ctx.send(f'Your Encoded Message For {message} Is : `{encoded_msg}`')
        except:
            await ctx.send('Cannot Incode Your Message')

    @commands.command()
    async def decode_msg(self, ctx, *, encodedmsg):
        """Decode You Encoded Message"""
        try:
            api = 'https://some-random-api.ml/base64?decode='+encodedmsg
            json_data = requests.get(api).json()
            decoded_msg = json_data['text']
            if len(decoded_msg) > 1024:
                mystbin_client = mystbin.Client()
                paste = await mystbin_client.post(decoded_msg)
                em = discord.Embed(
                    description=f'The Decoded Msg Is More Than discord Character limt So I HAve Posted It On BIN \n [Click Me To See]({str(paste)})')
                await ctx.send(embed=em)
            else:
                await ctx.send(f'Your Decoded Message For {encodedmsg} Is : {decoded_msg}')
        except:
            await ctx.send('Cannot Decode Your Message')


    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def dog_fact(self,ctx):
        """Give You Random Fact Of Dog"""
        api = 'https://some-random-api.ml/facts/dog'
        json_data = requests.get(api).json()
        fact = json_data['fact']
        em = discord.Embed(title='Random Dog Fact',description=f'{fact}',color=ctx.author.color)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cat_fact(self,ctx):
        """Give You Random Fact Of Cat"""
        api = 'https://some-random-api.ml/facts/cat'
        json_data = requests.get(api).json()
        fact = json_data['fact']
        em = discord.Embed(title='Random Cat Fact',description=f'{fact}',color=ctx.author.color)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def panda_fact(self,ctx):
        """Give You Random Fact Of Panda"""
        api = 'https://some-random-api.ml/facts/panda'
        json_data = requests.get(api).json()
        fact = json_data['fact']
        em = discord.Embed(title='Random Panda Fact',description=f'{fact}',color=ctx.author.color)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fox_fact(self,ctx):
        """Give You Random Fact Of Fox"""
        api = 'https://some-random-api.ml/facts/fox'
        json_data = requests.get(api).json()
        fact = json_data['fact']
        em = discord.Embed(title='Random Fox Fact',description=f'{fact}',color=ctx.author.color)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bird_fact(self,ctx):
        """Give You Random Fact Of Bird"""
        api = 'https://some-random-api.ml/facts/bird'
        json_data = requests.get(api).json()
        fact = json_data['fact']
        em = discord.Embed(title='Random Bird Fact',description=f'{fact}',color=ctx.author.color)
        await ctx.send(embed=em)
        
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def kola_fact(self,ctx):
        """Give You Random Fact Of Kola"""
        api = 'https://some-random-api.ml/facts/koala'
        json_data = requests.get(api).json()
        fact = json_data['fact']
        em = discord.Embed(title='Random Kola Fact',description=f'{fact}',color=ctx.author.color)
        await ctx.send(embed=em)

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)

        avatar = member.avatar_url_as(static_format='png')
        # e.set_author(name=str(member), url=avatar)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace('_', ' ').replace('guild', 'server').title()
            if value:
                allowed.append(f'`{name}`')
            else:
                denied.append(f'`{name}`')
        embeds = [
            discord.Embed(title=f'{str(member)} **Allowed** Permissions',
                          description='\n'.join(allowed), color=self.bot.color),
            discord.Embed(title=f'{str(member)} **Denied** Permissions',
                          description='\n'.join(denied), color=self.bot.color)
        ]
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command()
    @commands.guild_only()
    async def permissions(self, ctx, member: discord.Member = None, channel: discord.TextChannel = None):
        """Shows a member's permissions in a specific channel.

        If no channel is given then it uses the current one.

        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = channel or ctx.channel
        if member is None:
            member = ctx.author

        await self.say_permissions(ctx, member, channel)

    @commands.command()
    @commands.guild_only()
    async def botpermissions(self, ctx, *, channel: discord.TextChannel = None):
        """Shows the bot's permissions in a specific channel.

        If no channel is given then it uses the current one.

        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.

        To execute this command you must have Manage Roles permission.
        You cannot use this in private messages.
        """
        channel = channel or ctx.channel
        member = ctx.guild.me
        await self.say_permissions(ctx, member, channel)

    @commands.command()
    async def genderize(self, ctx, name: str):
        """Detremines Your Gender Through Name"""
        api = f'https://api.genderize.io/?name={name}'
        data = requests.get(api).json()
        names = data['name']
        gender = data['gender']
        probability = data['probability']

        em = discord.Embed(title='Gender Determiner Through Name',
                           color=ctx.author.color, inline=True)
        em.add_field(name='Name: ', value=names, inline=True)
        em.add_field(name='Gender: ', value=gender, inline=True)
        em.add_field(name='Probability: ', value=probability, inline=True)
        em.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)    

    @commands.command()
    @commands.guild_only()
    async def zipemoji(self, ctx: commands.Context):
        """Returns a zip file with all guild emojis"""
        guild = ctx.guild
        if not guild.emojis:
            return await ctx.send('This guild doesn\'t Have any emojis')

        async with ctx.typing():
            count = [0, 0]
            emojis = [] 
            for emoji in guild.emojis:
                count[emoji.animated] += 1
                ext = 'gif' if emoji.animated else 'png'
                data = await emoji.url.read()
                emojis.append((f'{emoji.name}.{ext}', data))

            limit = guild.emoji_limit
            msg = f'Static: {count[0]}/{limit} Animated: {count[1]}/{limit}'

            buf = BytesIO()
            with zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                for emoji in emojis:
                    zf.writestr(*emoji)

            buf.seek(0)
            file = discord.File(buf, f'emojis_{guild}.zip')

            await ctx.send(msg, file=file)

    async def fetch_weather_data(self, city: str) -> dict:
        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'APPID': self.bot.weather_api_key,
            'q': city,
            'units': 'metric'
        }
        self.bot.session = aiohttp.ClientSession()
        async with self.bot.session.get(url, params=params) as resp:
            js = await resp.json()
            if resp.status == 200:
                return js
            elif resp.status == 404:
                raise RuntimeError('Could not find that city')
            else:
                fmt = 'Failed to fetch weather data for city %r: %s (status code: %d %s)'
                

    @commands.command()
    async def time(self, ctx: commands.Context, *, city: str):
        """Show the date and time of a city"""
        try:
            data = await self.fetch_weather_data(city)
        except RuntimeError as exc:
            return await ctx.send(exc)

        now = datetime.utcnow()

        offset = data['timezone']
        sunrise = data['sys']['sunrise']
        sunset = data['sys']['sunset']

        emoji = '🌜' if sunrise <= now.timestamp() < sunset else '🌞'
        timestamp = now + timedelta(seconds=offset)
        hours, minutes = divmod(offset / 60, 60)

        await ctx.send(f'{emoji} **{timestamp:%d/%m/%Y %H:%M:%S}** (UTC {hours:+03.0f}:{minutes:02.0f})')
    
    @commands.command(aliases=['newmembers'])
    @commands.guild_only()
    async def newusers(self, ctx, *, count=5):
        """Tells you the newest members of the server.

        This is useful to check if any suspicious members have
        joined.

        The count parameter can only be up to 25.
        """
        count = max(min(count, 25), 5)

        if not ctx.guild.chunked:
            await self.bot.request_offline_members(ctx.guild)

        members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[:count]

        e = discord.Embed(title='🆕 New Members', colour=discord.Colour.green())

        for member in members:
            body = f'▫️ Joined {times.human_timedelta(member.joined_at)}\n▫️ Created {times.human_timedelta(member.created_at)}'
            e.add_field(name=f'{member} (ID: {member.id})', value=body, inline=False)
        e.set_footer(
            text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, *, question):
        """Interactively creates a poll with the following question.

        To vote, use reactions!
        """

        # a list of messages to delete when we're all done
        messages = [ctx.message]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100

        for i in range(20):
            messages.append(await ctx.send(f'Say poll option or {ctx.prefix}cancel to publish poll.'))

            try:
                entry = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f'{ctx.prefix}cancel'):
                break

            answers.append((to_emoji(i), entry.clean_content))

        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass # oh well

        answer = '\n'.join(f'{keycap}: {content}' for keycap, content in answers)
        e = discord.Embed(title = f'{ctx.author} asks: {question}',description=f'{answer}',color=self.bot.color)
        embed = await ctx.send(embed=e)
        for emoji, _ in answers:
            await embed.add_reaction(emoji)

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'{emote.xmark} | Missing the question.')

    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx, *questions_and_choices: str):
        """Makes a poll quickly.

        The first argument is the question and the rest are the choices.
        """

        if len(questions_and_choices) < 3:
            return await ctx.send(f'{emote.xmark} | Need at least 1 question with 2 choices.')
        elif len(questions_and_choices) > 21:
            return await ctx.send(f'{emote.xmark} | You can only have up to 20 choices.')

        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send(f'{emote.xmark} | Need Read Message History and Add Reactions permissions.')

        question = questions_and_choices[0]
        choices = [(to_emoji(e), v) for e, v in enumerate(questions_and_choices[1:])]

        try:
            await ctx.message.delete()
        except:
            pass

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        e = discord.Embed(title = f'{ctx.author} asks: {question}',description = f'{body}',color=self.bot.color)
        poll = await ctx.send(embed=e)
        for emoji, _ in choices:
            await poll.add_reaction(emoji)

    @commands.command(name='urban')
    async def _urban(self, ctx, *, word):
        """Searches urban dictionary."""

        url = 'http://api.urbandictionary.com/v0/define'
        ctx.session = aiohttp.ClientSession()
        async with ctx.session.get(url, params={'term': word}) as resp:
            if resp.status != 200:
                return await ctx.send(f'{emote.error} | An error occurred: {resp.status} {resp.reason}')

            js = await resp.json()
            data = js.get('list', [])
            if not data:
                return await ctx.send(f'{emote.xmark} | No results found for: `{word}`')

        pages = TeaPages(UrbanDictionaryPageSource(data))
        try:
            await pages.start(ctx)
        except menus.MenuError as e:
            await ctx.send(e)

    @commands.command(name="bookmark", aliases=("bm", "pin"))
    async def bookmark(self,ctx: commands.Context,target_message: WrappedMessageConverter,*,title: str = "Bookmark") -> None:
        """Send the author a link to `target_message` via DMs."""
        # Prevent users from bookmarking a message in a channel they don't have access to
        permissions = ctx.author.permissions_in(target_message.channel)
        if not permissions.read_messages:
            embed = discord.Embed(
                title=random.choice(ERROR_REPLIES),
                color=discord.Color.red(),
                description="You don't have permission to view this channel."
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=title,
            colour=self.bot.color,
            description=target_message.content
        )
        embed.add_field(name="Wanna give it a visit?", value=f"[Visit original message]({target_message.jump_url})")
        embed.set_author(name=target_message.author, icon_url=target_message.author.avatar_url)
        embed.set_thumbnail(url='https://images-ext-2.discordapp.net/external/zl4oDwcmxUILY7sD9ZWE2fU5R7n6QcxEmPYSE5eddbg/%3Fv%3D1/https/cdn.discordapp.com/emojis/654080405988966419.png?width=20&height=20')

        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
                await ctx.send(f"{ctx.author.mention}, please enable your DMs to receive the bookmark")
        else:
            await ctx.message.add_reaction('📨')

    @commands.command()
    async def ascii(self,ctx, *, text):
        if len(text) >= 16:
            await ctx.send(f'{emote.error} | You Cannot Use More thank 16 Characteres')
        result = pyfiglet.figlet_format(text)

        embed = discord.Embed(description=f"```{result}```",color= self.bot.color)
        await ctx.send(embed=embed)
def setup(bot):
    bot.add_cog(Utility(bot))
