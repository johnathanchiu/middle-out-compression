from collections import Counter
from middleOut.utils import *


class MiddleOutUtils:
    @staticmethod
    def max_key(d):
        v = list(d.values())
        k = list(d.keys())
        return k[v.index(max(v))]

    @staticmethod
    def build_library(byte_stream, size=2):
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

    @staticmethod
    def insert_libraries(partition, library, size=2):
        uncompressed, values = [], partition[size*8:]
        for i in values:
            if i == '1':
                return
            else:
                uncompressed.append(library[0])
                uncompressed.append(library[1])
        return uncompressed

    @staticmethod
    def merge_split(splits, left, right):
        values = []
        left_count, right_count = 0, 0
        for i in splits:
            if i == '1':
                values.append(left[left_count])
                left_count += 1
            else:
                values.append(right[right_count])
                right_count += 1
        return values

    @staticmethod
    def count_split(values, length):
        l_c, r_c, count = 0, 0, 0
        while count < length:
            if values[count] == '1':
                r_c += 1
            else:
                l_c += 1
            count += 1
        return l_c, r_c

    @staticmethod
    def grab_count(values, total, size=2):
        count, ent = size*8, 0
        while ent < total:
            if values[count] == '0':
                ent += 1; count += 1
            else:
                ent += 2; count += 1
        return count


class MiddleOut:

    SPLIT = 0.5

    @staticmethod
    def decompress(values, length, size=2):
        uncompressed = []
        if length == 0:
            return uncompressed
        iden, values = values[0], values[2:]
        if iden == '1':
            split, values = values[:length], values[length:]
            left_count, right_count = MiddleOutUtils.count_split(values, length)
            left_grab = MiddleOutUtils.grab_count(values, left_count)
            left_partition, left_lib, values = values[:left_grab], values[:size*8], values[left_grab:]
            right_grab = MiddleOutUtils.grab_count(values, right_count)
            right_partition, right_lib, values = values[:right_grab], values[:size*8], values[right_grab:]
            left = MiddleOut.decompress_helper(left_partition, left_lib)
            right = MiddleOut.decompress_helper(right_partition, right_lib)
            uncompressed = MiddleOutUtils.merge_split(split, left, right)
        else:
            lib = convertInt_list(values[:size*8], bits=8)
            return lib[:length]
        return uncompressed

    @staticmethod
    def decompress_helper(partition, lib):
        return MiddleOutUtils.insert_libraries(partition, lib)

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, size=2):
        count, unc_count = 0, 0
        compressed = ''
        uncompressed = []
        while count < len(byte_stream):
            tup = tuple(byte_stream[count:count+size])
            if tup != compression_dict:
                compressed += '1'
                uncompressed.append(byte_stream[count])
            else:
                compressed += '0'
            count += len(tup)
        return compressed, uncompressed

    @staticmethod
    def byte_compression(values, size=2, debug=False):
        if len(values) == 0:
            return ''
        if len(values) <= size:
            while len(values) % size != 0:
                values.append(0)
            iden, split, left, right = '0', '', values, []
        else:
            iden = '1'; split, left, right = MiddleOut.splitter(values)
        l_, r_ = MiddleOutUtils.build_library(left, size=size), MiddleOutUtils.build_library(right, size=size)
        left_lib, right_lib = convertBin_list(l_, bits=8), convertBin_list(r_, bits=8)
        comp_l, uncomp_l = MiddleOut.middle_out_helper(left, l_)
        comp_r, uncomp_r = MiddleOut.middle_out_helper(right, r_)
        stream_l = left_lib + comp_l; stream_r = right_lib + comp_r
        if debug:
            print("left side values: ", left_lib, ", ", comp_l)
            print("right side values: ", right_lib, ", ", comp_r)
        return iden + split + stream_l + stream_r + MiddleOut.byte_compression(uncomp_l) +\
               MiddleOut.byte_compression(uncomp_r)

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
        header = positive_binary(size)
        length = len(coefficients); minbits = minimum_bits(length)
        unary = unaryconverter(minbits)
        count = positive_binary(length, minbits)
        return header + unary + count + MiddleOut.byte_compression(coefficients, size=size)

    @staticmethod
    def middle_out_decompress(compressed, size=2):
        return
#
# @staticmethod
# def middle_out_decompress(bitstream, debug=False):
#     header = positive_int(bitstream[:8])
#     bitstream = bitstream[8:]
#     count, unary_count = 0, unaryToInt(bitstream)
#     count += unary_count + 1
#     length = positive_int(bitstream[count:count+unary_count])
#     bitstream = bitstream[count+unary_count:]
#     if debug: print("size:", length, ",", "compressed stream:", bitstream)
#     return MiddleOut.decompress(bitstream, length, size=header, debug=debug)
#
