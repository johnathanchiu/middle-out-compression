# Middle-Out Compression Algorithm
# © Johnathan Chiu, 2019

from middleout.runlength import rld, rle, rlepredict
from middleout.modified_huffman import Node
from middleout.utils import *

from collections import Counter
from functools import partial
from multiprocessing import Pool
from operator import itemgetter


class MiddleOutUtils:
    """ Utilities class used for middle out compression """

    DEBUG = True

    @staticmethod
    def max_key(d):
        v = list(d.values())
        return list(d.keys())[v.index(max(v))]

    @staticmethod
    def min_key(d):
        v = list(d.values())
        return list(d.keys())[v.index(min(v))]


class MiddleOutCompressor:
    """ Compressor Class """

    @staticmethod
    def lempel_ziv_derivative(uncompressed):
        compressed_stream = ''
        position, match_start = 0, 0
        preceding, match, right = {}, [], []
        for i in range(0, len(uncompressed) + 1):
            match.append(uncompressed[i]) if i < len(uncompressed) else match.append(0)
            match_iden = tuple(match)
            if match_iden in preceding:
                if preceding[match_iden] + 9 <= match_start:
                    if len(match_iden) == 9:
                        match_size = positive_binary(7, bits=3)
                        match_pos = positive_binary(preceding[match_iden], bits=MiddleOut.BIT_DEPTH)
                        compressed_stream += '0' + match_pos + match_size
                        match, match_start = [], i + 1
                else:
                    compressed_stream += '1' * len(match_iden)
                    [right.append(c) for c in match]
                    match, match_start = [], i + 1
            else:
                if len(match_iden) >= 2:
                    if len(match_iden) == 2:
                        compressed_stream += '1' * len(match_iden)
                        [right.append(c) for c in match]
                        match, match_start = [], i + 1
                    else:
                        hanging, match_iden = match[-1], tuple(match[:-1])
                        if match_iden in preceding:
                            match_size = positive_binary(len(match_iden) - 2, bits=3)
                            match_pos = positive_binary(preceding[match_iden], bits=MiddleOut.BIT_DEPTH)
                            compressed_stream += '0' + match_pos + match_size
                            match, match_start = [hanging], i
            if i <= len(uncompressed) - 9:
                forward_values = uncompressed[position:position + 9]
                for j in range(2, len(forward_values) + 1):
                    if tuple(forward_values[:j]) not in preceding:
                        preceding[tuple(forward_values[:j])] = position
                position += 1
        return compressed_stream, right


class MiddleOutDecompressor:
    """ Decompressor Class """

    @staticmethod
    def helper_decomp(compressed, right, length):
        decompress, pointer, right_pos = [], 0, 0
        while pointer < len(compressed):
            if compressed[pointer] == '1':
                decompress.append(right[right_pos])
                right_pos += 1; pointer += 1
            else:
                back_reference = positive_int(compressed[pointer + 1:pointer + 9])
                copy_length = positive_int(compressed[pointer + 9:pointer + 12]) + 2
                pointer += 12
                decompress += decompress[back_reference:back_reference + copy_length]
        if len(decompress) == length:
            return decompress
        return decompress[:-1]


class MiddleOut:
    """ Passes values into the compressor and decompressor, pads streams """

    BIT_DEPTH = 8






