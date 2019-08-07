
class Node:
    """ Huffman tree building helper """

    def __init__(self, symbol, size):
        self.size = size
        self.symbols = [symbol]

    def merge_node(self, nodes):
        """ merge node passed in args """
        self.symbols += nodes.get_symbols()
        self.size += nodes.size

    def get_symbols(self):
        """ return symbols"""
        return self.symbols

    def get_size(self):
        """ return size of node """
        return self.size

    def get_set(self):
        """ return symbols of node as set """
        return set(self.symbols)

    def __repr__(self):
        return str(self.symbols)

    def __eq__(self, other):
        return self.symbols == other.get_symbols()

    def __hash__(self):
        return self.size % 4
