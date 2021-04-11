from cfg_classes import VarType, Variable
from re import findall


def GetTextInsideSymbols(string, init_symbol, end_symbol):
    start = string.find(init_symbol)
    end = string.find(end_symbol)

    if start == -1 or end == -1:
        return None

    if string.count(init_symbol) != 1 or string.count(end_symbol) != 1:
        return None

    return string[start+1:end]


def GetTextFromDoubleQuotes(string):
    text = findall('"([^"]*)"', string)

    if not text:
        return None
    if len(text) > 1:
        return None

    return text[0]


def GetTextFromSingleQuotes(string):
    text = findall("'([^']*)'", string)

    if not text:
        return None
    if len(text) > 1:
        return None

    return str(text[0])


def GetNoAlpha(string):
    pos = 1
    while pos < len(string) and (string[pos].isalpha() or string[pos] == '|'):
        pos += 1
    return pos if pos < len(string) else None


def IdentExists(ident, char_set):
    try:
        next(filter(lambda x: x.ident == ident, char_set))
        return True
    except StopIteration:
        return False


def GetIdentValue(ident, char_set):
    try:
        ident = next(filter(lambda x: x.ident == ident, char_set))
        return ident.value.value
    except StopIteration:
        return None


def GetCharValue(char):
    # Finally, we check for the text inside the parenthesis
    value = GetTextInsideSymbols(char, '(', ')')

    # Check for missing or extra parenthesis
    if value == None:
        raise Exception(
            'In CHARACTERS, char is not defined correctly: missplaced parenthesis')

    # Check if the value is a digit
    if not value.isdigit():
        raise Exception(
            'In CHARACTERS, char is not defined correctly: non-digit CHR value')

    return chr(int(value))


def GetElementType(string, char_set):
    if '"' in string:
        return Variable(VarType.STRING, string.replace('"', ''))

    if '\'' in string:
        char = string.replace('\'', '')
        return Variable(VarType.CHAR, char)

    if string.isdigit():
        return Variable(VarType.NUMBER, string)

    if IdentExists(string, char_set):
        return Variable(VarType.IDENT, string)

    if 'CHR' in string:
        return Variable(VarType.CHAR, GetCharValue(string))
