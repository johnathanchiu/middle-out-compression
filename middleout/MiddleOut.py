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

    @staticmethod
    def count_stride_bits(bit_stream):
        return


class MiddleOutCompressor:
    """ Compressor Class """

    @staticmethod
    def byte_compression(uncompressed):
        compressed_stream = ''
        preceding, match, right = {}, [], []
        position, match_start, literal_count = 0, 0, 0
        for i in range(0, len(uncompressed) + 1):
            match.append(uncompressed[i]) if i < len(uncompressed) else match.append(0)
            match_iden = tuple(match)
            if match_iden in preceding:
                if preceding[match_iden] + MiddleOut.MAX_DISTANCE <= match_start:
                    if len(match_iden) == MiddleOut.MAX_DISTANCE:
                        match_pos = unsigned_binary(preceding[match_iden], bits=MiddleOut.BIT_DEPTH)
                        match_length = unsigned_binary(MiddleOut.MAX_DISTANCE - 2, bits=MiddleOut.DISTANCE_ENCODER)
                        compressed_stream += '0' + match_pos + match_length
                        match, match_start = [], i + 1
                else:
                    literal_count += len(match_iden)
                    compressed_stream += '1' * len(match_iden)
                    [right.append(c) for c in match]
                    match, match_start = [], i + 1
            else:
                if len(match_iden) >= 2:
                    if len(match_iden) == 2:
                        literal_count += len(match_iden)
                        compressed_stream += '1' * len(match_iden)
                        [right.append(c) for c in match]
                        match, match_start = [], i + 1
                    else:
                        hanging, match_iden = match[-1], tuple(match[:-1])
                        if match_iden in preceding:
                            match_pos = unsigned_binary(preceding[match_iden])
                            match_length = unsigned_binary(len(match_iden) - 2, bits=3)
                            compressed_stream += '0' + match_pos + match_length
                            match, match_start = [hanging], i
            if i <= len(uncompressed) - 9:
                forward_values = uncompressed[position:position + 9]
                for j in range(2, len(forward_values) + 1):
                    if tuple(forward_values[:j]) not in preceding:
                        preceding[tuple(forward_values[:j])] = position
                position += 1
        if literal_count > len(uncompressed) * 0.70:
            return '1' + unsigned_bin_list(uncompressed)
        return '0' + compressed_stream + MiddleOutCompressor.byte_compression(right)


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
                back_reference = unsigned_int(compressed[pointer + 1:pointer + 9])
                copy_length = unsigned_int(compressed[pointer + 9:pointer + 12]) + 2
                pointer += 12; decompress += decompress[back_reference:back_reference + copy_length]
        if len(decompress) == length:
            return decompress
        return decompress[:-1]


class MiddleOut:
    """ Passes values into the compressor and decompressor, pads streams """

    BIT_DEPTH = 8
    DISTANCE_ENCODER, MAX_DISTANCE = 3, 9

    @staticmethod
    def compress(byte_stream, stride=256, distance=9):
        MiddleOut.DISTANCE_ENCODER = minimum_bits(distance - 2)
        MiddleOut.BIT_DEPTH, MiddleOut.MAX_DISTANCE = minimum_bits(stride-1), distance
        partitions = split_file(byte_stream, chunksize=stride)
        with Pool(8) as p:
            compression = p.map(MiddleOutCompressor.byte_compression, partitions)
        return ''.join(compression)







