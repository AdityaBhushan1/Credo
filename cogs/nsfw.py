import requests
import discord
from discord import embeds
from discord.ext import commands
non_nsfw_gif = "https://cdn.discordapp.com/attachments/802518639274229800/802936914054610954/nsfw.gif"


class Nsfw(commands.Cog, name='NSFW'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hass(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=hass"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            await ctx.send(embed=em)

    @commands.command()
    async def hmidriff(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=hmidriff"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def pgif(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=pgif"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def fourk(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=4k"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def hneko(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=hneko"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def hkitsune(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=hkitsune"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def hentai(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=hentai"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def anal(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=anal"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def hanal(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=hanal"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def gonewild(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=gonewild"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def ass(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=ass"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def pussy(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=pussy"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def thigh(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=thigh"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def paizuri(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=paizuri"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def tentacle(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=tentacle"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def boobs(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=boobs"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def hboobs(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=hboobs"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)

    @commands.command()
    async def yaoi(self, ctx):
        nsfw = ctx.channel.is_nsfw()
        if nsfw == True:
            api = "https://nekobot.xyz/api/image?type=yaoi"
            r = requests.get(api).json()
            img = r['message']
            em = discord.Embed(color=ctx.author.color)
            em.set_image(url=img)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                title="Non-NSFW channel detected!", color=self.bot.color)
            em.add_field(name="Why should you care?",
                         value="Discord forbids the use of NSFW content outside the NSFW-option enabled channels.[More here](https://discord.com/guidelines#:~:text=You%20must%20apply%20the%20NSFW,sexualize%20minors%20in%20any%20way.)")
            em.set_image(url=non_nsfw_gif)
            
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Nsfw(bot))
