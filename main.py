#!/usr/bin/python
import sys
from cfg_lexer import CFG
from direct_dfa import DDFA
from parsing import Parser
from utils import DumpAutomata
from code_generator import CodeGen

program_title = '''

#\tCOCOR Expression Evaluator\t#

Evaluate tokens based on a user-defined grammar file. The default grammar file is taken as input/grammar.cfg. If you want to specify a grammar of your own, you may edit the current grammar.cfg file or create a .cfg file and specify it on the program's input.

    usage:   $ python main.py [<your_cfg_file>]
    example: $ python main.py ./input/my_grammar.cfg
'''

tokens_generated = '''
The tokens generated are the following: '''

file_generated = '''
scanner.py has been generated in the root folder. You may run it as `python scanner.py` in your terminal. You may as well specify any file for the scanner to read tokens from; otherwise, ./input/test_input.txt will be taken as the default file.

    usage:   $ python scanner.py [<your_file>]
    example: $ python scanner.py ./my_file.txt
'''

if __name__ == "__main__":

    print(program_title)
    grammar_file = './input/grammar.cfg'

    if len(sys.argv) > 1:
        grammar_file = sys.argv[1]

    try:
        cfg = CFG(grammar_file)
    except Exception as e:
        print(f'\tERR: "{grammar_file}" file not found. {e}')
        exit(-1)

    parser = Parser(cfg)
    tokens = parser.ToSingleExpression()
    tree = parser.Parse(tokens)

    # print(f'ARBOL SINTÁCTICO:\n{tree}')

    symbols = set(
        [x for x in '(){}[].ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz+-_\'\"\n\r\t\\; '])

    # Direct DFA
    ddfa = DDFA(tree, symbols, cfg.keywords)
    DumpAutomata(ddfa)

    CodeGen('./scanner.py', cfg.tokens).GenerateScannerFile()

    print(file_generated)

    # ddfa.GraphAutomata()
