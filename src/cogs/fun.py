from .utils import emote
import discord
from discord.ext import commands
import requests
import aiohttp
import random
import ksoftapi





                    
class Fun(commands.Cog, name='Fun'):
    def __init__(self,bot):
        self.bot = bot
        self.ksoftclient = ksoftapi.Client(self.bot.ksoft_api_key)

    @commands.command()   
    async def meme(self,ctx):
        """Gives You Random Meme"""
        try:
            meme = await self.ksfotclient.images.random_meme()
        except:
            await ctx.send('An Error Occured.')
            return
        if meme.nsfw == True:
            await ctx.send('An Error Occured.')
            return
        em = discord.Embed(title = f'{meme.title}',color=self.bot.color)
        em.set_image(url=meme.image_url)
        em.set_footer(text=f'👍 {meme.upvotes} 👎 {meme.downvotes}')
        await ctx.send(embed=em)
    
    @commands.command(aliases=['howhot', 'hot'])
    async def hotcalc(self, ctx, *, user: discord.Member):
        """ Returns a random percent for how hot is a discord user """
        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        emoji = "💔"
        if hot > 25:
            emoji = "❤"
        if hot > 50:
            emoji = "💖"
        if hot > 75:
            emoji = "💞"
        
        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command()
    async def token(self,ctx,member:discord.Member):
        url = "https://some-random-api.ml/bottoken"
        json_data = requests.get(url).json()
        token = json_data['token']
        e = discord.Embed(title=f"{member.name}'s token:",description=f"```\n{token}```\n",color=self.bot.color)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def wasted(self,ctx,member: discord.Member = None):
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/wasted?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gay(self,ctx,member: discord.Member = None):
        """Adds Gay Overlay To Your Avatar"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/gay?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def glass(self,ctx,member: discord.Member = None):
        """Adds Glass Over Lay To Your Avatar"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/glass?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def greyscale(self,ctx,member: discord.Member = None):
        """Gray Scale Your Avtar"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/greyscale?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def invertgreyscale(self,ctx,member: discord.Member = None):
        """Inverts Grey Scale"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/invertgreyscale?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def brightness(self,ctx,member: discord.Member = None):
        """Brightens Avtar"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/brightness?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
        
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def threshold(self,ctx,member: discord.Member = None):
        """Thresholds Your Avtar"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/threshold?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sepia(self,ctx,member: discord.Member = None):
        """Converts Avtar In Sepia"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/sepia?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def red(self,ctx,member: discord.Member = None):
        """Converts Avtar Into Red"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/red?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def green(self,ctx,member: discord.Member = None):
        """Converts Avtar Into Green"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/green?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blue(self,ctx,member: discord.Member = None):
        """Converts Avtar Into Blue"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/blue?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)
    
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def invert(self,ctx,member: discord.Member = None):
        """Inverts Avtar"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/invert?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pixelate(self,ctx,member: discord.Member = None):
        """Pixelate Avtar"""
        member = member or ctx.author
        url = f"https://some-random-api.ml/canvas/pixelate?avatar={member.avatar_url_as(format='png')}"
        em = discord.Embed(color = ctx.author.color)
        em.set_image(url=url)
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    async def threats(self,ctx,member:discord.Member = None):
        member = ctx.author if not member else member
        api = f"https://nekobot.xyz/api/imagegen?type=threats&url={member.avatar_url}"
        r = requests.get(api).json()
        img = r['message']
        e = discord.Embed(title=f"There Are 3 Biggest Threats To World: ",description=f"Nuclear Bomb, Fire, {member.name}",color = self.bot.color)
        e.set_image(url=img)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def clyde(self,ctx,*,message:str):
        """Make Clyde Say Message"""
        api = f"https://nekobot.xyz/api/imagegen?type=clyde&text={message}"
        r = requests.get(api).json()
        img = r['message']
        await ctx.send(img)

    @commands.command()
    async def ship(self,ctx,member1:discord.Member,member2:discord.Member):
        api = f"https://nekobot.xyz/api/imagegen?type=ship&user1={member1.avatar_url}&user2={member2.avatar_url}"
        r = requests.get(api).json()
        img = r['message']
        e = discord.Embed(color=self.bot.color)
        e.set_image(url=img)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def captcha(self,ctx,member:discord.Member=None):
        member = ctx.author if not member else member
        api = f"https://nekobot.xyz/api/imagegen?type=captcha&url={member.avatar_url}&username={member.name}"
        r = requests.get(api).json()
        img = r['message']
        e = discord.Embed(color=self.bot.color)
        e.set_image(url=img)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)
    
    @commands.command()
    async def gif(self,ctx,*,search_term):
        """Search Your Favoriate GIF"""
        if search_term is None or search_term == "":
            return await ctx.send(f"{emote.xmark} | Please enter a valid search term")
        lmt = 10
        r = requests.get(f"https://g.tenor.com/v1/search?q={search_term}&key={self.bot.tenor_apikey}&limit={lmt}").json()
        rval = random.randint(0,10)
        url_fetch = r["results"][rval]["media"][0]["gif"]["url"]
        e = discord.Embed(color=self.bot.color)
        e.set_image(url=url_fetch)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)
    
    @commands.command()
    async def whowouldwin(self,ctx,member1:discord.Member,member2:discord.Member):
        api = f"https://nekobot.xyz/api/imagegen?type=whowouldwin&user1={member1.avatar_url}&user2={member2.avatar_url}"
        r = requests.get(api).json()
        img = r['message']
        e = discord.Embed(title=f"Who Would Win?? {member1.name} or {member2.name}",color=self.bot.color)
        e.set_image(url=img)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def iphone(self,ctx,member:discord.Member = None):
        member = ctx.author if not member else member
        api = f"https://nekobot.xyz/api/imagegen?type=iphonex&url={member.avatar_url}"
        r = requests.get(api).json()
        img = r['message']
        e = discord.Embed(color=self.bot.color)
        e.set_image(url=img)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def trumptweet(self,ctx,*,message:str):
        """Makes A Trump Tweet"""
        api = f"https://nekobot.xyz/api/imagegen?type=trumptweet&text={message}"
        r = requests.get(api).json()
        img = r['message']
        e = discord.Embed(color=self.bot.color)
        e.set_image(url=img)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def tweet(self,ctx,*,message:str):
        """Makes A tweet"""
        api = f"https://nekobot.xyz/api/imagegen?type=tweet&username={ctx.author.name}&text={message}"
        r = requests.get(api).json()
        img = r['message']
        e = discord.Embed(title=f"{ctx.author.name} Just Tweeted",color=self.bot.color)
        e.set_image(url=img)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command(aliases=['phcomment'])
    async def pornhubcomment(self,ctx,*,message:str):
        """Makes A P*** Hub Comment"""
        api = f"https://nekobot.xyz/api/imagegen?type=phcomment&image={ctx.author.avatar_url}&text={message}&username={ctx.author.name}"
        r = requests.get(api).json()
        img = r['message']
        e = discord.Embed(title=f"{ctx.author.name} Just Commented On P*** Hub",color=self.bot.color)
        e.set_image(url=img)
        e.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def wink(self,ctx,user: discord.Member = None):
        if user == None:
            user = ctx.author

        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/animu/wink') as r:
                    data = await r.json()

                    em = discord.Embed(title=f'{ctx.author} Wants To Wink {user}',timestamp=ctx.message.created_at,color=discord.Colour.green())
                    em.set_image(url = data['link'])
                    em.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    async def pat(self,ctx,):
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/animu/pat') as r:
                    data = await r.json()

                    em = discord.Embed(title=f'Pat! is self-explanatory i guess',timestamp=ctx.message.created_at,color=discord.Colour.green())
                    em.set_image(url = data['link'])
                    em.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    async def hug(self,ctx,user: discord.Member = None):
        if user == None:
            user = ctx.author

        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/animu/hug') as r:
                    data = await r.json()

                    em = discord.Embed(title=f'{ctx.author} Wants To Hug {user}',timestamp=ctx.message.created_at,color=discord.Colour.green())
                    em.set_image(url = data['link'])
                    em.set_footer(icon_url = ctx.author.avatar_url, text = f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Fun(bot))