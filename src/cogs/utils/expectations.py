from discord.ext import commands
from. import emote
class Credoerror(commands.CheckFailure):
    pass

class InvalidColor(Credoerror):
    def __init__(self, argument):
        super().__init__(
            f"{emote.error} | `{argument}` doesn't seem to be a valid color, \nPick a correct colour from [here](https://www.google.com/search?q=color+picker)"
        )

class PastTime(Credoerror):
    def __init__(self):
        super().__init__(
            f"{emote.error} |The time you entered seems to be in past.\n\nKindly try again, use times like: `tomorrow` , `friday 9pm`"
        )


TimeInPast = PastTime


class InvalidTime(Credoerror):
    def __init__(self):
        super().__init__(f"{emote.error} |The time you entered seems to be invalid.\n\nKindly try again.")

class NotSetup(Credoerror):
    def __init__(self):
        super().__init__(
            f"{emote.error} | This command requires you to have Credo Setuped In This Server.\nKindly setup the bot and try again."
        )


class ScrimsManagerNotSetup(Credoerror):
    def __init__(self):
        super().__init__(
            f"{emote.error} | This command requires you to have Scrims Manager Setuped In This Server.\nKindly setup the scrims manager and try again."
        )