import discord
from discord.ext import commands
from ..utils import emote
from prettytable import PrettyTable,ORGMODE


class SmanagerListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scrim_data = {}
    

####################################################################################################################
#============================================= scrims manager registrations processes =============================#
####################################################################################################################
    @commands.Cog.listener()
    async def on_message(self,message):
        # print('entered')
        scrims = await self.bot.db.fetchrow(f'SELECT * FROM smanager.custom_data WHERE reg_ch = $1',message.channel.id)
        if not scrims:
            # print('not scrims')
            return 

        if scrims['toggle'] == False:
            # print('false toogle')
            return
        if message.author.bot or "teabot-smanger" in [role.name for role in message.author.roles]:
            # print('bot,role')
            return

        if "teabot-sm-banned" in [role.name for role in message.author.roles]:
            return self.bot.dispatch("deny_reg",message,"baned_from_scrims")

        if scrims['is_running'] == False:
            # print('running false')
            await message.reply(f'{emote.error} | Registration Has Not Opend Yet',delete_after=10)
            return

        mentions = len([mem for mem in message.mentions])
        if mentions == 0 or mentions < scrims['num_correct_mentions']:
            return self.bot.dispatch("deny_reg",message,"insufficient_mentions")

        for mem in message.mentions:
            if mem.bot:
                return self.bot.dispatch("deny_reg",message,"mentioned_bot")

        try:
            matched_lines = [line.strip() for line in message.clean_content.lower().split('\n') if "team" in line]
            team_name = [x for x in matched_lines[0].lower().split() if x not in {'team', 'name', ':', '-', ':-', 'name:', 'name-', 'name:-'}]
            team_name = ' '.join([i for i in team_name if all(ch not in i for ch in ['@'])])
        except:
            return self.bot.dispatch("deny_reg",message,"incorrect_teamname")
        
        if team_name is None:
            team_name = f'{message.author.name} Team'

        if team_name in self.scrim_data[scrims['c_id']]["team_name"]:
            return self.bot.dispatch("deny_reg",message,"allready_registerd")

        self.scrim_data[scrims['c_id']]['counter'] = self.scrim_data[scrims['c_id']]['counter'] - 1

        self.scrim_data[scrims['c_id']]['team_name'].append(f"{team_name}")
        if self.scrim_data[scrims['c_id']]['counter'] == 0:
            self.bot.dispatch("auto_close_reg",message,scrims)

        role = discord.utils.get(message.guild.roles, id = scrims['correct_reg_role'])
        try:
            await message.author.add_roles(role)
            # print('asssgined role')
        except:
            pass
        # print('updated cache')
        try:
            await message.add_reaction(f'{emote.tick}')
        except:
            pass
        self.bot.dispatch("correct_reg_logs",message,team_name)


    @commands.Cog.listener()
    async def on_auto_close_reg(self,message,scrims):
        overwrite = message.channel.overwrites_for(message.guild.default_role)
        overwrite.send_messages = False
        overwrite.view_channel = True
        try:
            await message.channel.set_permissions(message.guild.default_role, overwrite=overwrite)
        except:
            pass
        await message.channel.send(':lock: | **__Registration Is Closed Now.__**')
        self.bot.dispatch("reg_closed_db_update",scrims)
        self.bot.dispatch("reg_closed_logs",scrims['c_id'],scrims['custom_title'],scrims['custom_num'],scrims['guild_id'])
        await self.bot.db.execute('UPDATE smanager.custom_data SET is_running = $1, is_registeration_done_today = $2 WHERE reg_ch = $3',False,True,message.channel.id)


    @commands.Cog.listener()
    async def on_reg_closed_db_update(self,data):
        for i in range(data['reserverd_slots']):
            self.scrim_data[data['c_id']]['team_name'].append('Reserved Slot')
        # print('yep')
        # print(self.scrim_data[data['c_id']]['team_name'])

        await self.bot.db.execute('UPDATE smanager.custom_data SET team_names = $1 WHERE c_id = $2',self.scrim_data[data['c_id']]['team_name'],data['c_id'])
        # print('yep')
        self.scrim_data.pop(data['c_id'])
        # print('yep')
        self.bot.dispatch("slotlist_sender",data)
        # print('yep')

    @commands.Cog.listener()
    async def on_slotlist_sender(self,datas):
        data = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1',datas['c_id'])
        if data['auto_slot_list_send'] == True:
            slot_table = PrettyTable()
            slot_table.field_names = ["Slot No.", "Team Name"]
            slot_table.set_style(ORGMODE)
            slot_count = 1
            for message in data['team_names']:
                slot_table.add_row([f"slot {slot_count}", f"{message}"])
                slot_count+=1

            embed = discord.Embed(title = f"Slotlist For {data['custom_title']}",description = f'''```py\n{slot_table}\n```''',color = self.bot.color)
            channel = data['slotlist_ch']
            if not channel:return
            ch = self.bot.get_channel(channel)
            await ch.send(embed = embed)
    

    ###################################################################################################################
    #========================================scrims manager Auto Open Listner ========================================#
    ###################################################################################################################
    @commands.Cog.listener()
    async def on_reg_open(self,channel_id):
        # print('extered on_reg_open')
        channel = await self.bot.fetch_channel(channel_id)
        await self.bot.db.execute(f'UPDATE smanager.custom_data SET is_running = $1,team_names = NULL WHERE reg_ch = $2',True,channel.id)
        data = await self.bot.db.fetchrow(f"SELECT * FROM smanager.custom_data WHERE reg_ch = $1",channel.id)
        custom_num = data['custom_num']
        guild = await self.bot.fetch_guild(data['guild_id'])
        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = True
        overwrite.view_channel = True

        self.scrim_data[data['c_id']] = {"counter":data['allowed_slots'],"team_name":[]}
        await channel.set_permissions(guild.default_role, overwrite=overwrite)
        self.bot.dispatch("reg_ch_open_msg",channel_id)
        self.bot.dispatch("reg_open_msg_logs",channel_id,guild.id)


####################################################################################################################
#====================================================== scrims manager Logs Listeners =============================#
####################################################################################################################
    @commands.Cog.listener()
    async def on_reg_ch_open_msg(self,channel_id):
        ch = await self.bot.fetch_channel(channel_id)
        data = await self.bot.db.fetchrow(f"SELECT * FROM smanager.custom_data WHERE reg_ch = $1",ch.id)
        allowe_slots = data['allowed_slots']
        slots = data['num_slots']
        reserved_slots = data['reserverd_slots']
        mentions = data['num_correct_mentions']
        em = discord.Embed(title = '🛠️ Registartion Opened 🛠️',description = f'Total Slots = *`{allowe_slots}/{slots}[{reserved_slots}]`*\nMinimum Mentions = *`{mentions}`*',color =self.bot.color)
        await ch.send(embed = em)

    @commands.Cog.listener()
    async def on_deny_reg(self,message,type):
        if type == "insufficient_mentions":
            await message.reply('You Did Not Mentioned Correct Number Of Peoples',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Due To Insufficient Mentions",message.guild.id)
            try:
                await message.add_reaction(f'{emote.xmark}')
            except:
                pass
        elif type == "mentioned_bot":
            await message.reply('You Mentioned A Bot',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Because They Have Mentioned A Bot",message.guild.id)
            try:
                await message.add_reaction(f'{emote.xmark}')
            except:
                pass
        elif type == "baned_from_scrims":
            await message.reply('You Are banned From Scrims',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Because They Are Banned Form Scrims",message.guild.id)
            try:
                await message.add_reaction(f'{emote.xmark}')
            except:
                pass
        elif type == "incorrect_teamname":
            await message.reply('Team Name Is Not Correct',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Because No Team Name Was Given",message.guild.id)
            try:
                await message.add_reaction(f'{emote.xmark}')
            except:
                pass
        elif type == "allready_registerd":
            await message.reply('You Are Already Registred',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Because They Are Already Registerd",message.guild.id)
            try:
                await message.add_reaction(f'{emote.xmark}')
            except:
                pass
        else:
            pass

    @commands.Cog.listener()
    async def on_correct_reg_logs(self,message,team_name):
        log_ch = discord.utils.get(message.guild.channels, name='teabot-sm-logs')
        em = discord.Embed(title = f'🛠️ SuccessFull Registration 🛠️',description = f'{emote.tick} | Registration For Team Name = `{team_name}` Is Successfully Accepeted',color=self.bot.color)
        await log_ch.send(embed = em)

    @commands.Cog.listener()
    async def on_reg_closed_logs(self,customid,customname,customnum,guild_id):
        guild = self.bot.get_guild(guild_id)
        log_channel = discord.utils.get(guild.channels, name='teabot-sm-logs')
        msg = discord.Embed(title = f'🛠️ Registration Closed 🛠️', description = f'{emote.tick} | Succesfully Closed Registration For Custom ID = `{customid}`, Custom Number = `{customnum}`, Custom Name = `{customname}`',color=self.bot.color)
        await log_channel.send(embed=msg)

    @commands.Cog.listener()
    async def on_reg_open_msg_logs(self,ch_id,guild_id):
        guild = self.bot.get_guild(guild_id)
        # print(guild)
        # print('entered on_reg_open_msg_logs')
        ch = await self.bot.fetch_channel(ch_id)
        data = await self.bot.db.fetchrow(f"SELECT * FROM smanager.custom_data WHERE reg_ch = $1",ch.id)
        log_ch = discord.utils.get(guild.channels, name='teabot-sm-logs')
        # print(log_ch)
        custom_id = data['c_id']
        custom_num = data['custom_num']
        custom_name = data['custom_title']
        msg = discord.Embed(title = f'🛠️ Registration Opened 🛠️', description = f'{emote.tick} | Succesfully Opened Registration For Custom ID = `{custom_id}`, Custom Number = `{custom_num}`, Custom Name = `{custom_name}`',color=self.bot.color)
        await log_ch.send(embed=msg)
        # print('Done on_reg_open_msg_logs')

    @commands.Cog.listener()
    async def on_deny_reg_logs(self,message,guild_id):
        guild = self.bot.get_guild(guild_id)
        log_channel = discord.utils.get(guild.channels, name='teabot-sm-logs')
        em = discord.Embed(title = '🛠️ Registration Denied 🛠️' ,description = f'{message}',color=self.bot.color)
        await log_channel.send(embed=em)