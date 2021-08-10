import discord
from discord.ext import commands, tasks
import aiohttp
import ksoftapi




class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.automeme.start()
        self.client = ksoftapi.Client(self.bot.ksoft_api_key)

    @tasks.loop(minutes=5)
    async def automeme(self):
        # print('entered automeme')
        async with aiohttp.ClientSession() as cs:
            try:
                meme = await self.client.images.random_meme()
            except:
                return
            if meme.nsfw is True:
                return
            em = discord.Embed(title = f'{meme.title}',color=self.bot.color)
            em.set_image(url=meme.image_url)
            em.set_footer(text=f'👍 {meme.upvotes} 👎 {meme.downvotes}')
            channel_id = []
            record = await self.bot.db.fetch('SELECT automeme_channel_id FROM public.server_configs WHERE automeme_toogle = $1',True)   
            if not record:return
            for res in record:
                r = res['automeme_channel_id']
                channel_id.append(r)
            for channels in channel_id:
                channel = self.bot.get_channel(channels)
                await channel.send(embed = em)
                # print('done')
    @automeme.before_loop
    async def before_automeme(self):
        await self.bot.wait_until_ready()
    


def setup(bot):
    bot.add_cog(Tasks(bot))
