import asyncio
import re
from discord.ext import commands, menus
import discord
import string
from ..utils import inputs,emote
from datetime import datetime
# import datetime
from discord.ext.commands.converter import RoleConverter, TextChannelConverter

class ScrimError(commands.CommandError):
    pass



class CustomEditMenu(menus.Menu):
    def __init__(self,*, scrim):
        super().__init__(
            timeout=120,
            delete_message_after=False,
            clear_reactions_after=True,
        )
        self.scrim = scrim
        self.check = (
            lambda msg: msg.channel == self.ctx.channel
            and msg.author == self.ctx.author
        )

    def initial_embed(self):
        scrim = self.scrim
        fetched_slot_channel = self.bot.get_channel(scrim['slotlist_ch'])
        slotlist_channel = getattr(
            fetched_slot_channel, "mention", "`Channel Deleted!`"
        )#
        fetched_reg_ch = self.bot.get_channel(scrim['reg_ch'])
        registration_channel = getattr(
            fetched_reg_ch, "mention", "`Channel Deleted!`"
        )#,

        guild = self.bot.get_guild(scrim['guild_id'])
        role = discord.utils.get(guild.roles, id = scrim['correct_reg_role'])
        scrim_role = getattr(
            role, "mention", "`Role Deleted!`"
            )#

        open_time = (scrim['open_time']).strftime("%I:%M %p")

        embed = discord.Embed(color=discord.Color.green())
        embed.title = f"Edit Scrims Configuration: {scrim['c_id']}"
        def reactions(str):
            data = scrim[f'{str}']
            if data == True:
                return f'{emote.switch_on}'
            else:
                return f'{emote.switch_off}'

        fields = {
            "Custom Name": f"`{scrim['custom_title']}`",
            "Registration Channel": registration_channel,
            "Slotlist Channel": slotlist_channel,
            "Role": scrim_role,
            "Mentions": f"`{scrim['num_correct_mentions']:,}`",
            "Slots": f"`{scrim['num_slots']:,}`",
            "Open Time": f"`{open_time}`",
            "Reserved Slots": f"`{scrim['reserverd_slots']}`",
            "Auto Clean":  f"{reactions('auto_clean')}",
            "Auto Slotlist Send":  f"{reactions('auto_slot_list_send')}"
        }

        for idx, (name, value) in enumerate(fields.items()):
            embed.add_field(
                name=f"{emote.regional_indicator(string.ascii_uppercase[idx])} {name}:",
                value=value,
            )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        return embed

    async def cembed(self, description):
        return await self.ctx.send(
            embed=discord.Embed(
                color=discord.Color.green(),
                title=f"🛠️ Scrims Manager",
                description=description,
            )
        )

    async def send_initial_message(self, ctx, channel):
        return await channel.send(embed=self.initial_embed())

    async def refresh(self):
        self.scrim = await self.ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1',self.scrim['c_id'])
        await self.message.edit(embed=self.initial_embed())
    async def refresh_db(self):
        self.scrim = await self.ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1',self.scrim['c_id'])
        # await self.message.edit(embed=self.initial_embed())

    # async def update_scrim(self, **kwargs):
    #     await Scrim.filter(pk=self.scrim['c_id']).update(**kwargs)
    #     await self.refresh()

    @menus.button(emote.regional_indicator('A'))
    async def change_scrim_name(self, payload):
        msg = await self.cembed(
            "What is the new name you gave to give to these scrims?"
        )
        # name = await inputs.string_input(
        #     self.ctx,
        #     self.check,
        #     delete_after=True,
        # )
        try:
            name = await self.ctx.bot.wait_for("message", check=self.check, timeout=120)
        except asyncio.TimeoutError:
            await self.ctx.send(f"{emote.error} | You failed to select a title in time. Try again!")
            self.stop()
            return 
        # if len(name) > 30:
        #     raise ScrimError("Scrims Name cannot exceed 30 characters.")
        # elif len(name) < 5:
        #     raise ScrimError("The length of new name is too short.")

        await inputs.safe_delete(msg)
        await inputs.safe_delete(name)
        await self.refresh_db()
        await self.ctx.db.execute('UPDATE smanager.custom_data SET custom_title = $1 WHERE c_id = $2',name.content,self.scrim['c_id'])
        await self.refresh()
        # await self.update_scrim(name=name)

    @menus.button(emote.regional_indicator('B'))
    async def change_registration_channel(self, payload):
        msg = await self.cembed("Which is the new channel for registrations?")
        # channel = await inputs.channel_input(
        #     self.ctx,
        #     self.check,
        #     delete_after=True,
        # )
        try:
            channel = await self.ctx.bot.wait_for("message", check=self.check, timeout=120)
        except asyncio.TimeoutError:
            await self.ctx.send(f"{emote.error} | You failed to select a channel in time. Try again!")
            self.stop()
            return 

        else:
            if len(channel.channel_mentions) == 0:
                await self.ctx.send(f'{emote.error} | Thats Not A Channel')
                self.stop()
                return 

            try:
                converted_channel = await TextChannelConverter().convert(self.ctx, channel.content)
            except:
                await self.ctx.send(f'{emote.error} | Thats Not A Channel')
                self.stop()
                return 

            if not converted_channel.permissions_for(self.ctx.me).read_messages:
                await self.ctx.send(
                f"{emote.error} | Unfortunately, I don't have read messages permissions in {channel.mention}."
                )
                self.stop()
                return
            
            if not converted_channel.permissions_for(self.ctx.me).send_messages:
                await self.ctx.send(
                f"{emote.error} | Unfortunately, I don't have send messages permissions in {channel.mention}."
                )
                self.stop()
                return

        await inputs.safe_delete(msg)
        await inputs.safe_delete(channel)
        await self.refresh_db()
        await self.ctx.db.execute('UPDATE smanager.custom_data SET reg_ch = $1 WHERE c_id = $2',converted_channel.id,self.scrim['c_id'])
        await self.refresh()
        # await self.update_scrim(registration_channel_id=channel.id)

    @menus.button(emote.regional_indicator('C'))
    async def change_slotlist_channel(self, payload):
        msg = await self.cembed("Which is the new channel for slotlists?")
        try:
            channel = await self.ctx.bot.wait_for("message", check=self.check, timeout=120)
            
        except asyncio.TimeoutError:
            await self.ctx.send(f"{emote.error} | You failed to select a channel in time. Try again!")
            self.stop()
            return 

        else:
            if len(channel.channel_mentions) == 0:
                await self.ctx.send(f'{emote.error} | Thats Not A Channel')
                self.stop()
                return 

            try:
                converted_channel = await TextChannelConverter().convert(self.ctx, channel.content)
            except:
                await self.ctx.send(f'{emote.error} | Thats Not A Channel')
                self.stop()
                return 

            if not converted_channel.permissions_for(self.ctx.me).read_messages:
                await self.ctx.send(
                f"{emote.error} | Unfortunately, I don't have read messages permissions in {channel.mention}."
                )
                self.stop()
                return
            
            if not converted_channel.permissions_for(self.ctx.me).send_messages:
                await self.ctx.send(
                f"{emote.error} | Unfortunately, I don't have send messages permissions in {channel.mention}."
                )
                self.stop()
                return

        await inputs.safe_delete(msg)
        await inputs.safe_delete(channel)
        await self.refresh_db()
        await self.ctx.db.execute('UPDATE smanager.custom_data SET slotlist_ch = $1 WHERE c_id = $2',converted_channel.id,self.scrim['c_id'])
        await self.refresh()
        # await self.update_scrim(slotlist_channel_id=channel.id)

    @menus.button(emote.regional_indicator('D'))
    async def change_scrim_role(self, payload):
        msg = await self.cembed("Which is the new role for correct registration?")
        # role = await inputs.role_input(
        #     self.ctx,
        #     self.check,
        #     delete_after=True,
        # )
        try:
            role = await self.ctx.bot.wait_for("message", check=self.check, timeout=120)
        except asyncio.TimeoutError:
            await self.ctx.send(f"{emote.error} | You failed to select a role in time. Try again!")
            self.stop()
            return

        else:
            if len(role.role_mentions) == 0:
                await self.ctx.send(f'{emote.error} | Thats Not A Role')
                self.stop()
                return
            try:
                converted_role = await RoleConverter().convert(self.ctx, role.content)
            except:
                await self.ctx.send(f'{emote.error} | Thats Not A Role')
                self.stop()
                return

            if converted_role > self.ctx.me.top_role:
                await self.ctx.send(
                    f"{emote.error} | The position of {converted_role.mention} is above my top role. So I can't give it to anyone.\nKindly move {self.ctx.me.top_role.mention} above {converted_role.mention} in Server Settings."
                )
                self.stop()
                return

            if self.ctx.author.id != self.ctx.guild.owner_id:
                if converted_role > self.ctx.author.top_role:
                    await self.ctx.send(
                        f"{emote.error} | The position of {converted_role.mention} is above your top role {self.ctx.author.top_role.mention}."
                    )
                    self.stop()
                    return
        await inputs.safe_delete(msg)
        await inputs.safe_delete(role)
        await self.refresh_db()
        await self.ctx.db.execute('UPDATE smanager.custom_data SET correct_reg_role = $1 WHERE c_id = $2',converted_role.id,self.scrim['c_id'])
        await self.refresh()
        # await self.update_scrim(role_id=role.id)

    @menus.button(emote.regional_indicator('E'))
    async def change_required_mentions(self, payload):
        msg = await self.cembed(
            "How many mentions are required for successful registration?"
        )
        # mentions = await inputs.integer_input(
        #     self.ctx,
        #     self.check,
        #     delete_after=True,
        #     limits=(0, 10),
        # )
        try:
            mentions = await self.bot.wait_for('message', timeout=120, check=self.check)
        except asyncio.TimeoutError:
            await self.ctx.send(f"{emote.error} | You failed to select number of mentions requried in time. Try again!")
            self.stop()
            return

        if not mentions.content.isdigit():
            await self.ctx.send(f'{emote.error} | You Did Not Entered A Integer Please Try Agin By Running Same Command')
            self.stop()
            return
        int_mentions = int(mentions.content)
        await inputs.safe_delete(msg)
        await inputs.safe_delete(mentions)
        await self.refresh_db()
        await self.ctx.db.execute('UPDATE smanager.custom_data SET num_correct_mentions = $1 WHERE c_id = $2',int_mentions,self.scrim['c_id'])
        await self.refresh()
        # await self.update_scrim(required_mentions=mentions)

    @menus.button(emote.regional_indicator('F'))
    async def change_total_slots(self, payload):
        msg = await self.cembed("How many total slots are there?")
        # slots = await inputs.integer_input(
        #     self.ctx,
        #     self.check,
        #     delete_after=True,
        #     limits=(1, 30),
        # )
        try:
            slots = await self.bot.wait_for('message', timeout=120, check=self.check)
        except asyncio.TimeoutError:
            await self.ctx.send(f"{emote.error} | You failed to select number of slots. Try again!")
            self.stop()
            return

        if not slots.content.isdigit():
            await self.ctx.send(f'{emote.error} | You Did Not Entered A Integer Please Try Agin By Running Same Command')
            self.stop()
            return
        int_slots = int(slots.content)
        if int_slots > 25:
            await self.ctx.send(f'{emote.error} | You Entered Slots Number More Than `25` \n**Note: Maximum Nuber Of Slots Is `25`**')
            self.stop()
            return
        await inputs.safe_delete(msg)
        await inputs.safe_delete(slots)
        await self.ctx.db.execute('UPDATE smanager.custom_data SET num_slots = $1 WHERE c_id = $2',int_slots,self.scrim['c_id'])
        await self.refresh_db()
        await self.ctx.db.execute('UPDATE smanager.custom_data SET allowed_slots = $2 WHERE c_id = $3',self.scrims['num_slots'] - self.scrim['reserverd_slots'],self.scrim['c_id'])
        await self.refresh()
        # await self.update_scrim(total_slots=slots)

    @menus.button(emote.regional_indicator('G'))
    async def change_open_time(self, payload):
        msg = await self.cembed(
            "**At what time should I open registrations?**"
            "\n> Time must be in 24h and in this format **`hh:mm`**"
        )

        # open_time = await inputs.time_input(self.ctx, self.check, delete_after=True)
        try:
            open_time = await self.ctx.bot.wait_for("message", check=self.check, timeout=120)
        except asyncio.TimeoutError:
            await self.ctx.send(f"{emote.error} | Timeout, You have't responsed in time. Try again!")
            self.stop()
            return
        else:
            match = re.match(r"\d+:\d+", open_time.content)
            if not match:
                await self.ctx.send(f'{emote.error} | Thats Not A Valid Time')
                self.stop()
                return
            match = match.group(0) 
            hour, minute = match.split(":")
            str_time = f'{hour}:{minute}'
            converting = datetime.strptime(str_time,'%H:%M')
            final_time = converting.time()
        await inputs.safe_delete(msg)
        await inputs.safe_delete(open_time)
        await self.refresh_db()
        await self.ctx.db.execute('UPDATE smanager.custom_data SET open_time = $1 WHERE c_id = $2',final_time,self.scrim['c_id'])
        await self.refresh()

    @menus.button(emote.regional_indicator('H'))
    async def change_reserved_slots(self, payload):
        msg = await self.cembed("How many reserved slots are there?")
        # reserverd_slots = await inputs.integer_input(
        #     self.ctx,
        #     self.check,
        #     delete_after=True,
        #     limits=(1, 30),
        # )
        try:
            reserverd_slots = await self.bot.wait_for('message', timeout=120, check=self.check)
        except asyncio.TimeoutError:
            await self.ctx.send(f"{emote.error} | You failed to select number of slots. Try again!")
            self.stop()
            return

        if not reserverd_slots.content.isdigit():
            await self.ctx.send(f'{emote.error} | You Did Not Entered A Integer Please Try Agin By Running Same Command')
            self.stop()
            return
        int_reserverd_slots = int(reserverd_slots.content)
        if int_reserverd_slots > self.scrim['num_slots']:
            await self.ctx.send(f'{emote.error} | You Entered Reserved Slots Number More Than Total Number Of Slots, it should be less than total num of slots ')
            self.stop()
            return
        await inputs.safe_delete(msg)
        await inputs.safe_delete(reserverd_slots)
        await self.ctx.db.execute('UPDATE smanager.custom_data SET reserverd_slots = $1 WHERE c_id = $2',int_reserverd_slots,self.scrim['c_id'])
        await self.refresh_db()
        await self.ctx.db.execute('UPDATE smanager.custom_data SET ,allowed_slots = $1 WHERE c_id = $3',self.scrim['num_slots'] - self.scrims['reserverd_slots'],self.scrim['c_id'])
        await self.refresh()

    @menus.button(emote.regional_indicator("I"))
    async def change_auto_clean(self, payload):
        if self.scrim['auto_clean'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET auto_clean = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET auto_clean = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()

    @menus.button(emote.regional_indicator("J"))
    async def change_auto_slotlist_sender(self, payload):
        if self.scrim['auto_slot_list_send'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET auto_slot_list_send = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET auto_slot_list_send = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()
        

    # @menus.button('🇯')
    # async def change_open_role(self, payload):
    #     msg = await self.cembed("For which role should I open registrations?")

    #     role = await inputs.role_input(
    #         self.ctx,
    #         self.check,
    #         delete_after=True,
    #     )

    #     await inputs.safe_delete(msg)
    #     await self.update_scrim(open_role_id=role.id)

    @menus.button("⏹️")
    async def on_stop(self, payload):
        self.stop()



class DaysEditorMenu(menus.Menu):
    def __init__(self,*, scrim):
        super().__init__(
            timeout=120,
            delete_message_after=False,
            clear_reactions_after=True,
        )
        self.scrim = scrim
        self.check = (
            lambda msg: msg.channel == self.ctx.channel
            and msg.author == self.ctx.author
        )

    def initial_embed(self):
        scrim = self.scrim

        embed = discord.Embed(color=discord.Color.green())
        embed.title = f"Edit Scrims Days Configuration: {scrim['c_id']}"

        def reactions(str):
            data = scrim[f'open_on_{str}']
            if data == True:
                return f'{emote.switch_on}'
            else:
                return f'{emote.switch_off}'

        fields = {
            ":one: Monday": f"{reactions('monday')}",
            ":two: Tuesday": f"{reactions('tuesday')}",
            ":three: Wednesday": f"{reactions('wednesday')}",
            ":four: Thursday": f"{reactions('thursday')}",
            ":five: Friday": f"{reactions('friday')}",
            ":six: Saturday": f"{reactions('saturday')}",
            ":seven: Sunday": f"{reactions('sunday')}",
        }

        for idx, (name, value) in enumerate(fields.items()):
            embed.add_field(
                name=f"{name}:",
                value=value,
            )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        return embed

    async def cembed(self, description):
        return await self.ctx.send(
            embed=discord.Embed(
                color=discord.Color.green(),
                title=f"🛠️ Scrims Manager",
                description=description,
            )
        )

    async def send_initial_message(self, ctx, channel):
        return await channel.send(embed=self.initial_embed())

    async def refresh(self):
        self.scrim = await self.ctx.db.fetchrow('SELECT * FROM smanager.custom_data WHERE c_id = $1',self.scrim['c_id'])
        await self.message.edit(embed=self.initial_embed())
    
    @menus.button('\U00000031\U0000fe0f\U000020e3')
    async def change_scrim_monday(self,payload):
        if self.scrim['open_on_monday'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_monday = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_monday = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()

    @menus.button('\U00000032\U0000fe0f\U000020e3')
    async def change_scrim_tuesday(self,payload):
        if self.scrim['open_on_tuesday'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_tuesday = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_tuesday = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()

    @menus.button('\U00000033\U0000fe0f\U000020e3')
    async def change_scrim_wednesday(self,payload):
        if self.scrim['open_on_wednesday'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_wednesday = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_wednesday = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()

    @menus.button('\U00000034\U0000fe0f\U000020e3')
    async def change_scrim_thursday(self,payload):
        if self.scrim['open_on_thursday'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_thursday = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_thursday = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()

    @menus.button('\U00000035\U0000fe0f\U000020e3')
    async def change_scrim_friday(self,payload):
        if self.scrim['open_on_friday'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_friday = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_friday = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()

    @menus.button('\U00000036\U0000fe0f\U000020e3')
    async def change_scrim_saturday(self,payload):
        if self.scrim['open_on_saturday'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_saturday = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_saturday = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()

    @menus.button('\U00000037\U0000fe0f\U000020e3')
    async def change_scrim_sunday(self,payload):
        if self.scrim['open_on_sunday'] == True:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_sunday = $1 WHERE c_id = $2',False,self.scrim['c_id'])
            await self.refresh()
        else:
            await self.ctx.db.execute('UPDATE smanager.custom_data SET open_on_sunday = $1 WHERE c_id = $2',True,self.scrim['c_id'])
            await self.refresh()

    @menus.button("⏹️")
    async def on_stop(self, payload):
        self.stop()
