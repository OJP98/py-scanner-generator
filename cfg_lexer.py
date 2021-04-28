from utils import (
    IdentExists,
    GetElementType,
    GetTextInsideSymbols,
    GetIdentValue,
    GetCharValue
)
from set_parser import TokenExpression, SetGenerator, SetDecl
from cfg_classes import *
from math import inf
from parsing import Parser
from direct_dfa import DDFA
from pprint import pprint

SCANNER_WORDS = ['COMPILER', 'CHARACTERS', 'IGNORE',
                 'KEYWORDS', 'TOKENS', 'END', 'PRODUCTIONS']


class CFG:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

        self.compiler_name = None
        self.characters = list()
        self.keywords = list()
        self.tokens = list()
        self.ignore = set()

        self.file_lines = self.ReadFile()
        self.curr_line = None
        self.Next()

        self.ReadLines()
        self.allchars = set()

    def Next(self):
        try:
            self.curr_line = next(self.file_lines)
        except StopIteration:
            self.curr_line = None

    def ReadFile(self):
        try:
            self.file = open(self.filepath, 'r', encoding='latin-1')
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
                    # print('\n', '='*20, 'TOKENS', '='*20)
                    self.ReadSection('TOKENS')

                elif 'IGNORE' in self.curr_line:
                    self.ReadIgnore()
                    self.Next()

                elif 'PRODUCTIONS' in self.curr_line:
                    self.Next()

                elif 'END' in self.curr_line:
                    end_compiler_name = self.curr_line[self.curr_line.index(
                        'END')+1]
                    self.Next()

            elif '(.' in self.curr_line[:2]:
                self.ReadComment()
                self.Next()

            else:
                self.Next()

    def ReadSection(self, section):
        joined_set = ''
        while not any(word in SCANNER_WORDS for word in self.curr_line):
            curr_set = ' '.join(self.curr_line)

            # Is there a comment?
            if '(.' in curr_set[:2]:
                self.ReadComment()

            # Does the set contains both = and .
            if '=' in curr_set and '.' == curr_set[-1] and joined_set != '':
                curr_set = curr_set[:-1]
                self.GetKeyValue(curr_set, section)
                self.Next()

            # elif '=' in curr_set and not '.' == curr_set[-1]:
            #     print('\nWARNING: Statement without ending (Ignored):', curr_set)
            #     self.Next()

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
                print('WARNING: Ignored statement:', curr_set)
                self.Next()

    def ReadComment(self):
        while not '.)' in self.curr_line:
            self.Next()

    def ReadIgnore(self):
        curr_set = ' '.join(self.curr_line)
        line = curr_set.split('IGNORE', 1)[1]
        line = line.replace('.', '')

        value = SetDecl(line, self.characters).Set()
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
        ident, value = line.split('=', 1)
        ident = ident.strip()
        value = value.strip()
        context = None

        # Check if ident exists
        if IdentExists(ident, self.characters):
            raise Exception(f'Ident "{ident}" declared twice!')

        # Are there any keywords?
        # TODO: Except might be lower case or upper case
        if 'EXCEPT' in value:
            kwd_index = value.index('EXCEPT')
            context = value[kwd_index:]
            value = value[:kwd_index]

        # Parse this new set
        parser = TokenExpression(value, self.characters)
        value = parser.Parse(token_id=ident)
        token = Token(ident, list(value), context)
        # print()
        # print(f'{token}')
        self.tokens.append(token)

    def KeywordDecl(self, line):
        ident, value = line.split('=', 1)
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
        key, value = line.split('=', 1)

        key = key.strip()
        set_decl = SetDecl(value, self.characters)
        value = list(set_decl.Set())
        # print()
        # print(f'CRUDO:\n{key}: {value}')
        final_set = SetGenerator(value, self.characters).GenerateSet()
        # print()
        # print(f'GENERADO\n{key}: {final_set}')
        self.characters.append(Character(key, final_set))

    def GenerateSet(self, eval_set):
        generator = SetGenerator(eval_set, self.characters)
        generated_set = generator.GenerateSet()
        return generated_set

    def GetAllChars(self):
        for character in self.characters:
            self.allchars.update(character.value)
        for token in self.tokens:
            for var in token.value:
                if var.type == VarType.CHAR or var.type == VarType.STRING:
                    self.allchars.update(var.value)

        return self.allchars

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
