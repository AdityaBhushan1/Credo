import discord 
import asyncio
import json
avaible_slots = '2'
total_slots = '3'
reserved_slots = '4'
mentions_required = '5'
def check(msg):
    return msg.author == ctx.author and ctx.channel == msg.channel
try:
    message = await bot.wait_for('message', timeout=80.0, check=check)
except asyncio.TimeoutError:
    return await ctx.send(embed = took_long)

content = str(message.content)
content = content.replace('<<available_slots>>',avaible_slots)
content = content.replace('<<total_slots>>',total_slots)
content = content.replace('<<reserved_slots>>',reserved_slots)
content = content.replace('<<mentions_required>>',mentions_required)
if content.startswith('{') and content.endswith('}'):
    embed = json.loads(content)
    if len(embed['title']) > 200:
        return await ctx.send('Title Is So Long')
    if len(embed['description']) > 2000:
        return await ctx.send('Description Is So Long')
    if "footer" in content:
        if len(embed['footer']['text']) > 200:
            return await ctx.send('Footer Is So Long')
    if "author" in content:
        if len(embed['author']['name'])>200:
            return await ctx.send('Author Is So Long')


    final_embed = discord.Embed.from_dict(embed)
    await ctx.channel.send(embed=final_embed)
else:
    return await ctx.send('Nope')


# string = 'testing 12345 @#$ <<available_slots>>'
# string = string.replace('<<available_slots>>','2')
# print(string)
