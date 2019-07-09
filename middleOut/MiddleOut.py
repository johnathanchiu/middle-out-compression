from collections import Counter
from middleOut.utils import *


class MiddleOutUtils:
    @staticmethod
    def max_key(d):
        v = list(d.values())
        k = list(d.keys())
        return k[v.index(max(v))]

    @staticmethod
    def build_library(byte_stream, size=2, debug=False):
        count = 0
        dictionary = {}
        if len(byte_stream) < size:
            for _ in range(size - len(byte_stream)):
                temp = list([0])
                temp.extend(byte_stream)
                byte_stream = temp
        while count <= len(byte_stream) - size:
            partition = tuple(byte_stream[count:count + size])
            if partition not in dictionary:
                dictionary[partition] = 1
            else:
                dictionary[partition] += 1
            count += 1
        large_occur = MiddleOutUtils.max_key(dictionary)
        return large_occur

    @staticmethod
    def make_count(byte_stream):
        return Counter(byte_stream)


class MiddleOut:

    SPLIT = 0.5

    @staticmethod
    def decompress(values):
        return


    @staticmethod
    def middle_out_helper(byte_stream, compression_dict):
        count, unc_count = 0, 0
        compressed = ''
        uncompressed = []
        while count < len(byte_stream):
            compressor = 2
            tup = tuple(byte_stream[count:count+compressor])
            if tup != compression_dict:
                compressed += '1'
                uncompressed.append(byte_stream[count])
            else:
                compressed += '0'
            count += len(tup)
        return compressed, uncompressed

    @staticmethod
    def byte_compression(values, size=2):
        if len(values) == 0:
            return ''
        if len(values) < size:
            while len(values) % size != 0:
                values.append(0)
            split, left, right = '', values, []
        else:
            split, left, right = MiddleOut.splitter(values)
        l_, r_ = MiddleOutUtils.build_library(left, size=size), MiddleOutUtils.build_library(right, size=size)
        left_lib, right_lib = convertBin_list(l_, bits=8), convertBin_list(r_, bits=8)
        comp_l, uncomp_l = MiddleOut.middle_out_helper(left, l_)
        comp_r, uncomp_r = MiddleOut.middle_out_helper(right, r_)
        stream_l = split + left_lib + comp_l
        stream_r = right_lib + comp_r
        return stream_l + MiddleOut.byte_compression(uncomp_l) + stream_r + MiddleOut.byte_compression(uncomp_r)

    @staticmethod
    def splitter(values):
        occurence = 0
        split_set = set([])
        occurence_dict = MiddleOutUtils.make_count(values)
        while occurence / len(values) < MiddleOut.SPLIT:
            largest = MiddleOutUtils.max_key(occurence_dict)
            split_set.add(largest)
            occurence += occurence_dict[largest]
            occurence_dict[largest] = 0
        return MiddleOut.branch_tree(values, split_set)

    @staticmethod
    def branch_tree(values, left_tree_values):
        split = ''
        right, left = array.array('b', []), array.array('b', [])
        for v in values:
            if v in left_tree_values:
                split += '0'
                left.append(v)
            else:
                split += '1'
                right.append(v)
        return split, left, right

    @staticmethod
    def middle_out(coefficients, size=2):
        return MiddleOut.byte_compression(coefficients, size=size)

    @staticmethod
    def middle_out_decompress(compressed, size=2):
        return
