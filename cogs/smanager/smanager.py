import asyncio
import discord,re
from discord.ext import commands
from ..utils import emote
from .sutils import CustomEditMenu,DaysEditorMenu
from ..utils.paginitators import Pages
from prettytable import PrettyTable,ORGMODE
from datetime import datetime
from disputils import  BotConfirmation
from .listners import SmanagerListeners
from .tasks import SmanagerTasks
from .tag_check import TagCheckListners

class SManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group(invoke_without_command = True)
    async def smanager(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @smanager.command(name='setup')
    # @is_bot_setuped()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True,manage_roles=True)
    async def smanager_setup(self,ctx):
        '''
        Setups The Tea Bot Scrims Manager In Your Server
        '''
        data = await ctx.db.fetchval('SELECT is_bot_setuped FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if data == False:
            await ctx.send(f'{emote.error} | This Server Dose Not Have Bot Setuped Here Use `*setup`')
            return
        scrims_manager = await self.bot.db.fetchval('SELECT scrims_manager FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager == False:
            start_msg = await ctx.send(f'{emote.loading} | Setting Up Scrims Manager')
            guild=ctx.guild
            permissions = discord.Permissions(send_messages=True, read_messages=True,administrator=True)
            sm_role = await guild.create_role(name='teabot-smanger',permissions=permissions,colour=self.bot.color)
            sm_banned_role = await guild.create_role(name='teabot-sm-banned')
            guild = ctx.guild
            member = ctx.author
            overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True,send_messages=True),
            member: discord.PermissionOverwrite(read_messages=True,send_messages=True),
            sm_role:discord.PermissionOverwrite(read_messages=True,send_messages=True)
        }
            smlogchannel = await guild.create_text_channel('teabot-sm-logs', overwrites=overwrites)
            try:
                await ctx.author.add_roles(sm_role)
            except:
                pass
            await self.bot.db.execute(
                'UPDATE server_configs SET scrims_manager = $1 WHERE guild_id = $2',
            True,
            ctx.guild.id
            )

            slot_embed = discord.Embed(title = "🛠️Scrims Manager Logs🛠️",description = f"If events related to scrims i.e opening registrations or adding roles , etc are triggered, then they will be logged in this channel. Also I have created {sm_role.mention}, you can give that role to your scrims-moderators. User with {sm_role.mention} can also send messages in registration channels and they won't be considered as scrims-registration.\n Note: Do not rename this channel.",color = self.bot.color)
            smlogchannel_msg = await smlogchannel.send(embed=slot_embed)
            await smlogchannel_msg.pin(reason = 'bcs its important')
            await start_msg.edit(
                content = f'''
                            {emote.tick} | Created {sm_role.mention} Give This Role To Your Scrims Manager Who Manages The Scrims Note Don't Change Role Name Other Wise the Won't Able To Manage Scrims 
                            \n{emote.tick} | Created {smlogchannel.mention} Channel To Log Scrimms Manager
                            \n{emote.tick} | Created {sm_banned_role.mention} Give This Role To Banned Members From Scrims
                            \n{emote.tick} | Successfully Setuped Scrims Manager Use `*smanager setup-custom` To See Avaible Custom Help
                            ''')
        else:
            await ctx.send(f'{emote.error} | This Server Already Have Scrims Manager Setuped')


    @smanager.command(name='setup-custom')
    @commands.has_role('teabot-smanger')
    # @is_smanager_setuped()
    async def smanager_setup_custom(self,ctx):
        """
        Setups The Custom In Your Server
        """
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')

        if scrims_manager['custom_setuped'] > scrims_manager['max_customs']:
            return await ctx.send(f'{emote.error} | You Have Setuped Max Number Customs You Cannot Setup More Customs')
        await ctx.release()

        took_long = discord.Embed(title =f'{emote.error} | You took long. Goodbye.',color = self.bot.color)
        inncorrect_channel_mention = discord.Embed(title =f'{emote.error} | You Did Not Mentioned Correct Channel Please Try Agin By Running Same Command',color=self.bot.color)
        inncorrect_role_mention = discord.Embed(title =f'{emote.error} | You Did Not Mentioned Correct Role Please Try Agin By Running Same Command',color=self.bot.color)

        def check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel
# queston 1
        q1 = discord.Embed(description = f'🛠️ Ok,Lets Start You Will Get 80 Seconds To Answer Each Question \nQ1. What Should Be The Channel Where I Will Send Slot List?',color = self.bot.color)
        q1.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q1)
        try:
            slot_channel = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)

        if slot_channel.content == f'{ctx.prefix}cancel':
            return await ctx.send('Aborting.')
        if len(slot_channel.channel_mentions) == 0 or len(slot_channel.channel_mentions) > 1:
            return await ctx.send(embed= inncorrect_channel_mention)
        try:
            fetched_slot_channel = await commands.TextChannelConverter().convert(ctx,slot_channel.content)
        except:
            await ctx.send(embed= inncorrect_channel_mention)
# question 2
        q2 = discord.Embed(description = f'🛠️ Sweet! Slotlist Will Be Uploaded In {fetched_slot_channel.mention} \nQ2. What Should Be The Registration Channel Where I WIll Accept Registration?',color=self.bot.color)
        q2.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q2)
        try:
            reg_channel = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)

        if reg_channel.content == f'{ctx.prefix}cancel':
            return await ctx.send('Aborting.')
        if len(reg_channel.channel_mentions) == 0 or len(reg_channel.channel_mentions) > 1:
            return await ctx.send(embed= inncorrect_channel_mention)
        try:
            fetched_reg_channel = await commands.TextChannelConverter().convert(ctx,reg_channel.content)
        except:
            await ctx.send(embed= inncorrect_channel_mention)
# question 3
        q3 = discord.Embed(description = f'🛠️ Ok! I Will Accept Registration In {fetched_reg_channel.mention} \nQ3. which role should I give for correct registration?',color=self.bot.color)
        q3.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q3)
        try:
            succes_reg_role = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)

        if succes_reg_role.content == f'{ctx.prefix}cancel':
            return await ctx.send('Aborting.')
        if len(succes_reg_role.role_mentions) == 0 or len(succes_reg_role.role_mentions) > 1:
            return await ctx.send(embed=inncorrect_role_mention)
        try:
            fetched_succes_reg_role = await commands.RoleConverter().convert(ctx,succes_reg_role.content)
        except:
            await ctx.send(embed=inncorrect_role_mention)
# question 4
        q4 = discord.Embed(description = f'🛠️ Sweet! So I Will give This Role {fetched_succes_reg_role.mention} For Correct Registration \nQ4. How many total slots do you have? **Note: Maximum Nuber Of Slots Is `25`** ',color=self.bot.color)
        q4.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q4)
        try:
            total_num_slots = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)

        if total_num_slots.content == f'{ctx.prefix}cancel':
            return await ctx.send('Aborting.')
        if not total_num_slots.content.isdigit():
            return await ctx.send(f'{emote.error} | You Did Not Entered A Integer Please Try Agin By Running Same Command')
        
        int_converted_total_num_slots = int(total_num_slots.content)
        if int_converted_total_num_slots > 25:
            return await ctx.send(f'{emote.error} | You Entered Slots Number More Than `25` \n**Note: Maximum Nuber Of Slots Is `25`**')
# question 5
        q5 = discord.Embed(description = f'🛠️ Hmm! So I Will Only Accept {int_converted_total_num_slots}  No Of Registrations \nQ5 How many slots do you Want Too Keep Reserved If No Reserved Slots Reply With `0`',color=self.bot.color)
        q5.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q5)
        try:
            reserved_slots = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)

        if reserved_slots.content == f'{ctx.prefix}cancel':
            return await ctx.send('Aborting.')
        if not reserved_slots.content.isdigit():
            return await ctx.send(f'{emote.error} | You Did Not Entered A Integer Please Try Agin By Running Same Command')
        int_reserved_slots = int(reserved_slots.content)
        if int_reserved_slots > int_converted_total_num_slots:
            return await ctx.send(f'{emote.error} | You Entered Reserverd Slots Number More Than Total Slots It should be less than total number of slots')
# question 6
        q6 = discord.Embed(description = f'🛠️ Ok! So I Will Reserve {int_reserved_slots}  No Of Slots \nQ6. What are the minimum number of mentions for correct registration?',color=self.bot.color)
        q6.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q6)
        try:
            minimum_mentions_for_reg = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)

        if minimum_mentions_for_reg.content == f'{ctx.prefix}cancel':
            return await ctx.send('Aborting.')
        if not minimum_mentions_for_reg.content.isdigit():
            return await ctx.send(f'{emote.error} | You Did Not Entered A Integer Please Try Agin By Running Same Command')
        int_minimum_mentions_for_reg = int(minimum_mentions_for_reg.content)
# question 7
        q7 = discord.Embed(description = f'🛠️ Sweet! So I Will Only Accept Registration If There Will {int_minimum_mentions_for_reg}  No Of Mentions \nQ7. At What Time I Should Open Registration Please Write Time In 24 Hours Format EX:`15:00` And Bot Only Support IST Time Zone',color=self.bot.color)
        q7.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q7)
        try:
            reg_open_time = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)

        if reg_open_time.content == f'{ctx.prefix}cancel':
            return await ctx.send('Aborting.')
        match = re.match(r"\d+:\d+", reg_open_time.content)
        if not match:
            return await ctx.send(f'{emote.error} | Thats Not A Valid Time')
        match = match.group(0) 
        hour, minute = match.split(":")
        str_time = f'{hour}:{minute}'
        converting = datetime.strptime(str_time,'%H:%M')
        reg_open_final_time = converting.time()

# question 8
        q8 = discord.Embed(description = f'🛠️ Ok I Will Open Registration At `{reg_open_final_time}` IST \nQ8. what is the name you gave to these scrims?',color=self.bot.color)
        q8.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q8)
        try:
            custom_name = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)

        if custom_name.content == f'{ctx.prefix}cancel':
            return await ctx.send('Aborting.')
# finals
        allowed_slots = int_converted_total_num_slots - int_reserved_slots
        embed_final = discord.Embed(title = f'🛠️ Custom Setup 🛠️',color = self.bot.color)
        embed_final.add_field(name='Custom Name: ',value = f'{custom_name.content}')
        embed_final.add_field(name='Slot List Channel: ',value = f'{fetched_slot_channel.mention}')
        embed_final.add_field(name='Registration Channel: ',value = f'{fetched_reg_channel.mention}')
        embed_final.add_field(name='Succes Full Registration Role: ',value = f'{fetched_succes_reg_role.mention}')
        embed_final.add_field(name='Total No Of Slots: ',value = f'{int_converted_total_num_slots}')
        embed_final.add_field(name='Reserved Slots: ',value = f'{int_reserved_slots}')
        embed_final.add_field(name='Final Avaible Slots: ',value = f'{allowed_slots}')
        embed_final.add_field(name='Total No Of Mentions: ',value = f'{minimum_mentions_for_reg.content}')
        embed_final.add_field(name='Regsitration Open Time: ',value = f'{reg_open_final_time}')
        final_embed = await ctx.send(embed = embed_final)

        reactions = ['<:tick:820320509564551178>','<:xmark:820320509211574284>']
        def reactioncheck(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reactions

        for emoji in reactions:
            await final_embed.add_reaction(emoji)
        
        try:
            reaction,user = await self.bot.wait_for('reaction_add', timeout=80.0, check=reactioncheck)
        except asyncio.TimeoutError:
            await ctx.send(embed = took_long)
            await final_embed.delete()
            return

        if str(reaction.emoji) == '<:tick:820320509564551178>':
            final_changing_msg = await ctx.send(f'{emote.loading} | Setting Up Custom')
            async with ctx.db.acquire() as con:
                custom_num = scrims_manager['custom_setuped'] + 1
                await con.execute('''INSERT INTO smanager.custom_data (custom_num,
                guild_id,
                slotlist_ch,
                reg_ch,
                num_slots,
                reserverd_slots,
                num_correct_mentions,
                custom_title,
                correct_reg_role,
                open_time,
                allowed_slots) 
                VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)''',
                custom_num,ctx.guild.id,fetched_slot_channel.id,fetched_reg_channel.id,int_converted_total_num_slots,
                int_reserved_slots,int_minimum_mentions_for_reg,custom_name.content,
                fetched_succes_reg_role.id, reg_open_final_time,allowed_slots)
                await con.execute('UPDATE server_configs SET custom_setuped = $1 WHERE guild_id = $2',custom_num,ctx.guild.id)
                custom_id = await con.fetchval('SELECT c_id FROM smanager.custom_data WHERE reg_ch = $1',fetched_reg_channel.id)
                await final_changing_msg.edit(content=f'{emote.tick} | Successfully Setuped Custom ID = `{custom_id}`, Custom Number = `{custom_num}`')
        else:
            await final_embed.delete()
            await ctx.send('Aborting.')
            return

    @smanager.command(name='open')
    @commands.has_role('teabot-smanger')
    # @is_smanager_setuped()
    async def smanager_open(self,ctx,*,custom_id:int):
        """
        Manually Opens The Registration
        """
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')

        data = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)

        channel = await self.bot.db.fetchval('SELECT reg_ch FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not channel:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')

        if not data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')
        
        if data['is_registeration_done_today'] == True:
            return await ctx.send(f'{emote.error} | Registration For Today Is Already Completed')

        if data['is_running'] == True:
            return await ctx.send(f'{emote.error} | Registration Is Already Going On')
        
        self.bot.dispatch("reg_open",channel)

        await ctx.send(f'{emote.tick}')

    @smanager.command(name='close')
    @commands.has_role('teabot-smanger')
    # @is_smanager_setuped()
    async def smanager_close(self,ctx,*,custom_id:int):
        """
        Manually Closes The Rewgistration
        """
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')

        data = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)

        if not data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')
        
        if data['is_registeration_done_today'] == True:
            return await ctx.send(f'{emote.error} | Registration For Today Is Already Completed')
        else:
            if data['is_running'] == False:
                return await ctx.send(f'{emote.error} | Registration Has Not Opened Yet')
        channel = discord.utils.get(ctx.guild.channels, id=data['reg_ch'])
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        overwrite.view_channel = True
        try:
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        except:
            return await ctx.send(f'{emote.error} | I Don Not Have Manage channel permission')

        await channel.send(':lock: | **__Registration Is Closed Now.__**')
        self.bot.dispatch("reg_closed_logs",data['c_id'],data['custom_title'],data['custom_num'],data['guild_id'])
        self.bot.dispatch("reg_closed_db_update",data)
        await self.bot.db.execute('UPDATE smanager.custom_data SET  is_running = $1, is_registeration_done_today = $2 WHERE reg_ch = $3',False,True,data['reg_ch'])

        await ctx.send(f'{emote.tick}')

    @smanager.command(name='delete')
    @commands.has_role('teabot-smanger')
    # @is_smanager_setuped()
    async def smanager_delete(self,ctx,*,custom_id:int):
        """Deletes The Setuped Custom"""
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')

        channel = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not channel:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')

        confirmation = BotConfirmation(ctx, self.bot.color)
        await confirmation.confirm(f"Would you like to Delete Custom Info With Custom Id = `{custom_id}`")
        if confirmation.confirmed:
            custom_num = scrims_manager['custom_setuped'] - 1
            await self.bot.db.execute('DELETE FROM smanager.custom_data WHERE c_id = $1',custom_id)
            await self.bot.db.execute('UPDATE server_configs SET custom_setuped = $1 WHERE guild_id = $2',custom_num,ctx.guild.id)
            await confirmation.update(f"{emote.tick} | Successfull Deleted Custom Info With Custom Id = `{custom_id}`")
        else:
            return await confirmation.update(f"Not Confirmed", hide_author=True, color=self.bot.color)


    @smanager.command(name = 'toogle-custom')
    @commands.has_role('teabot-smanger')
    async def smanager_toggle_custom(self,ctx,custom_id:int):
        '''
        Toggle Scrims Manger Custom
        '''
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')
        data = await ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')
        
        if data['toggle'] == False:
            await ctx.db.execute('UPDATE smanager.custom_data SET toggle = $1 WHERE c_id = $2',True,custom_id)
            await ctx.send(f'{emote.tick} | Successfully enabled custom with id `{custom_id}`')
            return
        else:
            await ctx.db.execute('UPDATE smanager.custom_data SET toggle = $1 WHERE c_id = $2',False,custom_id)
            await ctx.send(f'{emote.tick} | Successfully disabled custom with id `{custom_id}`')
            return


    @smanager.command(name='edit-custom')
    # @is_smanager_setuped()
    @commands.has_role('teabot-smanger')
    async def smanager_edit_custom(self,ctx,*,custom_id:int):
        """Edit The Custom Data"""
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')
        
        custom_data = await ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not custom_data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')

        if custom_data['is_running'] == True:
            return await ctx.send(f'{emote.error} | Registration Is Going On')

        menu = CustomEditMenu(scrim=custom_data)
        await menu.start(ctx)

    #======= days editor ===========#
    @smanager.command(name='edit-day')
    # @is_smanager_setuped()
    @commands.has_role('teabot-smanger')
    async def smanager_edit_day(self,ctx,*,custom_id:int):
        """Edit The Custom Open Days"""
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')
        
        custom_data = await ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not custom_data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')

        menu = DaysEditorMenu(scrim=custom_data)
        await menu.start(ctx)


    @smanager.command(name='send-slotslist')
    @commands.has_role('teabot-smanger')
    # @is_smanager_setuped()
    async def smanager_send_slotslist(self,ctx,*,custom_id:int):
        """
        Send's The Slotlist To Setuped Channel
        """
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')

        custom_data = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1',custom_id)
        if not custom_data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')
        
        if custom_data['is_running'] == True:
            return await ctx.send(f'{emote.error} | Registration Is Going On')

        if custom_data['is_registeration_done_today'] == False:
            return await ctx.send(f'{emote.error} | Registration For Today Is Not Done')

        editable_message = await ctx.send(F'{emote.loading} | Generating Slotlist')
        slot_table = PrettyTable()
        slot_table.field_names = ["Slot No.", "Team Name"]
        slot_table.set_style(ORGMODE)
        slot_count = 1
        for message in custom_data['team_names']:
            slot_table.add_row([f"slot {slot_count}", f"{message}"])
            slot_count+=1

        embed = discord.Embed(title = f"Slotlist For {custom_data['custom_title']}",description = f'''```css\n{slot_table}\n```''',color = self.bot.color)
        await editable_message.edit(content = 'Here Is The Slotlist')
        final_embed = await ctx.send(embed = embed)
        reactions = ['<:tick:820320509564551178>','<:xmark:820320509211574284>']
        def reactioncheck(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reactions

        for emoji in reactions:
            await final_embed.add_reaction(emoji)
        
        try:
            reaction,user = await self.bot.wait_for('reaction_add', timeout=80.0, check=reactioncheck)
        except asyncio.TimeoutError:
            await ctx.send('Time Up')
            await final_embed.delete()
            return

        if str(reaction.emoji) == '<:tick:820320509564551178>':
            ch = self.bot.get_channel(custom_data['slotlist_ch'])
            await ch.send(embed= embed)
            await ctx.send(f'{emote.tick} | Done')
        else:
            await final_embed.delete()
            return

    @smanager.command(name='config')
    @commands.has_role('teabot-smanger')
    async def smanager_config(self,ctx):
        """See The Scrims Manager Configuration For This Server"""
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')

        allscrims = await ctx.db.fetch('SELECT * FROM smanager.custom_data WHERE guild_id = $1',ctx.guild.id)
        if not allscrims:
            return await ctx.send(f'{emote.error} | this server does not have any customs')

        if not len(allscrims):
            return await ctx.send(
                f"You do not have any scrims setup on this server.\n\nKindly use `{ctx.prefix}smanager setup` to setup one."
            )

        to_paginate = []
        for idx, scrim in enumerate(allscrims, start=1):
            ch = self.bot.get_channel(scrim['reg_ch'])
            slot_ch = self.bot.get_channel(scrim['slotlist_ch'])
            reg_channel = getattr(ch, "mention", "`Channel Deleted!`")
            slot_channel = getattr(slot_ch, "mention", "`Channel Deleted!`")
            role = discord.utils.get(ctx.guild.roles, id = scrim['correct_reg_role'])
            role = getattr(role, "mention", "`Role Deleted!`")
            open_time = (scrim['open_time']).strftime("%I:%M %p")
            mystring = f" Scrim ID: `{scrim['c_id']}`\n Name: `{scrim['custom_title']}`\n Registration Channel: {reg_channel}\n Slotlist Channel: {slot_channel}\n Role: {role}\n Mentions: `{scrim['num_correct_mentions']}`\n Total Slots: `{scrim['num_slots']}`\n Reserved Slots : `{scrim['reserverd_slots']}`\n Open Time: `{open_time}`\n Toggle: `{scrim['toggle']}`"

            to_paginate.append(f"**`<------ {idx:02d} ------>`**\n\n{mystring}\n")

        paginator = Pages(
            ctx, title="Total Custom Setuped: {}".format(len(to_paginate)), entries=to_paginate, per_page=1, show_entry_count=True
        )

        await paginator.paginate()
        


##############################################################################################################################
#================================================== Tag Check ===============================================================#
##############################################################################################################################
    
    @commands.group()
    async def tag_check(self,ctx):
        '''
        Sytem For Tag Check
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @tag_check.command(name = 'set')
    @commands.has_role('teabot-smanger')
    async def tag_check_set(self,ctx,check_channel:discord.TextChannel,*,mentions_required:int):
        '''
        Setups The Tag Check In You Server
        '''
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')

        data = await self.bot.db.fetchrow('SELECT * FROM smanager.tag_check WHERE guild_id = $1',ctx.guild.id)
        if not data:
            editable = await ctx.send(f'{emote.loading} | Setting Up Tag Check')
            await ctx.db.execute('INSERT INTO smanager.tag_check (guild_id,ch_id,toggle,mentions_required) VALUES($1,$2,$3,$4)',ctx.guild.id,check_channel.id,True,mentions_required)
            await editable.edit(content = f'{emote.tick} | successfully setuped tag check in {check_channel.mention}')
            return
        editable = await ctx.send(f'{emote.loading} | Setting Up Tag Check')
        await ctx.db.execute('UPDATE smanager.tag_check SET ch_id=$1,toggle = $2,mentions_required = $3 WHERE guild_id = $4',check_channel.id,True,mentions_required,ctx.guild.id)
        await editable.edit(content = f'{emote.tick} | successfully setuped tag check in {check_channel.mention}')

    @tag_check.command(name = 'toggle')
    @commands.has_role('teabot-smanger')
    async def tag_check_toggle(self,ctx):
        '''
        Toggles This Tag Check
        '''
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            return await ctx.send(f'{emote.error} | This Server Does Not Have Scrims Managers Setup')

        data = await self.bot.db.fetchrow('SELECT * FROM smanager.tag_check WHERE guild_id = $1',ctx.guild.id)
        if not data:
            return await ctx.send(f'{emote.error} | This Server Does Not Scrims Manager Setuped')
        if data['toggle'] == False:
            await ctx.db.execute('UPDATE smanager.tag_check SET toggle = $1 WHERE guild_id = $2',True,ctx.guild.id)
            await ctx.send(f'{emote.tick} | Successfully enabled tag check')
            return
        await ctx.db.execute('UPDATE smanager.tag_check SET toggle = $1 WHERE guild_id = $2',False,ctx.guild.id)
        await ctx.send(f'{emote.tick} | Successfully disabled tag check')



####################################################################################################################
#===================================================== Tournamwnt manager =========================================#
####################################################################################################################

def setup(bot):
    bot.add_cog(SManager(bot))
    bot.add_cog(SmanagerListeners(bot))
    bot.add_cog(SmanagerTasks(bot))
    bot.add_cog(TagCheckListners(bot))
