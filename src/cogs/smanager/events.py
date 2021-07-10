import discord,re
from discord.ext import commands
from ..utils import emote
from prettytable import PrettyTable,ORGMODE
import json
from .sutils import delete_denied_message


class EsportsListners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scrim_data = {}
    

####################################################################################################################
#============================================= scrims manager registrations processes =============================#
####################################################################################################################
    @commands.Cog.listener()
    async def on_message(self,message):
        if not message.guild or message.author.bot:
            return
        # print('entered')
        scrims = await self.bot.db.fetchrow(f'SELECT * FROM smanager.custom_data WHERE reg_ch = $1 AND toggle = $2',message.channel.id,True)
        if not scrims:
            # print('not scrims')
            return 

        elif "credo-smanger" in [role.name for role in message.author.roles]:
            # print('bot,role')
            return

        elif "credo-sm-banned" in [role.name for role in message.author.roles]:
            if scrims['auto_delete_on_reject'] == True:
                self.bot.loop.create_task(delete_denied_message(message))
                return
            return

        elif scrims['is_running'] == False:
            if scrims['auto_delete_on_reject'] == True:
                self.bot.loop.create_task(delete_denied_message(message))
            return await message.reply(f'{emote.error} | Registration Has Not Opend Yet',delete_after=10)
            

        
        elif len([mem for mem in message.mentions]) == 0 or len([mem for mem in message.mentions]) < scrims['num_correct_mentions']:
            if scrims['auto_delete_on_reject'] == True:
                self.bot.loop.create_task(delete_denied_message(message))
                self.bot.dispatch("deny_reg",message,"insufficient_mentions")
                return
            return self.bot.dispatch("deny_reg",message,"insufficient_mentions")
        else:
            for mem in message.mentions:
                if mem.bot in message.mentions:
                    if scrims['auto_delete_on_reject'] == True:
                        self.bot.loop.create_task(delete_denied_message(message))
                        self.bot.dispatch("deny_reg",message,"mentioned_bot")
                        return
                    return self.bot.dispatch("deny_reg",message,"mentioned_bot")
                else:pass

            team_name = re.search(r"team.*", message.content.lower())
            if team_name is None:
                return f"{message.author}'s team"

            team_name = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", team_name.group()).strip()

            team_name = f"Team {team_name.title()}" if team_name else f"{message.author}'s team"

            if team_name in self.scrim_data[scrims['c_id']]["team_name"]:
                if scrims['auto_delete_on_reject'] == True:
                    self.bot.loop.create_task(delete_denied_message(message))
                    self.bot.dispatch("deny_reg",message,"allready_registerd")
                    return
                return self.bot.dispatch("deny_reg",message,"allready_registerd")
            else:

                self.scrim_data[scrims['c_id']]['counter'] = self.scrim_data[scrims['c_id']]['counter'] - 1

                self.scrim_data[scrims['c_id']]['team_name'].append(f"{team_name}")
                if self.scrim_data[scrims['c_id']]['counter'] == 0:
                    self.bot.dispatch("auto_close_reg",message.channel.id)
                

                role = discord.utils.get(message.guild.roles, id = scrims['correct_reg_role'])
                try:
                    await message.author.add_roles(role)
                    
                except:
                    pass
                # print('updated cache')
                try:
                    await message.add_reaction(f'{emote.tick}')
                except:
                    pass
                self.bot.dispatch("correct_reg_logs",message,team_name)

####################################################################################################################
#============================================= scrims manager Auto close registration =============================#
####################################################################################################################

    @commands.Cog.listener()
    async def on_auto_close_reg(self,channel_id):
        scrims = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE reg_ch = $1',channel_id)
        guild = self.bot.get_guild(scrims['guild_id'])
        channel = self.bot.get_channel(channel_id)
        if scrims['open_role'] == None:
            overwrite = channel.overwrites_for(guild.default_role)
            overwrite.send_messages = False
            overwrite.view_channel = True
            try:
                await channel.set_permissions(guild.default_role, overwrite=overwrite)
            except:
                pass
            message = scrims['close_message_embed']
            embed = json.loads(message)
            em = discord.Embed.from_dict(embed)
            await channel.send(embed = em)
            self.bot.dispatch("reg_closed_db_update",scrims)
            self.bot.dispatch("reg_closed_logs",scrims['c_id'],scrims['custom_title'],scrims['custom_num'],scrims['guild_id'])
            await self.bot.db.execute('UPDATE smanager.custom_data SET is_running = $1, is_registeration_done_today = $2 WHERE reg_ch = $3',False,True,channel.id)
        else:
            role = guild.get_role(scrims["open_role"])
            overwrite = channel.overwrites_for(role)
            overwrite.send_messages = False
            overwrite.view_channel = True
            try:
                await channel.set_permissions(role, overwrite=overwrite)
            except:
                pass
            message = scrims['close_message_embed']
            embed = json.loads(message)
            em = discord.Embed.from_dict(embed)
            await channel.send(embed = em)
            self.bot.dispatch("reg_closed_db_update",scrims)
            self.bot.dispatch("reg_closed_logs",scrims['c_id'],scrims['custom_title'],scrims['custom_num'],scrims['guild_id'])
            await self.bot.db.execute('UPDATE smanager.custom_data SET is_running = $1, is_registeration_done_today = $2 WHERE reg_ch = $3',False,True,channel.id)

####################################################################################################################
#============================================= scrims manager registrations close db update =======================#
####################################################################################################################

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

####################################################################################################################
#============================================= scrims manager slotlist sender =====================================#
####################################################################################################################

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
        if not channel:return
        else:
            await self.bot.db.execute(f'UPDATE smanager.custom_data SET is_running = $1,team_names = NULL WHERE reg_ch = $2',True,channel.id)
            data = await self.bot.db.fetchrow(f"SELECT * FROM smanager.custom_data WHERE reg_ch = $1",channel.id)
            guild = await self.bot.fetch_guild(data['guild_id'])
            if not guild:return 
            else:
                if data['open_role'] == None:
                    overwrite = channel.overwrites_for(guild.default_role)
                    overwrite.send_messages = True
                    overwrite.view_channel = True
                    self.scrim_data[data['c_id']] = {"counter":data['allowed_slots'],"team_name":[]}
                    try:
                        await channel.set_permissions(guild.default_role, overwrite=overwrite)
                    except:
                        self.bot.dispatch("cannot_open_reg",guild.id,f"I Was Unable To Open Registration For `{data['c_id']}` Because I Don't Have Premission To Manager Channe")
                        self.scrim_data.pop(data['c_id'])
                        return
                    else:
                        self.bot.dispatch("reg_ch_open_msg",channel.id)
                        self.bot.dispatch("reg_open_msg_logs",channel.id,guild.id)
                else:
                    role = guild.get_role(data["open_role"])
                    overwrite = channel.overwrites_for(role)
                    overwrite.send_messages = True
                    overwrite.view_channel = True
                    self.scrim_data[data['c_id']] = {"counter":data['allowed_slots'],"team_name":[]}
                    try:
                        await channel.set_permissions(guild.default_role, overwrite=overwrite)
                    except:
                        self.bot.dispatch("cannot_open_reg",guild.id,f"I Was Unable To Open Registration For `{data['c_id']}` Because I Don't Have Premission To Manager Channe")
                        self.scrim_data.pop(data['c_id'])
                        return
                    else:
                        self.bot.dispatch("reg_ch_open_msg",channel.id)
                        self.bot.dispatch("reg_open_msg_logs",channel.id,guild.id)

        


####################################################################################################################
#====================================================== scrims manager Logs Listeners =============================#
####################################################################################################################
    @commands.Cog.listener()
    async def on_reg_ch_open_msg(self,channel_id):
        ch = await self.bot.fetch_channel(channel_id)
        data = await self.bot.db.fetchrow(f"SELECT * FROM smanager.custom_data WHERE reg_ch = $1",ch.id)
        message = data['open_message_embed']
        message = message.replace('<<available_slots>>',f"{data['allowed_slots']}")
        message = message.replace('<<reserved_slots>>',f"{data['reserverd_slots']}")
        message = message.replace('<<total_slots>>',f"{data['num_slots']}")
        message = message.replace('<<custom_title>>',f"{data['custom_title']}")
        message = message.replace('<<mentions_required>>',f"{data['num_correct_mentions']}")
        embed = json.loads(message)
        em = discord.Embed.from_dict(embed)
        guild = self.bot.get_guild(data['guild_id'])
        role = guild.get_role(data["ping_role"])
        await ch.send(content = role.mention if role else None ,embed=em,allowed_mentions=discord.AllowedMentions(roles=True))

    @commands.Cog.listener()
    async def on_deny_reg(self,message,type,addreact=True):
        if type == "insufficient_mentions":
            await message.reply('You Did Not Mentioned Correct Number Of Peoples',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Due To Insufficient Mentions",message.guild.id)
            if addreact == True:
                try:
                    await message.add_reaction(f'{emote.xmark}')
                except:
                    pass
        elif type == "mentioned_bot":
            await message.reply('You Mentioned A Bot',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Because They Have Mentioned A Bot",message.guild.id)
            if addreact == True:
                try:
                    await message.add_reaction(f'{emote.xmark}')
                except:
                    pass
        elif type == "baned_from_scrims":
            await message.reply('You Are banned From Scrims',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Because They Are Banned Form Scrims",message.guild.id)
            if addreact == True:
                try:
                    await message.add_reaction(f'{emote.xmark}')
                except:
                    pass
        # elif type == "incorrect_teamname":
        #     await message.reply('Team Name Is Not Correct',delete_after=10)
        #     self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Because No Team Name Was Given",message.guild.id)
        #     if addreact == True:
        #         try:
        #             await message.add_reaction(f'{emote.xmark}')
        #         except:
        #             pass
        elif type == "allready_registerd":
            await message.reply('You Are Already Registred',delete_after=10)
            self.bot.dispatch("deny_reg_logs",f"Reagistration For {message.author}'s Team Has Been Dnied Because They Are Already Registerd",message.guild.id)
            if addreact == True:
                try:
                    await message.add_reaction(f'{emote.xmark}')
                except:
                    pass
        else:
            pass

    @commands.Cog.listener()
    async def on_correct_reg_logs(self,message,team_name):
        log_ch = discord.utils.get(message.guild.channels, name='credo-sm-logs')
        em = discord.Embed(title = f'🛠️ SuccessFull Registration 🛠️',description = f'{emote.tick} | Registration For Team Name = `{team_name}` Is Successfully Accepeted',color=self.bot.color)
        await log_ch.send(embed = em)

    @commands.Cog.listener()
    async def on_reg_closed_logs(self,customid,customname,customnum,guild_id):
        guild = self.bot.get_guild(guild_id)
        log_channel = discord.utils.get(guild.channels, name='credo-sm-logs')
        msg = discord.Embed(title = f'🛠️ Registration Closed 🛠️', description = f'{emote.tick} | Succesfully Closed Registration For Custom ID = `{customid}`, Custom Number = `{customnum}`, Custom Name = `{customname}`',color=self.bot.color)
        await log_channel.send(embed=msg)

    @commands.Cog.listener()
    async def on_reg_open_msg_logs(self,ch_id,guild_id):
        guild = self.bot.get_guild(guild_id)
        # print(guild)
        # print('entered on_reg_open_msg_logs')
        ch = await self.bot.fetch_channel(ch_id)
        data = await self.bot.db.fetchrow(f"SELECT * FROM smanager.custom_data WHERE reg_ch = $1",ch.id)
        log_ch = discord.utils.get(guild.channels, name='credo-sm-logs')
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
        log_channel = discord.utils.get(guild.channels, name='credo-sm-logs')
        em = discord.Embed(title = '🛠️ Registration Denied 🛠️' ,description = f'{message}',color=self.bot.color)
        await log_channel.send(embed=em)

    @commands.Cog.listener()
    async def on_cannot_open_reg(self,guild_id,message:str):
        guild = self.bot.get_guild(guild_id)
        log_channel = discord.utils.get(guild.channels, name='credo-sm-logs')
        em = discord.Embed(title = '🛠️ Cannot Open Registartion 🛠️' ,description = f'{message}',color=self.bot.color)
        await log_channel.send(embed=em)

####################################################################################################################
#============================================= channel delete listners ============================================#
####################################################################################################################

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        data = await self.bot.db.fetchrow(f"SELECT * FROM smanager.custom_data WHERE reg_ch = $1",channel.id)
        if not data: pass
        else:
            if channel.id == int(data['reg_ch']):
                await self.bot.db.execute("UPDATE smanager.custom_data SET toggle = $1 WHERE c_id = $2",False,data['c_id'])
                if data['is_running'] == True:
                    await self.bot.db.execute("UPDATE smanager.custom_data SET is_running = $1,is_registeration_done_today = $2 WHERE c_id = $3 AND is_running = $4",False,True,data['c_id'],True)
                else:
                    pass
                log_channel = discord.utils.get(channel.guild.channels, name='credo-sm-logs')
                em = discord.Embed(description = f"The Regitration Channel For Scrims With Id `{data['c_id']}` Has Been Deleted And Scrims Is Toggled Off Kinldy Set New Channel And Toggle It On",color = self.bot.color)
                await log_channel.send(embed=em)
            else:pass

        slot_ch = await self.bot.db.fetchrow(f"SELECT * FROM smanager.tag_check WHERE ch_id = $1",channel.id)

        if not slot_ch:pass
        else:
            if channel.id == int(slot_ch['ch_id']):
                await self.bot.dd.execute('DELETE FROM smanager.custom_data WHERE ch_id = $1',channel.id)
                log_channel = discord.utils.get(channel.guild.channels, name='credo-sm-logs')
                em = discord.Embed(description = f"The Tag Check Channel Has Been Deleted Kindly Setup Tag Check Again With New Channel",color = self.bot.color)
                await log_channel.send(embed=em)
            else:pass

        easy_tagging = await self.bot.db.fetchrow(f"SELECT * FROM smanager.ez_tag WHERE ch_id = $1",channel.id)

        if not easy_tagging:pass
        else:
            if channel.id == int(slot_ch['ch_id']):
                await self.bot.dd.execute('DELETE FROM smanager.ez_tag WHERE ch_id = $1',channel.id)
                log_channel = discord.utils.get(channel.guild.channels, name='credo-sm-logs')
                em = discord.Embed(description = f"The Easy Tag Channel Has Been Deleted Kindly Setup Easy Tag Again With New Channel",color = self.bot.color)
                await log_channel.send(embed=em)
            else:pass


####################################################################################################################
#================================================ Role delete listners ============================================#
####################################################################################################################

####################################################################################################################
#============================================= tag check listners =================================================#
####################################################################################################################

    @commands.Cog.listener(name = 'on_message')
    async def on_tag_check_message(self,message):
        data = await self.bot.db.fetchrow('SELECT * FROM smanager.tag_check WHERE ch_id = $1 AND toggle != $2',message.channel.id,False)
        if not data:
            return

        mentions = len([mem for mem in message.mentions])
        if mentions == 0 or mentions < data['mentions_required']:
            await message.reply('You Did Not Mentioned Correct Number Of Peoples',delete_after=10)
            try:
                await message.add_reaction(f'{emote.xmark}')
            except:
                pass
            return

        for mem in message.mentions:
            if mem.bot:
                await message.reply('You Mentioned A Bot',delete_after=10)
                try:
                    await message.add_reaction(f'{emote.xmark}')
                except:
                    pass
                return
        team_name = re.search(r"team.*", message.content.lower())
        if team_name is None:
            return f"{message.author}'s team"
        team_name = re.sub(r"<@*#*!*&*\d+>|team|name|[^\w\s]", "", team_name.group()).strip()
        team_name = f"Team {team_name.title()}" if team_name else f"{message.author}'s team"
        try:
            await message.add_reaction(f'{emote.tick}')
        except:
            pass
        em = discord.Embed(color=self.bot.color)
        em.description = f"Team Name: {team_name}\nPlayers: {(', '.join(m.mention for m in message.mentions)) if message.mentions else message.author.mention}"
        await message.reply(embed = em)


####################################################################################################################
#============================================= easy tagging listners ==============================================#
####################################################################################################################

        
    @commands.Cog.listener(name = 'on_message')
    async def on_ez_tag_message(self,message):
        if not message.guild or message.author.bot:
            return
        channel_id = message.channel.id
        data = await self.bot.db.fetchrow("SELECT * FROM smanager.ez_tag WHERE ch_id = $1 AND toggle = $2",channel_id,True)

        if not data:return
        elif len([mem for mem in message.mentions]) == 0:
            self.bot.loop.create_task(delete_denied_message(message,5))
            await message.reply(content = f'{emote.error} | There Are No Mentions In This Message',delete_after = 5) 
            return
        else:
            members_mentions = list()
            for mem in message.mentions:
                if mem.bot in message.mentions:
                    self.bot.loop.create_task(delete_denied_message(message,5))
                    await message.reply(content = f'{emote.error} | You Have Mentioned A Bot',delete_after = 5) 
                    return
                members_mentions.append(f'<@!{mem.id}>')
            mentions = ", ".join(members_mentions)
            msg = await message.reply(f"```{message.clean_content}\nTags: {mentions}```")
            self.bot.loop.create_task(delete_denied_message(msg,10))
            self.bot.loop.create_task(delete_denied_message(message,5))
