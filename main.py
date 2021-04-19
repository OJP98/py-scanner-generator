from cfg_lexer import CFG
from parsing import Parser
from direct_dfa import DDFA
import pickle

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

cfg = CFG('input/grammar.cfg')
parser = Parser(cfg)

# pprint(cfg.tokens)

tokens = parser.ToSingleExpression()

# print(cfg)
# print(tokens)

tree = parser.Parse(tokens)
print(f'\nARBOL SINTÁCTICO:\n{tree}')

symbols = set(
    [x for x in '.ABCDEFGHOL0123456789abcdefghijklmnopqrstuvwxyz()1234567890+-'])

ddfa = DDFA(tree, symbols, '123469504712984371298651437129')

# print(ddfa.nodes)
# print('states:', ddfa.states)
# print('accepting states:', ddfa.accepting_states)
# print('accepting dict:', ddfa.accepting_dict)
# print('augmented states:', ddfa.augmented_states)
# pprint(ddfa.trans_func)

ddfa_regex = ddfa.EvalRegex('adios')
print(ddfa_regex)
pickle.dump(ddfa, open('./output/automata.p', 'wb'))
# ddfa.GraphAutomata()
