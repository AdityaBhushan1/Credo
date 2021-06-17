from discord.ext import commands
from .utils import emote
import discord
from .utils import expectations

class Prefix(commands.Converter):
    async def convert(self, ctx, argument):
        user_id = ctx.bot.user.id
        if argument.startswith((f'<@{user_id}>', f'<@!{user_id}>')):
            raise commands.BadArgument('That is a reserved prefix already in use.')
        return argument
class BotSettings(commands.Cog):
    """Handles the bot's configuration system.

    This is how you disable or enable certain commands
    for your server or block certain channels or members.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def config(self, ctx):
        """Handles configuration for the bot."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

##########################################################################################################
###========================================== Prefix Handling Commands ==================================#
##########################################################################################################

    @commands.group(name='prefix', invoke_without_command=True)
    async def prefix(self, ctx):
        """Manages the server's custom prefixes.
        If called without a subcommand, this will list the currently set
        prefixes.
        """
        prefixes = self.bot.get_guild_prefixes(ctx.guild)
        del prefixes[1]
        e = discord.Embed(title='Prefixes', colour=self.bot.color)
        e.set_footer(text=f'{len(prefixes)} prefixes')
        e.description = '\n'.join(f'{index}. {elem}' for index, elem in enumerate(prefixes, 1))
        await ctx.send(embed=e)

    @prefix.command(name='add', ignore_extra=False)
    @commands.has_permissions(manage_guild=True)
    async def prefix_add(self, ctx, prefix: Prefix):
        """Adds A New Prefix To The Server Prefixes.You Can Have Upto 10 Prefixes Per Guild
        """

        current_prefixes = self.bot.get_raw_guild_prefixes(ctx.guild.id)
        current_prefixes.append(prefix)
        try:
            await self.bot.set_guild_prefixes(ctx.guild, current_prefixes)
        except Exception as e:
            await ctx.send(f'{emote.error} {e}')
        else:
            await ctx.send(emote.tick)

    @prefix_add.error
    async def prefix_add_error(self, ctx, error):
        if isinstance(error, commands.TooManyArguments):
            await ctx.send("You've given too many prefixes. Either quote it or only do it one by one.")

    @prefix.command(name='remove', aliases=['delete'], ignore_extra=False)
    @commands.has_permissions(manage_guild=True)
    async def prefix_remove(self, ctx, prefix: Prefix):
        """Removes A Custom Prefix From Your Guild
        """

        current_prefixes = self.bot.get_raw_guild_prefixes(ctx.guild.id)

        if prefix == self.bot.defaultprefix:
            return await ctx.error(f'thats a reserved prefix')
        try:
            current_prefixes.remove(prefix)
        except ValueError:
            return await ctx.send(f'This Server do not have this prefix {prefix} registered.')

        try:
            await self.bot.set_guild_prefixes(ctx.guild, current_prefixes)
        except Exception as e:
            await ctx.send(f'{emote.error} {e}')
        else:
            await ctx.send(emote.tick)


##########################################################################################################
###====================================== Setup Etc Commands And Toggle Comamnds ========================#
##########################################################################################################

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def setup(self,ctx):
        """
        Setups The Bot In your Server
        """
        guild = ctx.guild
        member = ctx.author
        overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True,send_messages=True),
        member: discord.PermissionOverwrite(read_messages=True,send_messages=True)
    }
        channel = await guild.create_text_channel('Tea Bot Private', overwrites=overwrites)
        record = await ctx.db.fetch("SELECT * FROM public.brodcast WHERE guild_id = $1", ctx.guild.id)
        data = await ctx.db.fetch("SELECT * FROM public.server_configs WHERE guild_id = $1", ctx.guild.id)
        if not record:
            await ctx.db.execute("INSERT INTO public.brodcast (guild_id,channel_id) VALUES ($1,$2)", ctx.guild.id,channel.id)
        await ctx.db.execute('UPDATE public.brodcast SET channel_id = $2 WHERE guild_id = $1', ctx.guild.id,channel.id)
        if not data:
            await ctx.db.execute("INSERT INTO public.server_configs (guild_id,is_bot_setuped) VALUES ($1,$2)", ctx.guild.id,True)
        await ctx.db.execute('UPDATE public.server_configs SET is_bot_setuped = $1 WHERE guild_id = $2',True,ctx.guild.id)


        e = discord.Embed(title='What is this channel for?'
        ,description='This channel is made for you to get regular updates about bot. All the changelogs/update logs/bug fixes / official giveaways will be sent here.'
        ,color=self.bot.color)
        e.set_author(name="TierGamerpy#0252",icon_url='https://cdn.discordapp.com/avatars/749550694469599233/9abccc9f94b2f9e01cc2e788ff3c8cf0.webp?size=1024')
        e.add_field(name = '**__Important Notes__**',value='''▫️Do not rename this channel.\n▫️You can test bot's commands here if you want to.''')
        e.add_field(name='**__Important Link__**',value='[Support Server](https://discord.gg/rwQdnnQAXr)')
        pinningmsg = await channel.send(embed=e)
        await pinningmsg.pin(reason = 'bcs its important')
        await ctx.send(f'channel has been created <#{channel.id}>')
        await ctx.message.add_reaction(f'<:tick:820320509564551178>')

    
    @config.command(name='automeme-set')
    @commands.has_permissions(manage_guild=True)
    async def config_autommeme_set(self,ctx,channel:discord.TextChannel):
        '''
        Turn On Automeme
        '''
        data = await ctx.db.fetchval('SELECT is_bot_setuped FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if data == False:
            raise expectations.NotSetup
        await ctx.db.execute('UPDATE public.server_configs SET automeme_channel_id = $2,automeme_toogle = $3 WHERE guild_id = $1', ctx.guild.id, channel.id,True)
        await ctx.send(f'{emote.tick} | Successfully Setuped Automeme Channel To {channel.mention}')

    @config.command(name='autorole-set-human')
    @commands.has_permissions(manage_guild=True)
    async def config_autorole_set_human(self,ctx,role:discord.Role):
        '''
        Sets The Autorole For Human 
        '''
        data = await ctx.db.fetchval('SELECT is_bot_setuped FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if data == False:
            raise expectations.NotSetup
        botrole = discord.utils.get(ctx.guild.roles,name="TEA BOT")
        if role.position > botrole.position:
            await ctx.send(f'{emote.error} | My Role Is Not Above The Mentioned Role, Please Put My Role Above The Mentioned Role And Try Again')
            return
        else:
            pass
        await ctx.db.execute('UPDATE public.server_configs SET autorole_human = $2,autorole_human_toggle = $3 WHERE guild_id = $1', ctx.guild.id, role.id,True)
        await ctx.send(f'{emote.tick} | Successfully Set Autorole For Humans To {role.name}')


    @config.command(name='autorole-set-bot')
    @commands.has_permissions(manage_guild=True)
    async def config_autorole_set_bot(self,ctx,role:discord.Role):
        '''
        Sets The Autorole For Bots 
        '''
        data = await ctx.db.fetchval('SELECT is_bot_setuped FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if data == False:
            raise expectations.NotSetup
        botrole = discord.utils.get(ctx.guild.roles,name="TEA BOT")
        if role.position > botrole.position:
            await ctx.send(f'{emote.error} | My Role Is Not Above The Mentioned Role, Please Put My Role Above The Mentioned Role And Try Again')
            return
        else:
            pass
        await ctx.db.execute('UPDATE public.server_configs SET autorole_bot = $2,autorole_bot_toggle = True WHERE guild_id = $1', ctx.guild.id, role.id,True)
        await ctx.send(f'{emote.tick} | Successfully Set Autorole For Bots To {role.name}')

    @config.command(name='toggle')
    @commands.has_permissions(manage_guild=True)
    async def config_toggle(self, ctx,*, args):
        """
        This command handles the multiple modules of the to turn on and off

        Modules: 
            `autorole` - turn on/off autorole for human and bot both
            `autorole-human` - turn on/off autorole for human 
            `autorole-bot` - turn on/off autorole for bot
            `automeme` - turn on/off automeme
        """
        data = await ctx.db.fetchval('SELECT is_bot_setuped FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if data == False:
            raise expectations.NotSetup
        data = await ctx.db.fetchrow('SELECT * FROM public.server_configs WHERE guild_id = $1',ctx.guild.id)
        
        if args == 'autorole':
            if data['autorole_toggle'] == False:
                await ctx.db.execute('UPDATE public.server_configs SET autorole_toggle = $1 WHERE guild_id = $2',True,ctx.guild.id)
                await ctx.send(f'{emote.tick} | Successfully Enabled Autorole')
                return
            else:
                await ctx.db.execute('UPDATE public.server_configs SET autorole_toggle = $1 WHERE guild_id = $2',False,ctx.guild.id)
                await ctx.send(f'{emote.tick} | Successfully Disabled Autorole')
                return
        elif args == 'autorole-human':
            if data['autorole_human_toggle'] == False:
                await ctx.db.execute('UPDATE public.server_configs SET autorole_human_toggle = $1 WHERE guild_id = $2',True,ctx.guild.id)
                await ctx.send(f'{emote.tick} | Successfully Enabled Autorole For Humans')
                return
            else:
                await ctx.db.execute('UPDATE public.server_configs SET autorole_human_toggle = $1 WHERE guild_id = $2',False,ctx.guild.id)
                await ctx.send(f'{emote.tick} | Successfully Disabled Autorole For Humans')
                return
        elif args == 'autorole-bot':
            if data['autorole_bot_toggle'] == False:
                await ctx.db.execute('UPDATE public.server_configs SET autorole_bot_toggle = $1 WHERE guild_id = $2',True,ctx.guild.id)
                await ctx.send(f'{emote.tick} | Successfully Enabled Autorole For Bots')
                return
            else:
                await ctx.db.execute('UPDATE public.server_configs SET autorole_bot_toggle = $1 WHERE guild_id = $2',False,ctx.guild.id)
                await ctx.send(f'{emote.tick} | Successfully Disabled Autorole For Bots')
                return
        elif args == 'automeme':
            if data['automeme_toogle'] == False:
                await ctx.db.execute('UPDATE public.server_configs SET automeme_toogle = $1 WHERE guild_id = $2',True,ctx.guild.id)
                await ctx.send(f'{emote.tick} | Successfully Enabled Automeme')
                return
            else:
                await ctx.db.execute('UPDATE public.server_configs SET automeme_toogle = $1 WHERE guild_id = $2',False,ctx.guild.id)
                await ctx.send(f'{emote.tick} | Successfully Disabled Automeme')
                return
        else:
            await ctx.send(f'{emote.error} | Thats Not A Valid Argument Please Choose A valid Argument')
            await ctx.send_help(ctx.command)

def setup(bot):
    bot.add_cog(BotSettings(bot))