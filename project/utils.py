# Encodes string: '\n' (one character) -> '\\n' (two characters)
def encode(text: str) -> str:
    return text.encode('unicode_escape').decode('latin1')


# Decodes string: '\\n' (two characters) -> '\n' (one character)
def decode(text: str) -> str:
    return text.encode('latin1').decode('unicode-escape')
