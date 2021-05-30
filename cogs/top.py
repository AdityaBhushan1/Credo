import dbl
import discord
from discord.ext import commands


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = self.bot.top_gg 
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

def setup(bot):
    bot.add_cog(TopGG(bot))
    print('Loaded top.gg')