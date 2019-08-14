from collections import Counter
from middleout.utils import *
import array


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


class Huffman:
    """ Huffman tree compressor class """

    @staticmethod
    def max_key(d):
        v = list(d.values())
        return list(d.keys())[v.index(max(v))]

    @staticmethod
    def min_key(d):
        v = list(d.values())
        return list(d.keys())[v.index(min(v))]

    def grab_count(self, values):
        right, left = 0, 0
        for i in values:
            if i == '0': left += 1
            else: right += 1
        return left, right

    def huffman_division(self, counter):
        huffman_dictionary = {}
        for i in counter:
            size = counter[i]
            huffman_dictionary[Node(i, size)] = size
        while len(huffman_dictionary) > 2:
            smallest = Huffman.min_key(huffman_dictionary); del huffman_dictionary[smallest]
            second_smallest = Huffman.min_key(huffman_dictionary); del huffman_dictionary[second_smallest]
            smallest.merge_node(second_smallest); huffman_dictionary[smallest] = smallest.get_size()
        return Huffman.min_key(huffman_dictionary).get_set()

    def branch(self, byte_array, left_tree):
        split = ''
        right, left = array.array('B', []), array.array('B', [])
        for v in byte_array:
            if v in left_tree:
                split += '0'; left.append(v)
            else:
                split += '1'; right.append(v)
        return split, left, right

    def merge_split(self, back_transform, left, right):
        values = []
        left_count, right_count = 0, 0
        for i in back_transform:
            if i == '0':
                values.append(left[left_count]); left_count += 1
            else:
                values.append(right[right_count]); right_count += 1
        return values

    def compress(self, byte_array):
        minbits = minimum_bits(len(byte_array))
        header = unaryconverter(minbits) + unsigned_binary(len(byte_array), bits=minbits)
        huff = self.huffman_compression(byte_array)
        compressed = header + huff; pad = pad_stream(len(compressed)); num_padded = signed_bin(pad, bits=4)
        return unsigned_int_list(compressed + ('0' * pad) + num_padded)

    def decompress(self, bit_stream):
        bit_stream = remove_padding(bit_stream)
        bit_count_length = unary_to_int(bit_stream)
        compressed_bits = bit_stream[bit_count_length+1:]
        length, bit_stream = unsigned_int(compressed_bits[:bit_count_length]), compressed_bits[bit_count_length:]
        return self.huffman_decompression(bit_stream, length)[0]

    def huffman_decompression(self, bit_stream, length):
        if length == 0 or len(bit_stream) == 0:
            return [], bit_stream
        iden, bit_stream = bit_stream[0], bit_stream[1:]
        if iden == '0':
            splits, bit_stream = bit_stream[:length], bit_stream[length:]
            left_c, right_c = self.grab_count(splits)
            left, bit_stream = self.huffman_decompression(bit_stream, left_c)
            right, bit_stream = self.huffman_decompression(bit_stream, right_c)
            return self.merge_split(splits, left, right), bit_stream
        return unsigned_int_list(bit_stream[:8])*length, bit_stream[8:]

    def huffman_compression(self, byte_array):
        counts = Counter(byte_array)
        if len(counts) == 1:
            return '1' + unsigned_binary(byte_array[0])
        left_set = self.huffman_division(counts)
        split, left, right = self.branch(byte_array, left_set)
        return '0' + split + self.huffman_compression(left) + self.huffman_compression(right)


