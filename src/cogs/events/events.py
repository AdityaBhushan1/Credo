from discord.ext import commands
from colorama import Fore

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.RED + f"-------------------------------------")
        print(Fore.GREEN + f"Logging In...........................")
        print(Fore.GREEN + f"Logged In as: {self.bot.user.name}({self.bot.user.id})")
        print(Fore.GREEN + f"Connected Guilds:", len(self.bot.guilds))
        print(Fore.GREEN + f"Connected Users", len(self.bot.users))
        print(Fore.RED + f"-------------------------------------")

def setup(bot):
    bot.add_cog(Events(bot))
