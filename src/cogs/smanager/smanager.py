import discord,re,json,asyncio
from discord.ext import commands
from ..utils import emote
from .sutils import CustomEditMenu,DaysEditorMenu,delete_denied_message
from ..utils.paginitators import Pages
from prettytable import PrettyTable,ORGMODE
from datetime import datetime
from disputils import  BotConfirmation
from .events import EsportsListners
from ..utils import expectations
from pytz import timezone



class Esports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group(invoke_without_command = True,aliases = ['s','sm','scirms-manager'])
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
            raise expectations.NotSetup
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
            raise expectations.ScrimsManagerNotSetup

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
        else:
            if slot_channel.content == f'{ctx.prefix}cancel':
                return await ctx.send('Aborting.')
            if len(slot_channel.channel_mentions) == 0 or len(slot_channel.channel_mentions) > 1:
                return await ctx.send(embed= inncorrect_channel_mention)
            try:
                fetched_slot_channel = await commands.TextChannelConverter().convert(ctx,slot_channel.content)
            except:
                return await ctx.send(embed= inncorrect_channel_mention)
            else:
                if not fetched_slot_channel.permissions_for(ctx.me).read_messages:
                    await ctx.error(
                    f"Unfortunately, I don't have read messages permissions in {fetched_slot_channel.mention}."
                    )
                    return
            
                if not fetched_slot_channel.permissions_for(ctx.me).send_messages:
                    await ctx.error(
                    f"Unfortunately, I don't have send messages permissions in {fetched_slot_channel.mention}."
                    )

                    return

# question 2
        q2 = discord.Embed(description = f'🛠️ Sweet! Slotlist Will Be Uploaded In {fetched_slot_channel.mention} \nQ2. What Should Be The Registration Channel Where I WIll Accept Registration?',color=self.bot.color)
        q2.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed = q2)
        try:
            reg_channel = await self.bot.wait_for('message', timeout=80.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(embed = took_long)
        else:

            if reg_channel.content == f'{ctx.prefix}cancel':
                return await ctx.send('Aborting.')
            if len(reg_channel.channel_mentions) == 0 or len(reg_channel.channel_mentions) > 1:
                return await ctx.send(embed= inncorrect_channel_mention)
            try:
                fetched_reg_channel = await commands.TextChannelConverter().convert(ctx,reg_channel.content)
            except:
                return await ctx.send(embed= inncorrect_channel_mention)
            else:
                if not fetched_reg_channel.permissions_for(ctx.me).read_messages:
                    await ctx.error(
                    f"Unfortunately, I don't have read messages permissions in {fetched_reg_channel.mention}."
                    )
                    return
            
                if not fetched_reg_channel.permissions_for(ctx.me).send_messages:
                    await ctx.error(
                    f"Unfortunately, I don't have send messages permissions in {fetched_reg_channel.mention}."
                    )

                    return
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
            return await ctx.error(embed=inncorrect_role_mention)
        else:
            if fetched_succes_reg_role.managed:
                return await ctx.error(f"Role is an integrated role and cannot be added manually.")
            if fetched_succes_reg_role > ctx.me.top_role:
                await ctx.error(
                    f"The position of {fetched_succes_reg_role.mention} is above my top role. So I can't give it to anyone.\nKindly move {ctx.me.top_role.mention} above {fetched_succes_reg_role.mention} in Server Settings."
                )
                self.stop()
                return

            if ctx.author.id != ctx.guild.owner_id:
                if fetched_succes_reg_role > ctx.author.top_role:
                    await ctx.error(
                        f"The position of {fetched_succes_reg_role.mention} is above your top role {ctx.author.top_role.mention}."
                    )
                    self.stop()
                    return
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
                is_registration_done_today = False
                if reg_open_final_time <= datetime.now(timezone("Asia/Kolkata")).time():
                    is_registration_done_today = True
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
                is_registeration_done_today,
                allowed_slots) 
                VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)''',
                custom_num,ctx.guild.id,fetched_slot_channel.id,fetched_reg_channel.id,int_converted_total_num_slots,
                int_reserved_slots,int_minimum_mentions_for_reg,custom_name.content,
                fetched_succes_reg_role.id, reg_open_final_time,is_registration_done_today,allowed_slots)
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
            raise expectations.ScrimsManagerNotSetup

        data = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')
            
        if data['toggle'] == False:
            return await ctx.error(f'The Scrims Is Toggled Of So You Can Not Execute This Command')

        channel = data['reg_ch']

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
            raise expectations.ScrimsManagerNotSetup

        data = await self.bot.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)

        if not data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')
            
        if data['toggle'] == False:
            return await ctx.error(f'The Scrims Is Toggled Of So You Can Not Execute This Command')

        if data['is_registeration_done_today'] == True:
            return await ctx.send(f'{emote.error} | Registration For Today Is Already Completed')
        else:pass

        if data['is_running'] == False:
            return await ctx.send(f'{emote.error} | Registration Has Not Opened Yet')

        self.bot.dispatch("auto_close_reg",data['reg_ch'])
        await self.bot.db.execute('UPDATE smanager.custom_data SET  is_running = $1, is_registeration_done_today = $2 WHERE reg_ch = $3',False,True,data['reg_ch'])

        await ctx.send(f'{emote.tick}')

    @smanager.command(name='delete')
    @commands.has_role('teabot-smanger')
    # @is_smanager_setuped()
    async def smanager_delete(self,ctx,*,custom_id:int):
        """Deletes The Setuped Custom"""
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            raise expectations.ScrimsManagerNotSetup
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
            raise expectations.ScrimsManagerNotSetup
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
            raise expectations.ScrimsManagerNotSetup
        
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
            raise expectations.ScrimsManagerNotSetup
        
        custom_data = await ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not custom_data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')

        menu = DaysEditorMenu(scrim=custom_data)
        await menu.start(ctx)
    #======= open-message editor ===========#
    @smanager.command(name='edit-open-message')
    @commands.has_role('teabot-smanger')
    async def smanager_edit_open_message(self,ctx,*,custom_id:int):
        """Edits The Custom Open Message"""
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            raise expectations.ScrimsManagerNotSetup
        
        custom_data = await ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not custom_data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')
        
        embed = discord.Embed(title = f'Edit Open Message For Custom: `{custom_data["c_id"]}`',description = f'''You Will Get 5 Minutes To Make Your Embed Kindly [Click Here](https://embedbuilder.nadekobot.me/) To Create Your Embed\n\n**You Can Use These Variables In You Message:**\n
> 1. `<<available_slots>>` = to get available slots to registration
> 2. `<<reserved_slots>>` = to get count of reserved slots
> 3. `<<total_slots>>` = to get total slots
> 4. `<<custom_title>>` = to get scrims name
> 5. `<<mentions_required>>` = Mentions Required\n\n**Your Message Should Not Break These Rules:**\n
> 1.Embed titles are limited to 190 characters
> 2.Embed descriptions are limited to 1900 characters
> 3.There can be up to 5 fields
> 4.A field's name is limited to 100 characters and its value to 900 characters
> 5.The footer text is limited to 1900 characters
> 6.The author name is limited to 190 characters
> 7.The sum of all characters in an embed structure must not exceed 6000 characters\n\n**Note:**\n
> 1. You Should Follow Those Rulles Otherwies Your Message Won't Be Accpeted
> 2. You Will Have To Answer In 5 Minutes Otherwise You Will Have To Send The Command Again Or Keep Your Embed Ready Firstly Then Use The Command
> 3. You Can Use `[name](link)` for links to make it look cool like this: [click here](https://embedbuilder.nadekobot.me/)
> 4. Mention Meber Or role Like This `<@id>` Replace id with Mebmer,role id's **This Can Only Be Used In Description or field value**
> 5. Mention Channel Like This `<#id>` Replace Id With Channel id **This Can Only Be Used In Description or field value**
> 6. You Should Not Use Simple Text In Embed Builder.
        ''',color = self.bot.color)
        embed.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed=embed)
        def check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        try:
            message = await self.bot.wait_for('message', timeout=300.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.error('You Took Too Long Kindly Try Again')
        else:
            if message.content == f'{ctx.prefix}cancel':
                return await ctx.send('Aborting.')
            if message.content.startswith('{') and message.content.endswith('}'):
                msg = await ctx.send(f'{emote.loading} | Checking Your Inputed Data')
                embed = json.loads(message.content)
                if "title" in message.content:
                    if len(embed['title']) > 190:
                        await msg.delete()
                        return await ctx.error('Title Is So Long')
                if "description" in message.content:
                    if len(embed['description']) > 1900:
                        await msg.delete()
                        return await ctx.error('Description Is So Long')
                if "footer" in message.content:
                    if len(embed['footer']['text']) > 1900:
                        await msg.delete()
                        return await ctx.error('Footer Is So Long')
                if "author" in message.content:
                    if len(embed['author']['name'])>190:
                        await msg.delete()
                        return await ctx.send('Author Is So Long')
                if "fields" in message.content:
                    fields_count = 0
                    for items in embed['fields']:
                        if len(items['name']) > 100 or len(items['name']) == 0:
                            await msg.delete()
                            return await ctx.error('You One Of The Field Title Is Wrong')
                        if len(items['value']) > 900 or len(items['value']) == 0:
                            await msg.delete()
                            return await ctx.error('You One Of The Field Value Is Wrong')
                        fields_count += 1
                    if fields_count > 5:
                        await msg.delete()
                        return await ctx.error(f'You Have Given Fields More Than 5')
                if "plainText" in message.content:
                    return await ctx.send('You Have Breaked One Of The Rules')

                messageto_embeded = message.content
                messageto_embeded = messageto_embeded.replace('<<available_slots>>',f"{custom_data['allowed_slots']}")
                messageto_embeded = messageto_embeded.replace('<<reserved_slots>>',f"{custom_data['reserverd_slots']}")
                messageto_embeded = messageto_embeded.replace('<<total_slots>>',f"{custom_data['num_slots']}")
                messageto_embeded = messageto_embeded.replace('<<custom_title>>',f"{custom_data['custom_title']}")
                messageto_embeded = messageto_embeded.replace('<<mentions_required>>',f"{custom_data['num_correct_mentions']}")
                finalmessageto_embeded = json.loads(messageto_embeded)
                final_embed = discord.Embed.from_dict(finalmessageto_embeded)
                await msg.delete()
                reaction_message = await ctx.send(embed = final_embed)
                reactions = ['<:tick:820320509564551178>','<:xmark:820320509211574284>']
                def reactioncheck(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in reactions
                for emoji in reactions:
                    await reaction_message.add_reaction(emoji)
                    
                try:
                    reaction,user = await self.bot.wait_for('reaction_add', timeout=80.0, check=reactioncheck)
                except asyncio.TimeoutError:
                    await ctx.error('Time Up')
                    await reaction_message.delete()
                    return
                else:
                    if str(reaction.emoji) == '<:tick:820320509564551178>':
                        ch = self.bot.get_channel(custom_data['slotlist_ch'])
                        await ctx.db.execute('UPDATE smanager.custom_data SET open_message_embed = $1 WHERE c_id = $2',message.content,custom_id)
                        await ctx.send(f'{emote.tick} | Done')
                    else:
                        await ctx.error('aborting')
                        await reaction_message.delete()
                        return
            else:
                return await ctx.error('Thats Not A Valid Embed')
            

    #======= close-message editor ===========#
    @smanager.command(name='edit-close-message')
    @commands.has_role('teabot-smanger')
    async def smanager_edit_close_message(self,ctx,*,custom_id:int):
        """Edits The Custom Close Message"""
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            raise expectations.ScrimsManagerNotSetup
        custom_data = await ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1 AND guild_id = $2',custom_id,ctx.guild.id)
        if not custom_data:
            return await ctx.send(f'{emote.error} | Thats Not Correct Custom ID, To Get Valid Custom ID Use `{ctx.prefix}smanager config`')
        embed = discord.Embed(title = f'Edit Open Message For Custom: `{custom_data["c_id"]}`',description = f'''You Will Get 5 Minutes To Make Your Embed Kindly [Click Here](https://embedbuilder.nadekobot.me/) To Create Your Embed\n\n**Your Message Should Not Break These Rules:**\n
> 1.Embed titles are limited to 190 characters
> 2.Embed descriptions are limited to 1900 characters
> 3.There can be up to 5 fields
> 4.A field's name is limited to 100 characters and its value to 900 characters
> 5.The footer text is limited to 1900 characters
> 6.The author name is limited to 190 characters
> 7.The sum of all characters in an embed structure must not exceed 6000 characters\n\n**Note:**\n
> 1. You Should Follow Those Rulles Otherwies Your Message Won't Be Accpeted
> 2. You Will Have To Answer In 5 Minutes Otherwise You Will Have To Send The Command Again Or Keep Your Embed Ready Firstly Then Use The Command
> 3. You Can Use `[name](link)` for links to make it look cool like this: [click here](https://embedbuilder.nadekobot.me/)
> 4. Mention Meber Or role Like This `<@id>` Replace id with Mebmer,role id's **This Can Only Be Used In Description or field value**
> 5. Mention Channel Like This `<#id>` Replace Id With Channel id **This Can Only Be Used In Description or field value**
> 6. You Should Not Use Simple Text In Embed Builder.
        ''',color = self.bot.color)
        embed.set_footer(text = f'**Type `{ctx.prefix}cancel` To Cancel Setup Any Time**')
        await ctx.send(embed=embed)
        def check(msg):
            return msg.author == ctx.author and ctx.channel == msg.channel

        try:
            message = await self.bot.wait_for('message', timeout=300.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.error('You Took Too Long Kindly Try Again')
        else:
            if message.content == f'{ctx.prefix}cancel':
                return await ctx.send('Aborting.')
            if message.content.startswith('{') and message.content.endswith('}'):
                msg = await ctx.send(f'{emote.loading} | Checking Your Inputed Data')
                embed = json.loads(message.content)
                if "title" in message.content:
                    if len(embed['title']) > 190:
                        await msg.delete()
                        return await ctx.error('Title Is So Long')
                if "description" in message.content:
                    if len(embed['description']) > 1900:
                        await msg.delete()
                        return await ctx.error('Description Is So Long')
                if "footer" in message.content:
                    if len(embed['footer']['text']) > 1900:
                        await msg.delete()
                        return await ctx.error('Footer Is So Long')
                if "author" in message.content:
                    await msg.delete()
                    if len(embed['author']['name'])>190:
                        await msg.delete()
                        return await ctx.send('Author Is So Long')
                if "fields" in message.content:
                    fields_count = 0
                    for items in embed['fields']:
                        if len(items['name']) > 100 or len(items['name']) == 0:
                            await msg.delete()
                            return await ctx.error('You One Of The Field Title Is Wrong')
                        if len(items['value']) > 900 or len(items['value']) == 0:
                            await msg.delete()
                            return await ctx.error('You One Of The Field Value Is Wrong')
                        fields_count += 1
                    if fields_count > 5:
                        await msg.delete()
                        return await ctx.error(f'You Have Given Fields More Than 5')
                if "plainText" in message.content:
                    await msg.delete()
                    return await ctx.send('You Have Breaked One Of The Rules')
                final_embed = discord.Embed.from_dict(embed)
                await msg.delete()
                reaction_message = await ctx.send(embed = final_embed)
                reactions = ['<:tick:820320509564551178>','<:xmark:820320509211574284>']
                def reactioncheck(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in reactions
                for emoji in reactions:
                    await reaction_message.add_reaction(emoji)
                    
                try:
                    reaction,user = await self.bot.wait_for('reaction_add', timeout=80.0, check=reactioncheck)
                except asyncio.TimeoutError:
                    await ctx.error('Time Up')
                    await reaction_message.delete()
                    return
                else:
                    if str(reaction.emoji) == '<:tick:820320509564551178>':
                        ch = self.bot.get_channel(custom_data['slotlist_ch'])
                        await ctx.db.execute('UPDATE smanager.custom_data SET close_message_embed = $1 WHERE c_id = $2',message.content,custom_id)
                        await ctx.send(f'{emote.tick} | Done')
                    else:
                        await ctx.error('aborting')
                        await reaction_message.delete()
                        return
    #======= slotlist-embed-format ===========#
    # @smanager.command(name='edit-slotlist-embed-format')
    # @commands.has_role('teabot-smanger')
    # async def smanager_edit_slotlist_embed_format(self,ctx,*,custom_id:int):
    #     """Edits The Custom Slotlist Format"""
    #     #TODO Complete This
    #     scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
    #     if scrims_manager['scrims_manager'] == False:
    #         raise expectations.ScrimsManagerNotSetup

    #     embed = discord.Embed(title = f'',description = f'''  ''',color = self.bot.color)
    #     await ctx.send(embed=embed)


    @smanager.command(name='send-slotslist')
    @commands.has_role('teabot-smanger')
    async def smanager_send_slotslist(self,ctx,*,custom_id:int):
        """
        Send's The Slotlist To Setuped Channel
        """
        scrims_manager = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1',ctx.guild.id)
        if scrims_manager['scrims_manager'] == False:
            raise expectations.ScrimsManagerNotSetup

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
            raise expectations.ScrimsManagerNotSetup

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
            _role = getattr(role, "mention", "`Role Deleted!`")
            open_time = (scrim['open_time']).strftime("%I:%M %p")
            if scrim['close_time'] != None:
                close_time = (scrim['close_time']).strftime("%I:%M %p")
            ping_role = discord.utils.get(ctx.guild.roles, id = scrim['ping_role'])
            _ping_role = getattr(ping_role, "mention", "`None`")
            open_role = discord.utils.get(ctx.guild.roles, id = scrim['open_role'])
            _open_role = getattr(open_role, "mention", "`None`")



            mystring = f""" Scrim ID: `{scrim['c_id']}`\n 
            Name: `{scrim['custom_title']}`\n 
            Registration Channel: {reg_channel}\n 
            Slotlist Channel: {slot_channel}\n 
            Role: {_role}\n 
            Ping Role: {_ping_role}\n 
            Open Role: {_open_role}\n 
            Mentions: `{scrim['num_correct_mentions']}`\n 
            Total Slots: `{scrim['num_slots']}`\n 
            Reserved Slots : `{scrim['reserverd_slots']}`\n 
            Avaible Slots For Registration : `{scrim['allowed_slots']}`\n
            Open Time: `{open_time}`\n 
            Close Time: `{close_time}`\n 
            Toggle: `{scrim['toggle']}`"""

            to_paginate.append(f"**`<------ {idx:02d} ------>`**\n\n{mystring}\n")

        paginator = Pages(
            ctx, title="Total Custom Setuped: {}".format(len(to_paginate)), entries=to_paginate, per_page=1, show_entry_count=True
        )

        await paginator.paginate()
        


##############################################################################################################################
#================================================== Tag Check ===============================================================#
##############################################################################################################################
    
    @commands.group(aliases = ['tag-check','tgcheck','tg-check'])
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
            raise expectations.ScrimsManagerNotSetup

        data = await self.bot.db.fetchrow('SELECT * FROM smanager.tag_check WHERE guild_id = $1',ctx.guild.id)
        editable = await ctx.send(f'{emote.loading} | Setting Up Tag Check')
        if not data:
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
            raise expectations.ScrimsManagerNotSetup

        data = await self.bot.db.fetchrow('SELECT * FROM smanager.tag_check WHERE guild_id = $1',ctx.guild.id)
        if not data:
            return await ctx.send(f'{emote.error} | This Server Does Not Tag Check Setuped')
        if data['toggle'] == False:
            await ctx.db.execute('UPDATE smanager.tag_check SET toggle = $1 WHERE guild_id = $2',True,ctx.guild.id)
            await ctx.send(f'{emote.tick} | Successfully enabled tag check')
            return
        await ctx.db.execute('UPDATE smanager.tag_check SET toggle = $1 WHERE guild_id = $2',False,ctx.guild.id)
        await ctx.send(f'{emote.tick} | Successfully disabled tag check')



####################################################################################################################
#===================================================== Other Commnads =============================================#
####################################################################################################################

    @commands.command(aliases=("idp",)) 
    @commands.bot_has_permissions(embed_links=True, manage_messages=True)
    async def shareidp(self, ctx, room_id, room_password, map,ping_role: discord.Role = None):
        """
        Share Id/pass with embed.
        Message is automatically deleted after 30 minutes.
        """
        await ctx.message.delete()
        embed = discord.Embed(title=f"Custom Room. JOIN NOW!",color=self.bot.color)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Room ID:", value=room_id,inline=False)
        embed.add_field(name="Room Password:", value=room_password,inline=False)
        embed.add_field(name="Map:", value=map,inline=False)
        embed.set_footer(text=f"IDP Shared by: {ctx.author} | Auto delete in 30 minutes.", icon_url=ctx.author.avatar_url)
        msg = await ctx.send(
            content=ping_role.mention if ping_role else None,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True),
        )

        self.bot.loop.create_task(delete_denied_message(msg, 30 * 60))

####################################################################################################################
#======================================================== Easy Tagging ============================================#
####################################################################################################################

    @commands.group(invoke_without_command = True,aliases = ['ez_tag','eztag','ez-tag','etag'])
    async def easytag(self,ctx):
        """
        Handles Easy Tagging In Your Server
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @easytag.command(name = 'set')
    @commands.has_permissions(manage_guild = True)
    async def easytag_set(self,ctx,channel:discord.TextChannel):
        """
        Setups Easy tagging In Your Server
        """
        data = await self.bot.db.fetchrow('SELECT * FROM smanager.ez_tag WHERE guild_id = $1',ctx.guild.id)
        editable = await ctx.send(f'{emote.loading} | Setting Up Easy Tag')
        em = discord.Embed(title = "**__Tea Bot Easy Tagging__**",color = self.bot.color)
        em.description = f"""
            Unable to mention team mates while registering in scrims? Do not worry, we are here to help! Mention your team mates below and get their ID.\n\nUse the ID you get below in your registration format. This ID will tag yourteam mates and your registration will be successfully every single time.\n\nYou have 10 seconds to copy the ID
        """
        if not data:
            await ctx.db.execute('INSERT INTO smanager.ez_tag (guild_id,ch_id) VALUES($1,$2)',ctx.guild.id,channel.id)
            final_embed = await channel.send(embed = em)
            await final_embed.pin(reason = 'bcs its important')
            await editable.edit(content = f'{emote.tick} | successfully setuped easy tag in {channel.mention}')
            return
        await ctx.db.execute('UPDATE smanager.ez_tag SET ch_id=$1, WHERE guild_id = $2',channel.id,ctx.guild.id)
        final_embed = await channel.send(embed = em)
        await final_embed.pin(reason = 'bcs its important')
        await editable.edit(content = f'{emote.tick} | successfully setuped easy tag in {channel.mention}')

    @easytag.command(name = 'toggle')
    @commands.has_permissions(manage_guild = True)
    async def easytag_toggle(self,ctx):
        """Toggles Easy Tagging In Server"""
        data = await self.bot.db.fetchrow('SELECT * FROM smanager.ez_tag WHERE guild_id = $1',ctx.guild.id)
        if not data:
            return await ctx.error('You Do Not Easy Tag Setuped') 
        if data['toggle'] == False:
            await ctx.db.execute('UPDATE smanager.ez_tag SET toggle = $1 WHERE guild_id = $2',True,ctx.guild.id)
            return await ctx.success('Successfully Turned On Easy Tagging')
        else:
            await ctx.db.execute('UPDATE smanager.ez_tag SET toggle = $1 WHERE guild_id = $2',False,ctx.guild.id)
            return await ctx.success('Successfully Turned Off Easy Tagging')



####################################################################################################################
#===================================================== Tournament Manager =========================================#
####################################################################################################################



def setup(bot):
    bot.add_cog(Esports(bot))
    bot.add_cog(EsportsListners(bot))
