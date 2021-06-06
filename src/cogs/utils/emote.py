xmark = '<:xmark:820320509211574284>'
tick = '<:tick:820320509564551178>'
voice_channel = '<:Voice_channels:820162682883014667> '
text_channel = '<:Text_Channel:820162682970832897>'
error = '<:error:820162683147911169>'
questionmark = '<:questionmark:820319249867866143>'
info = '<:info:820332723121684530>'
youtube = '<:yotube:820657499895103518>'
loading = '<a:loading:824225352573255680>'
number_emojis = {
    1: "\u0031\ufe0f\u20e3",
    2: "\u0032\ufe0f\u20e3",
    3: "\u0033\ufe0f\u20e3",
    4: "\u0034\ufe0f\u20e3",
    5: "\u0035\ufe0f\u20e3",
    6: "\u0036\ufe0f\u20e3",
    7: "\u0037\ufe0f\u20e3",
    8: "\u0038\ufe0f\u20e3",
    9: "\u0039\ufe0f\u20e3"
}
x = "\U0001f1fd"
o = "\U0001f1f4"
switch_on ='<:switch_on:845865302571089930>'
switch_off ='<:switch_off:845865362193252372>'

def regional_indicator(c: str) -> str:
    """Returns a regional indicator emoji given a character."""
    return chr(0x1F1E6 - ord("A") + ord(c.upper()))
    

