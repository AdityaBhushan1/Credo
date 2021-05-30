import asyncio
from discord.ext import commands,tasks
import datetime as dt
from datetime import datetime,timedelta
from pytz import timezone

class SmanagerTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_clean.start()
        self.auto_open.start()

    ###################################################################################################################
    #========================================scrims manager Auto Clean================================================#
    ###################################################################################################################

    @tasks.loop(hours = 24)
    async def auto_clean(self):
        # print('entered Auto Clean')
        ch = await self.bot.db.fetch(f'SELECT reg_ch FROM smanager.custom_data WHERE auto_clean = $1 AND toggle = $2',True,True)
        rl = await self.bot.db.fetch(f'SELECT correct_reg_role FROM smanager.custom_data WHERE auto_clean = $1 AND toggle = $2',True,True)
        channel_ids = []
        
        for res in ch:
            # print('entered Ch appending')
            res = res['reg_ch']
            channel_ids.append(res)
        for channel in channel_ids:
            # print('entered Ch final')
            final_channel = self.bot.get_channel(channel)
            try:
            # print('Purging')
            # print(print(final_channel.id))
                await final_channel.purge(limit = 200 ,check = lambda x: not x.pinned)
            except:
                continue

        role_ids = []
        for ress in rl:
            ress = ress['correct_reg_role']
            role_ids.append(ress)
        for role_id in role_ids:
            guild_id = await self.bot.db.fetchval(f'SELECT guild_id FROM smanager.custom_data WHERE auto_clean = $1 AND correct_reg_role = $2',True,role_id)
            guild = self.bot.get_guild(guild_id)
            role = guild.get_role(role_id)
            for m in role.members:
                try:
                    await m.remove_roles(role,reason = 'Teabot Scims Mnagaer Autoclean')
                except:
                    continue
        await self.bot.db.execute('UPDATE smanager.custom_data SET is_registeration_done_today = $1 WHERE is_registeration_done_today = $2',False,True)
        # print('entered done')
                


    @auto_clean.before_loop
    async def before_auto_clean(self):
        await self.bot.wait_until_ready()
        hour, minute = 00,15

        now = datetime.now()
        future = datetime(now.year, now.month, now.day, hour, minute)

        if now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)

        delta = (future - now).seconds
        print(delta)
        await asyncio.sleep(delta)
        

    ###################################################################################################################
    #========================================scrims manager Auto Open=================================================#
    ###################################################################################################################
    @tasks.loop(seconds = 30)
    async def auto_open(self):
        # sunday -----------------------------------
        if dt.date.today().isoweekday() == 7:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND open_on_sunday = $5 AND allowed_slots != $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,True,0)
            if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # monday -----------------------------------
        elif dt.date.today().isoweekday() == 1:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_monday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # tuesday -----------------------------------
        elif dt.date.today().isoweekday() == 2:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_tuesday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # wednesday -----------------------------------
        elif dt.date.today().isoweekday() == 3:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_wednesday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # thursday -----------------------------------
        elif dt.date.today().isoweekday() == 4:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_thursday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # friday -----------------------------------
        elif dt.date.today().isoweekday() == 5:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_friday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # saturday -----------------------------------
        elif dt.date.today().isoweekday() == 6:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_saturday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        else:
            pass


    @auto_open.before_loop
    async def before_auto_open(self):
        await self.bot.wait_until_ready()
    

