import discord
from discord.ext import commands
import asyncio
from . import emote
from typing import Optional
from abc import ABC
from discord import Message, Embed, TextChannel, errors
from typing import Optional

__all__ = ("ConfirmationPrompt")



class Dialog(ABC):
    def __init__(self, *args, **kwargs):
        self._embed: Optional[Embed] = None
        self.message: Optional[Message] = None
        self.color: hex = kwargs.get("color") or kwargs.get("colour") or 0x4ca64c

    async def _publish(self, channel: Optional[TextChannel], **kwargs) -> TextChannel:
        if channel is None and self.message is None:
            raise TypeError(
                "Missing argument. You need to specify a target channel or message."
            )

        if channel is None:
            try:
                await self.message.edit(**kwargs)
            except errors.NotFound:
                self.message = None

        if self.message is None:
            self.message = await channel.send(**kwargs)

        return self.message.channel

    async def quit(self, text: str = None):
        if text is None:
            await self.message.delete()
            self.message = None
        else:
            await self.display(text)
            try:
                await self.message.clear_reactions()
            except errors.Forbidden:
                pass

    async def update(self, title: str = None, description: str = None, color: hex = None, hide_author: bool = False):
        if color is None:
            color = self.color

        self._embed.colour = color
        if title is not None:
            self._embed.title = title
        else:
            self._embed.title = None
        if description is not None:
            self._embed.description = description
        else:
            self._embed.description = None

        if hide_author:
            self._embed.set_author(name="")

        await self.display(embed=self._embed)

    async def display(self, text: str = None, embed: Embed = None):

        await self.message.edit(content=text, embed=embed)

class Confirmation(Dialog):
    """ Represents a message to let the user confirm a specific action. """

    def __init__(
        self,
        client: discord.Client,
        color: hex = 0x4ca64c,
        message: discord.Message = None,
    ):
        super().__init__(color=color)

        self._client = client
        self.color = color
        self.emojis = {f"{emote.tick}": True, f"{emote.xmark}": False}
        self._confirmed = None
        self.message = message
        self._embed: Optional[discord.Embed] = None

    @property
    def confirmed(self) -> bool:
        return self._confirmed

    async def confirm(
        self,
        user: discord.User,
        title: str = None,
        description: str = None,
        channel: discord.TextChannel = None,
        hide_author: bool = False,
        timeout: int = 20,
    ) -> bool or None:

        emb = discord.Embed(color=self.color)
        if title is not None:
            emb.title = title
        else:
            emb.title = None
        if description is not None:
            emb.description = description
        else:
            emb.description = None
        if not hide_author:
            emb.set_author(name=str(user), icon_url=user.avatar_url)

        self._embed = emb

        await self._publish(channel, embed=emb)
        msg = self.message

        for emoji in self.emojis:
            await msg.add_reaction(emoji)

        try:
            reaction = await self._client.wait_for(
                "raw_reaction_add",
                check=lambda r: (r.message_id == msg.id)
                and (r.user_id == user.id)
                and (str(r.emoji) in self.emojis),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            self._confirmed = None
            return
        else:
            self._confirmed = self.emojis[str(reaction.emoji)]
            return self._confirmed
        finally:
            try:
                await msg.clear_reactions()
            except discord.Forbidden:
                pass


class ConfirmationPrompt(Confirmation):
    def __init__(
        self,
        ctx: commands.Context,
        color: hex = 0x4ca64c,
        message: discord.Message = None,
    ):
        self._ctx = ctx

        super().__init__(ctx.bot, color, message)

    async def confirm(
        self,
        user: discord.User = None,
        title: str = None,
        description: str = None,
        channel: discord.TextChannel = None,
        hide_author: bool = False,
        timeout: int = 20,
    ) -> bool or None:
        

        if user is None:
            user = self._ctx.author

        if self.message is None and channel is None:
            channel = self._ctx.channel

        return await super().confirm(user,title,description, channel, hide_author, timeout)