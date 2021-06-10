import discord
from discord.ext import commands
from ..utils import emote

class RemoverRvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self,channel):
        record = await self.bot.db.fetchrow('SELECT * FROM public.server_configs WHERE guild_id = $1',channel.guild.id)
        if not record:return

        if record['automeme_channel_id'] == int(channel.id):
            await self.bot.db.execute('UPDATE public.server_configs SET automeme_channel_id = NULL automeme_toogle = $1 WHERE guild_id = $2',False,channel.guild.id)
            return
        else:
            pass
        
        brocast = await self.bot.db.fetchrow('SELECT * FROM public.brodcast WHERE guild_id = $1',channel.guild.id)
        if not brocast:return
        if brocast['channel_id'] == int(channel.id):
            await self.bot.db.execute('DELETE FROM public.brodcst WHERE guild_id = $1',channel.guild.id)
            await self.bot.db.execute('UPDATE public.server_configs SET is_bot_setuped = $1 WHERE guild_id = $2',False,channel.guild.id)
            return
        else:
            pass


    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        await self.bot.execute('DELETE FROM public.brodcst WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM public.server_configs WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM smanager.tag_check WHERE guild_id = $1',guild.id)
        await self.bot.execute('DELETE FROM smanager.custom_data WHERE guild_id = $1',guild.id)

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