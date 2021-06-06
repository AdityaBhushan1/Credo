from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await guild.chunk()
        print(f"-------------------------------------")
        print(f"Succefully Chunked Guilds")
        print(f"-------------------------------------")
        print(f"Logging In...........................")
        print(f"Logged In as: {self.bot.user.name}({self.bot.user.id})")
        print(f"Connected Guilds:", len(self.bot.guilds))
        print(f"Connected Users", len(self.bot.users))
        print(f"-------------------------------------")
    

def setup(bot):
    bot.add_cog(Events(bot))
