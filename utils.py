def GetTextInsideParenthesis(string):
    return string[string.find('(')+1:string.find(')')]


def IdentExists(string, char_set):
    try:
        next(filter(lambda x: x.ident == string, char_set))
        return True
    except StopIteration:
        return False
