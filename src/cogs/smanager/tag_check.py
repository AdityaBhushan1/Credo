from discord.ext import commands
from ..utils import emote
class TagCheckListners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

####################################################################################################################
#===================================================== tag check listners =========================================#
####################################################################################################################
    
    @commands.Cog.listener()
    async def on_message(self,message):
        data = await self.bot.db.fetchrow('SELECT * FROM smanager.tag_check WHERE ch_id = $1 AND toggle != $2',message.channel.id,False)
        if not data:
            return

        if message.author.bot or "teabot-smanger" in [role.name for role in message.author.roles]:
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
        try:
            matched_lines = [line.strip() for line in message.clean_content.lower().split('\n') if "team" in line]
            team_name = [x for x in matched_lines[0].lower().split() if x not in {'team', 'name', ':', '-', ':-', 'name:', 'name-', 'name:-'}]
            team_name = ' '.join([i for i in team_name if all(ch not in i for ch in ['@'])])
        except:
            await message.reply('Team Name Is Not Correct',delete_after=10)
            try:
                await message.add_reaction(f'{emote.xmark}')
            except:
                pass
            return

        try:
            await message.add_reaction(f'{emote.tick}')
        except:
            pass


