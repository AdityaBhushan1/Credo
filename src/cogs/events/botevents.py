import discord
from discord.ext import commands
from ..utils import emote

class RemoverRvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self,channel):
        record = await self.bot.db.fetchrow('SELECT * FROM public.server_configs WHERE guild_id = $1',channel.guild.id)
        brocast = await self.bot.db.fetchrow('SELECT * FROM public.brodcast WHERE guild_id = $1',channel.guild.id)
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE reg_ch = $1',channel.id)
        tag_check = await self.bot.db.fetchrow('SELECT * FROM smanager.tag_check WHERE guild_id = $1',channel.guild.id)

        if tag_check['ch_id'] == channel.id:
            await self.bot.db.execute('UPDATE smanager.tag_check SET toggle = $1 WHERE guild_id = $2',False,channel.guild.id)
            return
        else:
            pass
        if record['automeme_channel_id'] == channel.id:
            await self.bot.db.execute('UPDATE public.server_configs SET automeme_channel_id = NULL automeme_toogle = $1 WHERE guild_id = $2',False,channel.guild.id)
            return
        else:
            pass
        
        if record['autonsfw_channel_id'] == channel.id:
            await self.bot.db.execute('UPDATE public.server_configs SET autonsfw_channel_id = NULL autonsfw_toogle = $1 WHERE guild_id = $2',False,channel.guild.id)
            return
        else:
            pass
        if brocast['channel_id'] == channel.id:
            await self.bot.db.execute('DELETE FROM public.brodcst WHERE guild_id = $1',channel.guild.id)
            return
        else:
            pass
        if scrims_manager['reg_ch'] == channel.id:
            log_ch = discord.utils.get(channel.guild.channels, name='teabot-sm-logs')
            await self.bot.db.execute('UPDATE smanager.custom_data SET toggle = $1 WHERE reg_ch = $2',False,channel.id)
            await log_ch.send(f"{emote.error} | The Registration Cahnnel For `{scrims_manager['c_id']}` And Its Toggled Off Please Set New Cahnnel With Edit Commadn Then Toggle It On")
            return
        else:
            pass


    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        data = await self.bot.db.fetchval('SELECT is_server_premium FROM server_configs WHERE guild_id = $1',guild.id)
        if data == True:
            return
        await self.bot.execute('DELETE FROM public.brodcst WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM public.server_configs WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM smanager.tag_check WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM smanager.custom_data WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM plonks WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM plonks WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM command_config WHERE guild_id = $1',guild.id)

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        data = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',guild.id)
        if not data:
            await self.bot.db.execute('INSERT INTO server_configs (guild_id) VALUES($1)',guild.id)
            await self.bot.db.execute('INSERT INTO brodcast (guild_id) VALUES($1)',guild.id)
# #todo fix this
#     @commands.Cog.listener()
#     async def on_guild_role_delete(self,role):
#         autorole = await self.bot.db.fetchval('SELECT autoroleid FROM public.autorole WHERE guild_id = $1',role.guild.id)

#         if autorole == role.id:
#             await self.bot.db.execute('DELETE FROM public.autorole WHERE guild_id = $1',role.guild.id)
#         else:
#             pass

def setup(bot):
    bot.add_cog(RemoverRvents(bot))