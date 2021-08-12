import discord
from discord.ext import commands

class AutoEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild

        record = await self.bot.db.fetchrow('SELECT * FROM server_configs WHERE guild_id = $1 AND autorole_toggle = $2',guild.id,True)
        if not record:
            return

        if not member.bot:
            if record['autorole_human_toggle'] is False:
                return
            try:
                await member.add_roles(discord.Object(id=record['autorole_human']), reason="Credo's autorole")
            except discord.Forbidden:
                return

        elif member.bot:
            if record['autorole_bot_toggle'] is False:
                return
            try:
                await member.add_roles(discord.Object(id=record['autorole_bot']), reason="Credo's autorole")
            except discord.Forbidden:
                return
        else:
            pass

def setup(bot):
    bot.add_cog(AutoEvents(bot))