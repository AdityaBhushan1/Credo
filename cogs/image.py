import discord
from discord.ext import commands
import aiohttp
import requests


class Image(commands.Cog, name='Image'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def cat(self, ctx):
        """Gives You Random Image Of Cat"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('http://aws.random.cat/meow') as r:
                    data = await r.json()

                    em = discord.Embed(
                        title='Cat', timestamp=ctx.message.created_at, color=self.bot.color)
                    em.set_image(url=data['file'])
                    em.set_footer(icon_url=ctx.author.avatar_url,
                                  text=f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def dog(self, ctx):
        """Gives You Random Image Of Dog"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('http://random.dog/woof.json') as r:
                    data = await r.json()

                    em = discord.Embed(
                        title='Dog', timestamp=ctx.message.created_at, color=self.bot.color)
                    em.set_image(url=data['url'])
                    em.set_footer(icon_url=ctx.author.avatar_url,
                                  text=f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def fox(self, ctx):
        """Gives You Random Image Of Fox"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/img/fox') as r:
                    data = await r.json()

                    em = discord.Embed(
                        title='Fox', timestamp=ctx.message.created_at, color=self.bot.color)
                    em.set_image(url=data['link'])
                    em.set_footer(icon_url=ctx.author.avatar_url,
                                  text=f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def panda(self, ctx):
        """Gives You Random Image Of Panda"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/img/panda') as r:
                    data = await r.json()

                    em = discord.Embed(
                        title='Panda', timestamp=ctx.message.created_at, color=self.bot.color)
                    em.set_image(url=data['link'])
                    em.set_footer(icon_url=ctx.author.avatar_url,
                                  text=f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def red_panda(self, ctx):
        """Gives You Random Image Of Red Panda"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/img/red_panda') as r:
                    data = await r.json()

                    em = discord.Embed(
                        title='Red Panda', timestamp=ctx.message.created_at, color=self.bot.color)
                    em.set_image(url=data['link'])
                    em.set_footer(icon_url=ctx.author.avatar_url,
                                  text=f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bird(self, ctx):
        """Gives You Random Image Of Bird"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/img/birb') as r:
                    data = await r.json()

                    em = discord.Embed(
                        title='Bird', timestamp=ctx.message.created_at, color=self.bot.color)
                    em.set_image(url=data['link'])
                    em.set_footer(icon_url=ctx.author.avatar_url,
                                  text=f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def kola(self, ctx):
        """Gives You Random Image Of Kola"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/img/koala') as r:
                    data = await r.json()

                    em = discord.Embed(
                        title='kola', timestamp=ctx.message.created_at, color=self.bot.color)
                    em.set_image(url=data['link'])
                    em.set_footer(icon_url=ctx.author.avatar_url,
                                  text=f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pikachu(self, ctx):
        """Gives You Random Image Or GIF Of Pikachu"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://some-random-api.ml/img/pikachu') as r:
                    data = await r.json()

                    em = discord.Embed(
                        title='Pikachu', timestamp=ctx.message.created_at, color=self.bot.color)
                    em.set_image(url=data['link'])
                    em.set_footer(icon_url=ctx.author.avatar_url,
                                  text=f"Requested By {ctx.author.name}")
                    await ctx.send(embed=em)

    # @commands.command()
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def yt(self,ctx,comment:str):
    #     """Comments On Youtube"""
    #     url = f"https://some-random-api.ml/canvas/youtube-comment?avatar={ctx.author.avatar_url_as(format='png')}&username={ctx.author}&comment={comment}"
    #     em = discord.Embed(color = ctx.author.color)
    #     em.set_image(url=url)
    #     em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    #     await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Image(bot))
