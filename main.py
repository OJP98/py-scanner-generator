#!/usr/bin/python
import sys
import pickle
from cfg_lexer import CFG
from direct_dfa import DDFA
from parsing import Parser

program_title = '''

#        ...        #

Evaluate tokens based on a user-defined grammar file. The default-file is taken in input/grammar.cfg. If you want to specify a grammar of your own, you may edit the current grammar.cfg file or create a .cfg file and specify it on the program's input.
'''

tokens_generated = '''
The tokens generated are the following:
'''

file_generaetd = '''
scanner.py generated in output folder. You may run it as `python scanner.py` in your terminal. You may as well specify any file for the scanner to read in the program input; otherwise, test_input.txt will be taken as the default file.
'''


def DumpAutomata(automata):
    pickle.dump(automata, open('./output/automata.p', 'wb'))


if __name__ == "__main__":

    grammar_file = './input/grammar.cfg'

    if len(sys.argv) > 1:
        grammar_file = sys.argv[1]

    try:
        cfg = CFG(grammar_file)
    except:
        print(f'\tERR: "{grammar_file}" file not found.')
        exit(-1)

    parser = Parser(cfg)
    tokens = parser.ToSingleExpression()
    tree = parser.Parse(tokens)

    print(f'ARBOL SINTÁCTICO:\n{tree}')

    symbols = set(
        [x for x in '.ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz()+-'])

    # Direct DFA
    ddfa = DDFA(tree, symbols, '123469504712984371298651437129')
    DumpAutomata(ddfa)
    eval_word = '1200.E-9'
    ddfa_regex = ddfa.EvalRegex(eval_word)
    print(f'\n"{eval_word}"\t=>\t{ddfa_regex}')

    eval_word = 'nuevotokensiu'
    ddfa_regex = ddfa.EvalRegex(eval_word)
    print(f'"{eval_word}"\t=>\t{ddfa_regex}')

    eval_word = 'AB(H)'
    ddfa_regex = ddfa.EvalRegex(eval_word)
    print(f'"{eval_word}"\t=>\t{ddfa_regex}')

    # ddfa.GraphAutomata()
