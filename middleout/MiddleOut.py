# Middle-Out Compression Algorithm
# © Johnathan Chiu, 2019

from collections import Counter
from middleout.utils import *
from middleout.runlength import rld, rle


class MiddleOutUtils:

    @staticmethod
    def max_key(d):
        v = list(d.values())
        k = list(d.keys())
        return k[v.index(max(v))]

    # @staticmethod
    # def build_library(byte_stream, size=2):
    #     if len(byte_stream) == 0:
    #         return None
    #     if len(byte_stream) < size:
    #         while len(byte_stream) % size != 0:
    #             byte_stream.append(0)
    #     count = 0
    #     dictionary = {}
    #     while count <= len(byte_stream) - size:
    #         partition = tuple(byte_stream[count:count + size])
    #         if partition not in dictionary:
    #             dictionary[partition] = 1
    #         else:
    #             dictionary[partition] += 1
    #         count += 1
    #     large_occur = MiddleOutUtils.max_key(dictionary)
    #     return large_occur

    @staticmethod
    def merge_split(splits, left, right, debug=False):
        if debug: print("merging", splits, left, right)
        values = []
        left_count, right_count = 0, 0
        for i in splits:
            if i == '0':
                values.append(left[left_count]); left_count += 1
            else:
                values.append(right[right_count]); right_count += 1
        return values

    @staticmethod
    def count_split(values):
        l_c, r_c = 0, 0
        for i in values:
            if i == '1': r_c += 1
            else: l_c += 1
        return l_c, r_c

    @staticmethod
    def grab_count(values, total, size=2, start_z=False):
        count = 0 if start_z else size*8
        ent, remaining = 0, 0
        while ent < total:
            if values[count] == '0':
                ent += size; count += 1
            else:
                ent += 1; count += 1; remaining += 1
        return count, remaining

    @staticmethod
    def splitter(values):
        occurence = 0
        split_set = set([])
        occurence_dict = Counter(values)
        if len(occurence_dict) == 1: return '', values, [], '1'
        while occurence / len(values) < MiddleOut.SPLIT:
            largest = MiddleOutUtils.max_key(occurence_dict)
            split_set.add(largest)
            occurence += occurence_dict[largest]
            occurence_dict[largest] = 0
        return MiddleOutUtils.branch_tree(values, split_set)

    @staticmethod
    def branch_tree(values, left_tree):
        split = ''
        right, left = array.array('B', []), array.array('B', [])
        for v in values:
            if v in left_tree: split += '0'; left.append(v)
            else: split += '1'; right.append(v)
        return split, left, right, '0'


class MiddleOut:

    SPLIT = 0.5
    LITERAL_CUTOFF = 10
    RUNLENGTH_CUTOFF = 0.3

    @staticmethod
    def decompress(stream, length, size=2, debug=False):
        if debug: print("length: ", length)
        uncompressed = []
        if len(stream) == 0 or length == 0: return uncompressed, stream
        literal, stream = stream[0], stream[1:]
        if literal == '1': return positiveInt_list(stream[:length*8]), stream[length*8:]
        rl = stream[0]; stream = stream[1:]
        if rl == '1':
            minbits = unaryToInt(stream); stream = stream[minbits+1:]
            r_c = positive_int(stream[:minbits]) + 1
            stream = stream[minbits:]
        split, stream = stream[0], stream[1:]
        if debug: print("split: ", split == '0', ", run length: ", rl == '1')
        if split == '0':
            back_transform, stream = stream[:length], stream[length:]
            if debug: print("shift: ", back_transform)
            left_count, right_count = MiddleOutUtils.count_split(back_transform)
            if debug: print("left_count: ", left_count, ", right_count: ", right_count)
            left, stream = MiddleOut.decompress(stream, left_count, size=size, debug=debug)
            if rl == '1':
                right, stream = MiddleOut.decompress(stream, r_c, size=size, debug=debug)
                right = rld(right)
            else:
                right, stream = MiddleOut.decompress(stream, right_count, size=size, debug=debug)
            if debug: print("left: ", left); print("right: ", right)
            merger = MiddleOutUtils.merge_split(back_transform, left, right)
            return merger, stream
        else:
            library, stream = stream[:8], stream[8:]
            if debug: print("library: ", library)
            minbits = unaryToInt(stream); stream = stream[minbits+1:]
            num = positive_int(stream[:minbits]) + 1; stream = stream[minbits:]
            uncompressed = [positive_int(library)] * num
            return uncompressed, stream

    # @staticmethod
    # def decompress_helper(partition, lib, remaining, size=2, debug=False):
    #     if debug: print("part: ", partition, ", lib: ", lib, ", remaining: ", remaining, "size: ", size)
    #     uncompressed = []
    #     remaining_count = 0
    #     for i in partition:
    #         if i == '1':
    #             uncompressed.append(remaining[remaining_count])
    #             remaining_count += 1
    #         else:
    #             for x in range(size):
    #                 uncompressed.append(lib[x])
    #     if debug: print("uncompressed: ", uncompressed)
    #     return uncompressed

    @staticmethod
    def byte_compression(values, size=2, debug=False):
        if len(values) == 0: return ''
        if debug: print("original values: ", values); print("remaining length: ", len(values))
        literal = '0'; split, left, right, entrop = MiddleOutUtils.splitter(values)
        if len(values) <= MiddleOut.LITERAL_CUTOFF and entrop == '0': return '1' + positiveBin_list(values, bits=8)
        if debug: print("split:", entrop == '0'); print("left length:", len(left), "right length:", len(right))
        lib, comp_l = '', ''
        if entrop == '1':
            lib, minbits = positive_binary(left[0], bits=8), minimum_bits(len(left) - 1)
            comp_l, left = unaryconverter(minbits) + positive_binary(len(left) - 1, bits=minbits), []
            if debug: print("library:", positiveInt_list(lib))
        org, right = right, rle(right); rl = '1'; right_size = len(right)
        minbits = minimum_bits(right_size - 1)
        r_encode = unaryconverter(minbits) + positive_binary(right_size - 1, bits=minbits)
        if not (right_size < int(len(org) * MiddleOut.RUNLENGTH_CUTOFF) and len(org) > 0):
            right, rl, r_encode = org, '0', ''
        header = literal + rl + r_encode + entrop + split + lib + comp_l
        if debug: print("header:", header)
        return header + MiddleOut.byte_compression(left, size=size, debug=debug) + \
               MiddleOut.byte_compression(right, size=size, debug=debug)

    @staticmethod
    def middle_out(coefficients, size=2, debug=False):
        orgsize, org, rl = len(coefficients), coefficients, '1'
        coefficients = rle(coefficients)
        if orgsize < len(coefficients):
            coefficients = org; rl = '0'
        header = positive_binary(size)
        length = len(coefficients); minbits = minimum_bits(length)
        unary = unaryconverter(minbits)
        count = positive_binary(length, minbits)
        return rl + header + unary + count + MiddleOut.byte_compression(coefficients, size=size, debug=debug)

    @staticmethod
    def middle_out_decompress(bitstream, debug=False):
        rl, bitstream = bitstream[0], bitstream[1:]
        header = positive_int(bitstream[:8])
        bitstream = bitstream[8:]
        count, unary_count = 0, unaryToInt(bitstream)
        count += unary_count + 1
        length = positive_int(bitstream[count:count+unary_count])
        bitstream = bitstream[count+unary_count:]
        if debug: print("size:", length)
        if rl == '1':
            return rld(MiddleOut.decompress(bitstream, length, size=header, debug=debug)[0])
        return MiddleOut.decompress(bitstream, length, size=header, debug=debug)[0]
