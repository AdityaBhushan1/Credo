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
        self.auto_close_reg.start()
        # self.db_update_autoclean.start()

    ###################################################################################################################
    #========================================scrims manager Auto Clean================================================#
    ###################################################################################################################

    @tasks.loop(hours=24)
    async def auto_clean(self):
        # print('entered Auto Clean')
        ch = await self.bot.db.fetch(f'SELECT * FROM smanager.custom_data WHERE auto_clean = $1 AND toggle = $2 AND is_registeration_done_today = $3 AND is_running = $4 AND is_registeration_done_today = $5',True,True,True,False,True)
        rl = await self.bot.db.fetch(f'SELECT * FROM smanager.custom_data WHERE auto_clean = $1 AND toggle = $2 AND is_registeration_done_today = $3 AND is_running = $4 AND is_registeration_done_today = $5',True,True,True,False,True)
        channel_ids = []
        for res in ch:
            res = res['reg_ch']
            channel_ids.append(res)
        for channel in channel_ids:
            final_channel = self.bot.get_channel(channel)
            try:
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
                    await m.remove_roles(role,reason = 'Credo Scims Mnagaer Autoclean')
                except:
                    continue
        await self.bot.db.execute('UPDATE smanager.custom_data SET is_registeration_done_today = $1 WHERE is_registeration_done_today = $2',False,True)
        

                


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
        # monday -----------------------------------
        if dt.date.today().isoweekday() == 1:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_monday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            # # # # if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # tuesday -----------------------------------
        elif dt.date.today().isoweekday() == 2:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_tuesday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            # # # # if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # wednesday -----------------------------------
        elif dt.date.today().isoweekday() == 3:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_wednesday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            # # # # if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # thursday -----------------------------------
        elif dt.date.today().isoweekday() == 4:
            # print('thursday')
            data = await self.bot.db.fetch(f"""
            SELECT * FROM smanager.custom_data WHERE 
            open_time <= $1 
            AND toggle = $2 
            AND is_running = $3 
            AND is_registeration_done_today = $4 
            AND allowed_slots != $5 
            AND open_on_thursday = $6 
            """
            ,datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            # # # if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
                # print('dipatched')
        # friday -----------------------------------
        elif dt.date.today().isoweekday() == 5:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_friday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            # # # if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # saturday -----------------------------------
        elif dt.date.today().isoweekday() == 6:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots != $5 AND open_on_saturday = $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        # sunday -----------------------------------
        elif dt.date.today().isoweekday() == 7:
            data = await self.bot.db.fetch(f"SELECT reg_ch FROM smanager.custom_data WHERE open_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4 AND allowed_slots = $5 AND open_on_sunday != $6",datetime.now(timezone("Asia/Kolkata")).time(),True,False,False,0,True)
            # # # if not data: return
            channel_id = []
            for res in data:
                res = res['reg_ch']
                channel_id.append(res)
            for channel in channel_id:
                self.bot.dispatch("reg_open",channel)
        else:
            # print('Not Entered Any Day')
            pass

    @auto_open.before_loop
    async def before_auto_open(self):
        await self.bot.wait_until_ready()


    ###################################################################################################################
    #========================================scrims manager Auto Close================================================#
    ###################################################################################################################

    @tasks.loop(seconds = 30)
    async def auto_close_reg(self):
        data = await self.bot.db.fetch(f"SELECT * FROM smanager.custom_data WHERE close_time <= $1 AND toggle = $2 AND is_running = $3 AND is_registeration_done_today = $4",datetime.now(timezone("Asia/Kolkata")).time(),True,True,False)
        channel_id = []
        for res in data:
            res = res['reg_ch']
            channel_id.append(res)
        for channel in channel_id:
            self.bot.dispatch("auto_close_reg",channel)
        

    @auto_close_reg.before_loop
    async def before_auto_close_reg(self):
        await self.bot.wait_until_ready()
    
def setup(bot):
    bot.add_cog(SmanagerTasks(bot))
