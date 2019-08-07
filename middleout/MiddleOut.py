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

    @staticmethod
    def build_library(size, byte_stream=None):
        count = 0
        dictionary = {}
        if size == len(byte_stream):
            return tuple(byte_stream[count:count + size]), size * len(byte_stream)
        if size > len(byte_stream):
            return tuple(byte_stream), -10
        while count <= len(byte_stream) - size:
            partition = tuple(byte_stream[count:count + size])
            if partition not in dictionary:
                dictionary[partition] = 1
            else:
                dictionary[partition] += 1
            count += 1
        large_occur = MiddleOutUtils.max_key(dictionary)
        ratio = dictionary[large_occur] * size / len(byte_stream) / 1.1
        return large_occur, ratio

    @staticmethod
    def count_split(values):
        l_c, r_c = 0, 0
        for i in values:
            if i == '1': r_c += 1
            else: l_c += 1
        return l_c, r_c

    @staticmethod
    def grab_count(values, total, size):
        count, ent, remaining = size*8, 0, 0
        if MiddleOutUtils.DEBUG: print(count, total)
        while ent < total:
            if values[count] == '0':
                ent += size; count += 1
            else:
                ent += 1; count += 1; remaining += 1
        return count, remaining

    @staticmethod
    def split_definer(byte_array):
        counter, split_set, occurrence_count = 0, set([]), Counter(byte_array)
        if len(occurrence_count) == 1:
            return '', byte_array, [], '0', '1'
        split_set = MiddleOutUtils.huffman_division(occurrence_count).get_set()
        if MiddleOutCompressor.MAX_LIBRARY_SIZE <= 1 or len(split_set) / len(occurrence_count) >= 0.25:
            return MiddleOutUtils.branch(byte_array, split_set)
        return '', byte_array, [], '0', '0'

    @staticmethod
    def huffman_division(counter):
        huffman_dictionary = {}
        for i in counter:
            size = counter[i]
            huffman_dictionary[Node(i, size)] = size
        while len(huffman_dictionary) > 2:
            smallest = MiddleOutUtils.min_key(huffman_dictionary); del huffman_dictionary[smallest]
            second_smallest = MiddleOutUtils.min_key(huffman_dictionary); del huffman_dictionary[second_smallest]
            smallest.merge_node(second_smallest); huffman_dictionary[smallest] = smallest.get_size()
        return MiddleOutUtils.min_key(huffman_dictionary)

    @staticmethod
    def branch(byte_array, left_tree):
        split = ''
        right, left = array.array('B', []), array.array('B', [])
        for v in byte_array:
            if v in left_tree:
                split += '0'; left.append(v)
            else:
                split += '1'; right.append(v)
        return split, left, right, '1', '0'

    @staticmethod
    def merge_split(back_transform, left, right):
        if MiddleOutUtils.DEBUG:
            print('back:', len(back_transform), 'left:', len(left), 'right:', len(right))
        values = []
        left_count, right_count = 0, 0
        for i in back_transform:
            if i == '0':
                values.append(left[left_count]); left_count += 1
            else:
                values.append(right[right_count]); right_count += 1
        return values


class MiddleOutCompressor:
    """ Compressor Class """

    BIT_DEPTH = 8
    MAX_LIBRARY_SIZE = 8
    LIBRARY_BIT_SIZE = 3
    LIBRARY_RATIO = None
    LIBRARY_LIST = None
    LIBRARY = None
    DEBUG = False

    @staticmethod
    def byte_compress(values):
        if len(values) == 0: return ''
        back_transform, left, right, split, diff = MiddleOutUtils.split_definer(values)
        if MiddleOutCompressor.DEBUG: print("split:", split == '1', "singular:", diff == '1')
        left_c, left_u = '', left; size_bits, lib = '', ''
        if split == '0':
            if diff == '1':
                left_c, left_u = positive_binary(left[0], bits=MiddleOutCompressor.BIT_DEPTH), []
            else:
                size = MiddleOutCompressor.best_library(values)
                if MiddleOutCompressor.DEBUG: print("size:", size, "library:", MiddleOutCompressor.LIBRARY)
                left_c, left_u = MiddleOutCompressor.library_compressor(values, size=size)
                size_bits = positive_binary(size - 1, bits=MiddleOutCompressor.LIBRARY_BIT_SIZE)
                lib = positiveBin_list(MiddleOutCompressor.LIBRARY, bits=MiddleOutCompressor.BIT_DEPTH)
        header = split + diff + back_transform + size_bits + lib
        left, right = MiddleOutCompressor.byte_compress(left_u), MiddleOutCompressor.byte_compress(right)
        return header + left_c + left + right

    @staticmethod
    def best_library(byte_array):
        func = partial(MiddleOutUtils.build_library, byte_stream=byte_array)
        with Pool(8) as p:
            iterable = range(1, MiddleOutCompressor.MAX_LIBRARY_SIZE)
            results = p.map(func, iterable)
            MiddleOutCompressor.LIBRARY_LIST = list(map(itemgetter(0), results))
            values = list(map(itemgetter(1), results))
        best, ratio = max(enumerate(values), key=itemgetter(1))
        MiddleOutCompressor.LIBRARY_RATIO = ratio
        MiddleOutCompressor.LIBRARY = MiddleOutCompressor.LIBRARY_LIST[best]
        return best + 1

    @staticmethod
    def library_compressor(byte_values, size=0):
        count, unc_count = 0, 0
        compressed = ''; uncompressed = []
        while count < len(byte_values):
            tup = tuple(byte_values[count:count+size])
            if tup == MiddleOutCompressor.LIBRARY:
                compressed += '0'; count += len(tup)
            else:
                compressed += '1'; uncompressed.append(byte_values[count]); count += 1
        if MiddleOutCompressor.DEBUG: print(compressed, uncompressed)
        return compressed, uncompressed


class MiddleOutDecompressor:
    """ Decompressor Class """

    DEBUG = False

    @staticmethod
    def bit_decompression(bitstream, length):
        if len(bitstream) == 0 or length == 0:
            return [], bitstream
        split, diff = bitstream[0], bitstream[1]
        bitstream = bitstream[2:]
        if split == '1':
            back_trans, bitstream = bitstream[:length], bitstream[length:]
            left_count, right_count = MiddleOutUtils.count_split(back_trans)
            left, bitstream = MiddleOutDecompressor.bit_decompression(bitstream, left_count)
            right, bitstream = MiddleOutDecompressor.bit_decompression(bitstream, right_count)
            return MiddleOutUtils.merge_split(back_trans, left, right), bitstream
        else:
            if diff == '1':
                return [positive_int(bitstream[:8])] * length, bitstream[8:]
            size_bits = positive_int(bitstream[:MiddleOutCompressor.LIBRARY_BIT_SIZE]) + 1
            bitstream = bitstream[MiddleOutCompressor.LIBRARY_BIT_SIZE:]
            part_size, remainder = MiddleOutUtils.grab_count(bitstream, length, size_bits)
            partition, bitstream = bitstream[:part_size], bitstream[part_size:]
            if MiddleOutDecompressor.DEBUG: print("length of partition:", len(partition))
            right, bitstream = MiddleOutDecompressor.bit_decompression(bitstream, remainder)
            return MiddleOutDecompressor.library_values(partition, right, size_bits), bitstream

    @staticmethod
    def library_values(stream, remaining, lib_size):
        bin_lib, stream = stream[:lib_size*8], stream[lib_size*8:]
        lib = tuple(positiveInt_list(bin_lib, bits=MiddleOutCompressor.BIT_DEPTH))
        r_count, uncompressed = 0, []
        for i in stream:
            if i == '1':
                uncompressed.append(remaining[r_count])
                r_count += 1
            else:
                uncompressed += lib
        return uncompressed


class MiddleOut:
    """ Passes values into the compressor and decompressor, pads streams"""

    PRINTER = False

    @staticmethod
    def middle_out(stream, size):
        rl_size, rl = rlepredict(stream), '0'
        if rl_size < len(stream):
            stream, rl = rle(stream), '1'
        if MiddleOut.PRINTER: print("run length:", rl == '1')
        bit_length = minimum_bits(len(stream) - 1)
        header = unaryconverter(bit_length) + positive_binary(len(stream) - 1, bits=bit_length)
        bit_length = minimum_bits(size - 1)
        lib_header = unaryconverter(bit_length) + positive_binary(size - 1, bits=bit_length)
        MiddleOutCompressor.LIBRARY_BIT_SIZE = bit_length
        MiddleOutCompressor.MAX_LIBRARY_SIZE = size + 1
        mo_compressed = rl + header + lib_header + MiddleOutCompressor.byte_compress(stream)
        return mo_compressed

    @staticmethod
    def middle_out_decomp(bit_stream):
        rl, bit_stream = bit_stream[0], bit_stream[1:]
        length_unary = unaryToInt(bit_stream)
        eof = length_unary + 1
        length = positive_int(bit_stream[eof:eof+length_unary]) + 1
        bit_stream = bit_stream[eof+length_unary:]
        length_unary = unaryToInt(bit_stream)
        eoh = length_unary + 1
        MiddleOutCompressor.LIBRARY_BIT_SIZE = minimum_bits(positive_int(bit_stream[eoh:eoh+length_unary]))
        bit_stream = bit_stream[eoh+length_unary:]
        if rl == '1': return rld(MiddleOutDecompressor.bit_decompression(bit_stream, length)[0])
        return MiddleOutDecompressor.bit_decompression(bit_stream, length)[0]

    @staticmethod
    def compress(byte_stream, size=1, debug=False):
        assert len(byte_stream) > 0, print('no values to compress')
        MiddleOutCompressor.DEBUG, MiddleOutUtils.DEBUG = debug, debug
        mo_compressed = MiddleOut.middle_out(byte_stream, size)
        pad = pad_stream(len(mo_compressed)); num_padded = convertBin(pad, bits=4)
        mo_compressed += ('0' * pad) + num_padded
        return convert_to_list(mo_compressed)


    @staticmethod
    def decompress(bit_stream, debug=False):
        MiddleOutDecompressor.DEBUG, MiddleOutUtils.DEBUG = debug, debug
        bit_stream = remove_padding(bit_stream)
        return MiddleOut.middle_out_decomp(bit_stream)
