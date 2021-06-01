from discord.ext import commands
from. import emote
class TeaBoterror(commands.CheckFailure):
    pass

class InvalidColor(TeaBoterror):
    def __init__(self, argument):
        super().__init__(
            f"{emote.error} |`{argument}` doesn't seem to be a valid color, \nPick a correct colour from [here](https://www.google.com/search?q=color+picker)"
        )

class InputError(TeaBoterror):
    pass

class PastTime(TeaBoterror):
    def __init__(self):
        super().__init__(
            f"{emote.error} |The time you entered seems to be in past.\n\nKindly try again, use times like: `tomorrow` , `friday 9pm`"
        )


TimeInPast = PastTime


class InvalidTime(TeaBoterror):
    def __init__(self):
        super().__init__(f"{emote.error} |The time you entered seems to be invalid.\n\nKindly try again.")

class NotSetup(TeaBoterror):
    def __init__(self):
        super().__init__(
            f"{emote.error} |This command requires you to have Quotient's private channel.\nKindly setup teh bot and try again."
        )