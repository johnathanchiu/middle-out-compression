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
        if debug:
            print("largest occurring:", large_occur, ", ",
                  "size of byte stream:", len(byte_stream))
        return large_occur

    @staticmethod
    def make_count(byte_stream):
        return Counter(byte_stream)

    @staticmethod
    def build_dict(byte_lib):
        return {byte_lib: '0'}


class MiddleOut:

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, debug=False):
        if debug: print("current length:", len(byte_stream))
        count, unc_count = 0, 0
        compressed = ''
        uncompressed = []
        while count < len(byte_stream):
            compressor = 1
            tup = tuple(byte_stream[count:count+compressor])
            while tup in compression_dict and count+compressor < len(byte_stream)+1:
                compressor += 1
                tup = tuple(byte_stream[count:count+compressor])
            if len(tup) > 1:
                tup = tuple(byte_stream[count:count+compressor-1])
            if tup not in compression_dict:
                compressed += '1'
                uncompressed.append(byte_stream[count])
            else:
                compressed += compression_dict[tup]
            count += len(tup)
        if debug: print("bitstream length:", len(compressed), compressed)
        return compressed, uncompressed

    @staticmethod
    def byte_compression(values, size=2):
        if len(values) == 0:
            return ''
        split, left, right = MiddleOut.splitter(values)
        l_, r_ = MiddleOutUtils.build_library(left, size=size), MiddleOutUtils.build_library(right, size=size)
        l_dict, r_dict = MiddleOutUtils.build_dict(l_), MiddleOutUtils.build_dict(r_)
        comp_l, uncomp_l = MiddleOut.middle_out_helper(left, l_dict)
        comp_r, uncomp_r = MiddleOut.middle_out_helper(right, r_dict)
        return split + comp_l + MiddleOut.byte_compression(uncomp_l) + comp_r + MiddleOut.byte_compression(uncomp_r)

    @staticmethod
    def splitter(values):
        occurence = 0
        split_set = set([])
        occurence_dict = MiddleOutUtils.make_count(values)
        print(occurence_dict)
        occurence_dict = MiddleOutUtils.max_key(occurence_dict)
        while occurence / len(values) < 0.5:
            largest = MiddleOutUtils.max_key(occurence_dict)
            split_set.add(largest)
            occurence += occurence_dict[largest]
            occurence_dict[largest] = 0
        return MiddleOut.branch_tree(values, split_set)

    @staticmethod
    def branch_tree(values, left_tree_values):
        split = ''
        right, left = array.array('b', []), array.array('b', [])
        left_tree_values = set(left_tree_values)
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
        while len(coefficients) % size != 0:
            coefficients.append(0)
        return MiddleOut.byte_compression(coefficients, size=size)
