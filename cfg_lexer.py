from utils import (
    IdentExists,
    GetElementType,
    GetTextInsideSymbols,
    GetIdentValue,
    GetCharValue
)
from set_parser import SetParser, SetGenerator
from cfg_classes import *
from math import inf
from parsing import Parser
from direct_dfa import DDFA

CONTEXT_WORDS = ['EXCEPT', 'ANY', 'IGNORE', 'IGNORECASE']
SCANNER_WORDS = ['COMPILER', 'CHARACTERS', 'IGNORE',
                 'KEYWORDS', 'TOKENS', 'END', 'PRODUCTIONS']
TOKEN_KEYWORDS = ['EXCEPT', 'KEYWORDS']


class CFG:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

        self.compiler_name = None
        self.characters = list()
        self.keywords = list()
        self.tokens = list()
        self.ignore = None

        self.file_lines = self.ReadFile()
        self.curr_line = None
        self.Next()

        self.ReadLines()

    def Next(self):
        try:
            self.curr_line = next(self.file_lines)
        except StopIteration:
            self.curr_line = None

    def ReadFile(self):
        try:
            self.file = open(self.filepath, 'r')
        except:
            raise Exception('File not found!')
        finally:
            lines = self.file.readlines()
            temp = list()
            for line in lines:
                if line != '\n':
                    line = line.strip('\r\t\n')
                    line = line.strip()
                    line = line.split(' ')
                    line[:] = [i for i in line if i != '' or i]
                    temp.append(line)

        return iter(temp)

    def ReadLines(self):
        while self.curr_line != None:
            # Check if we got any important word in the lines
            if any(word in SCANNER_WORDS for word in self.curr_line):

                if 'COMPILER' in self.curr_line:
                    self.compiler_name = self.curr_line[self.curr_line.index(
                        'COMPILER')+1]
                    self.Next()

                elif 'CHARACTERS' in self.curr_line:
                    self.Next()
                    self.ReadSection('CHARACTERS')

                elif 'KEYWORDS' in self.curr_line:
                    self.Next()
                    self.ReadSection('KEYWORDS')

                elif 'TOKENS' in self.curr_line:
                    self.Next()
                    self.ReadSection('TOKENS')

                elif 'IGNORE' in self.curr_line:
                    self.ReadIgnore()
                    self.Next()

                elif 'PRODUCTIONS' in self.curr_line:
                    self.Next()

                elif 'END' in self.curr_line:
                    self.Next()

            elif '(.' in self.curr_line:
                self.ReadComment()
                self.Next()

            else:
                self.Next()

    def ReadSection(self, section):
        joined_set = ''
        while not any(word in SCANNER_WORDS for word in self.curr_line):
            curr_set = ' '.join(self.curr_line)

            # Is there a comment?
            if '(.' in curr_set:
                self.ReadComment()

            # Does the set contains both = and .
            if '=' in curr_set and '.' == curr_set[-1]:
                curr_set = curr_set[:-1]
                self.GetKeyValue(curr_set, section)
                self.Next()

            # If it doesn't contains a ., it's probably part of the previous set
            elif not '.' == curr_set[-1]:
                joined_set += curr_set
                self.Next()

            # If there's a ., it's probably the end of a previously joined set
            elif '.' == curr_set[-1]:
                joined_set += curr_set
                joined_set = joined_set[:-1]
                self.GetKeyValue(joined_set, section)
                self.Next()

            elif '(.' in self.curr_line:
                self.ReadComment()
                self.Next()

            else:
                print('POSIBLE ERROR:', curr_set)

    def ReadComment(self):
        while not '.)' in self.curr_line:
            self.Next()

    def ReadIgnore(self):
        curr_set = ' '.join(self.curr_line)
        line = curr_set.split('IGNORE', 1)[1]
        line = line.replace('.', ' ')
        value = self.Set(line)

        final_set = SetGenerator(value, self.characters).GenerateSet()
        self.ignore = final_set

    def GetKeyValue(self, line, attr):
        if attr == 'CHARACTERS':
            self.SetDecl(line)
        elif attr == 'KEYWORDS':
            self.KeywordDecl(line)
        elif attr == 'TOKENS':
            self.TokenDecl(line)

    def TokenDecl(self, line):
        ident, value = line.split('=')
        ident = ident.strip()
        value = value.strip()
        context = None

        # Check if ident exists
        if IdentExists(ident, self.characters):
            raise Exception(f'Ident "{ident}" declared twice!')

        # Are there any keywords?
        if 'EXCEPT' in value:
            kwd_index = value.index('EXCEPT')
            context = value[kwd_index:]
            value = value[:kwd_index]

        # Parse this new set
        parser = SetParser(value, self.characters)
        value = parser.Parse(token_id=ident)
        token = Token(ident, list(value), context)
        self.tokens.append(token)

    def KeywordDecl(self, line):
        ident, value = line.split('=')
        ident = ident.strip()
        value = value.strip().replace('.', '')
        value = value.replace('"', '')
        value = Variable(VarType.STRING, value)

        # Create ident object
        keyword = Keyword(ident, value)

        # Check if ident exists, else append it to list
        if IdentExists(ident, self.keywords):
            raise Exception('Keyword declared twice!')

        self.keywords.append(keyword)

    def SetDecl(self, line):
        key, value = line.split('=')

        key = key.strip()
        value = self.Set(value.strip())
        final_set = SetGenerator(value, self.characters).GenerateSet()
        self.characters.append(Character(key, final_set))

    def Set(self, value):
        value = value.replace(' ', '')
        bset = self.BasicSet(value)
        return bset

    def BasicSet(self, string):
        temp = list()

        while string:
            plus_index = string.find('+')
            minus_index = string.find('-')

            plus_index = plus_index if plus_index != -1 else inf
            minus_index = minus_index if minus_index != -1 else inf

            if plus_index < minus_index:
                char = self.Char(string[:plus_index], self.characters)
                temp.append(char)
                temp.append(Variable(VarType.UNION, '+'))
                string = string[plus_index+1:]

            elif minus_index < plus_index:
                char = self.Char(string[:minus_index], self.characters)
                temp.append(char)
                temp.append(Variable(VarType.DIFFERENCE, '-'))
                string = string[minus_index+1:]

            else:
                char = self.Char(string, self.characters)
                temp.append(char)
                break

        return temp

    def Char(self, string, item_set):

        values = string.split('..')

        if len(values) == 1:
            val = values[0]
            return GetElementType(val, self.characters)

        if len(values) != 2:
            raise Exception(
                f'In CHARACTERS, found more than one range instance: {string}')

        val1 = GetElementType(values[0], self.characters)
        val2 = GetElementType(values[1], self.characters)

        if not val1 or not val2:
            raise Exception(f'Unvalid char in Char: {string}')

        if val1.type != VarType.CHAR or val2.type != VarType.CHAR:
            raise Exception(
                f'Unvalid char range {string}')

        val1 = list(val1.value)[0]
        val2 = list(val2.value)[0]
        range1 = ord(val1)
        range2 = ord(val2)

        if range1 > range2:
            range1, range2 = range2, range1

        # Create a new list with all the chars in the range
        char_range = set([chr(char)
                          for char in range(range1, range2 + 1)])

        return Variable(VarType.CHAR, char_range)

    def GenerateSet(self, eval_set):
        generator = SetGenerator(eval_set, self.characters)
        generated_set = generator.GenerateSet()
        return generated_set

    def __repr__(self):
        return f'''
Compiler: {self.compiler_name}

Characters:
{self.characters}

Keywords:
{self.keywords}

Tokens:
{self.tokens}

''' + (f'Ignore: {self.ignore}' if self.ignore else '')
