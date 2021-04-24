from pprint import pprint
from utils import WriteToFile
from pythomata import SimpleDFA
from graphviz import Digraph

RAW_STATES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'


class DDFA:
    def __init__(self, tree, symbols, keywords, ignore_set):

        # Useful for syntax tree
        self.nodes = list()

        # FA properties
        self.symbols = symbols
        self.states = list()
        self.trans_func = dict()
        self.accepting_states = set()
        self.accepting_dict = dict()
        self.initial_state = 'A'
        self.keywords = keywords
        self.keywords_value = [
            keyword.value.value for keyword in self.keywords]
        self.ignore_set = ignore_set

        # Class properties
        self.tree = tree
        self.augmented_states = None
        self.iter = 1

        self.STATES = iter(RAW_STATES)

        # Initialize dfa construction
        self.ParseTree(self.tree)
        self.CalcFollowPos()

    def CalcFollowPos(self):
        for node in self.nodes:
            if node.value == '*':
                for i in node.lastpos:
                    child_node = next(filter(lambda x: x._id == i, self.nodes))
                    child_node.followpos += node.firstpos
            elif node.value == '.':
                for i in node.c1.lastpos:
                    child_node = next(filter(lambda x: x._id == i, self.nodes))
                    child_node.followpos += node.c2.firstpos

        # Initiate state generation
        initial_state = self.nodes[-1].firstpos

        # Filter the nodes that have a symbol
        self.nodes = list(filter(lambda x: x._id, self.nodes))

        # Get all the nodes with the symbol '#'.
        self.augmented_states = list(
            filter(lambda x: '#-' in x.value, self.nodes))

        self.augmented_states = set(
            [node._id for node in self.augmented_states])

        # Recursion
        self.CalcNewStates(initial_state, next(self.STATES))

    def CalcNewStates(self, state, curr_state):

        if not self.states:
            self.states.append(set(state))

            # If state in set(self.augmented_states).
            if state in list(self.augmented_states):
                self.accepting_dict[curr_state] = state
                self.accepting_states.update(curr_state)

        # Iteramos por cada símbolo
        for symbol in self.symbols:

            # Get all the nodes with the same symbol in followpos
            same_symbols = list(
                filter(lambda x: symbol in x.value and x._id in state, self.nodes))

            # Create a new state with the nodes
            new_state = set()
            for node in same_symbols:
                new_state.update(node.followpos)

            # new state is not in the state list
            if new_state not in self.states and new_state:

                # Get this new state's letter
                self.states.append(new_state)
                next_state = next(self.STATES)

                # Add state to transition function
                try:
                    self.trans_func[next_state]
                except:
                    self.trans_func[next_state] = dict()

                try:
                    existing_states = self.trans_func[curr_state]
                except:
                    self.trans_func[curr_state] = dict()
                    existing_states = self.trans_func[curr_state]

                # Add the reference
                existing_states[symbol] = next_state
                self.trans_func[curr_state] = existing_states

                # Is it an accepting_state?
                if bool(self.augmented_states & new_state):
                    self.accepting_states.update(next_state)
                    self.accepting_dict[next_state] = new_state

                # Repeat with this new state
                self.CalcNewStates(new_state, next_state)

            elif new_state:
                # State already exists... which one is it?
                for i in range(0, len(self.states)):

                    if self.states[i] == new_state:
                        state_ref = RAW_STATES[i]
                        break

                # Add the symbol transition
                try:
                    existing_states = self.trans_func[curr_state]
                except:
                    self.trans_func[curr_state] = {}
                    existing_states = self.trans_func[curr_state]

                existing_states[symbol] = state_ref
                self.trans_func[curr_state] = existing_states

    def ParseTree(self, node):
        method_name = node.__class__.__name__ + 'Node'
        method = getattr(self, method_name)
        return method(node)

    def SymbolNode(self, node):
        new_node = Node(self.iter, [self.iter], [self.iter],
                        value=node.value, nullable=False)
        self.nodes.append(new_node)
        return new_node

    def OrNode(self, node):
        node_a = self.ParseTree(node.a)
        self.iter += 1
        node_b = self.ParseTree(node.b)

        is_nullable = node_a.nullable or node_b.nullable
        firstpos = node_a.firstpos + node_b.firstpos
        lastpos = node_a.lastpos + node_b.lastpos

        new_node = Node(None, firstpos, lastpos,
                        is_nullable, '|', node_a, node_b)

        self.nodes.append(new_node)
        return new_node

    def AppendNode(self, node):
        node_a = self.ParseTree(node.a)
        self.iter += 1
        node_b = self.ParseTree(node.b)

        is_nullable = node_a.nullable and node_b.nullable
        if node_a.nullable:
            firstpos = node_a.firstpos + node_b.firstpos
        else:
            firstpos = node_a.firstpos

        if node_b.nullable:
            lastpos = node_b.lastpos + node_a.lastpos
        else:
            lastpos = node_b.lastpos

        new_node = Node(None, firstpos, lastpos,
                        is_nullable, '.', node_a, node_b)

        self.nodes.append(new_node)
        return new_node

    def KleeneNode(self, node):
        node_a = self.ParseTree(node.a)
        firstpos = node_a.firstpos
        lastpos = node_a.lastpos
        new_node = Node(None, firstpos, lastpos, True, '*', node_a)
        self.nodes.append(new_node)
        return new_node

    def BracketNode(self, node):
        # Node_a is epsilon
        node_a = Node(None, list(), list(), True)
        # self.iter += 1
        node_b = self.ParseTree(node.a)

        is_nullable = node_a.nullable or node_b.nullable
        firstpos = node_a.firstpos + node_b.firstpos
        lastpos = node_a.lastpos + node_b.lastpos

        new_node = Node(None, firstpos, lastpos,
                        is_nullable, '|', node_a, node_b)
        self.nodes.append(new_node)
        return new_node

    def EvalRegex(self, word):
        curr_state = 'A'
        for symbol in word:

            if not symbol in self.symbols:
                return 'None'

            try:
                curr_state = self.trans_func[curr_state][symbol]
            except:
                return 'None'

        if curr_state not in self.accepting_states:
            return 'None'

        gen_state = self.accepting_dict[curr_state]
        token = next(
            filter(lambda x: '#-' in x.value and x._id in gen_state, self.nodes))

        token_type = token.value.split('#-')[1]
        return f'{token_type}'

    def GraphAutomata(self):
        states = set(self.trans_func.keys())
        alphabet = set(self.symbols)

        dfa = SimpleDFA(states, alphabet, self.initial_state,
                        self.accepting_states, self.trans_func)

        graph = dfa.trim().to_graphviz()
        graph.attr(rankdir='LR')

        source = graph.source
        WriteToFile('./output/DirectDFA.gv', source)
        graph.render('./output/DirectDFA.gv', format='pdf', view=True)


class Node:
    def __init__(self, _id, firstpos=None, lastpos=None, nullable=False, value=None, c1=None, c2=None):
        self._id = _id
        self.firstpos = firstpos
        self.lastpos = lastpos
        self.followpos = list()
        self.nullable = nullable
        self.value = value
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return f'''
    id: {self._id}
    value: {self.value}
    firstpos: {self.firstpos}
    lastpos: {self.lastpos}
    followpos: {self.followpos}
    nullabe: {self.nullable}
    '''
