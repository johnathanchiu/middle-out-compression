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

    @staticmethod
    def build_library(byte_stream):
        count = 0
        dictionary = {}
        while count <= len(byte_stream) - MiddleOut.LIBRARY_SIZE:
            partition = tuple(byte_stream[count:count + MiddleOut.LIBRARY_SIZE])
            if partition not in dictionary:
                dictionary[partition] = 1
            else:
                dictionary[partition] += 1
            count += 1
        large_occur = MiddleOutUtils.max_key(dictionary)
        return large_occur

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
    def grab_count(values, total, start_z=False):
        count = 0 if start_z else MiddleOut.LIBRARY_SIZE*8
        ent, remaining = 0, 0
        while ent < total:
            if values[count] == '0':
                ent += MiddleOut.LIBRARY_SIZE; count += 1
            else:
                ent += 1; count += 1; remaining += 1
        return count, remaining

    @staticmethod
    def splitter(values):
        occurence = 0
        split_set = set([])
        occurence_dict = Counter(values)
        if len(occurence_dict) == 1:
            return '', values, [], '0', '1'
        while occurence / len(values) < MiddleOut.SPLIT:
            largest = MiddleOutUtils.max_key(occurence_dict)
            split_set.add(largest)
            occurence += occurence_dict[largest]
            occurence_dict[largest] = 0
        if MiddleOut.LIBRARY_SIZE < len(occurence_dict) < MiddleOut.LIBRARY_SIZE*2 and \
                0 < MiddleOut.LIBRARY_SIZE <= int(len(values) / 20):
            return '', values, [], '0', '0'
        return MiddleOutUtils.branch_tree(values, split_set)

    @staticmethod
    def branch_tree(values, left_tree):
        split = ''
        right, left = array.array('B', []), array.array('B', [])
        for v in values:
            if v in left_tree: split += '0'; left.append(v)
            else: split += '1'; right.append(v)
        return split, left, right, '1', '0'


class MiddleOut:

    SPLIT = 0.5
    LITERAL_CUTOFF = 10
    RUNLENGTH_CUTOFF = 0.3
    LIBRARY_SIZE = 0

    @staticmethod
    def decompress(stream, length, debug=False):
        if debug: print("length: ", length)
        uncompressed = []
        if len(stream) == 0 or length == 0: return uncompressed, stream
        literal, stream = stream[0], stream[1:]
        if literal == '1': return positiveInt_list(stream[:length*8]), stream[length*8:]
        rl, stream, r_c = stream[0], stream[1:], None
        if rl == '1':
            minbits = unaryToInt(stream); stream = stream[minbits+1:]
            r_c = positive_int(stream[:minbits]) + 1
            stream = stream[minbits:]
        split, entropy, stream = stream[0], stream[1], stream[2:]
        if debug: print("split:", split == '1', ", entropy: ", entropy == '1', ", run length: ", rl == '1')
        if split == '1':
            return MiddleOut.decompress_split_helper(stream, length, rl, r_c, debug=debug)
        else:
            if entropy == '1':
                return MiddleOut.decompress_entropy_helper(stream, debug=debug)
            else:
                library, stream = positiveInt_list(stream[:8*MiddleOut.LIBRARY_SIZE]), stream[8*MiddleOut.LIBRARY_SIZE:]
                if debug: print("library: ", library)
                partition_size, remaining = MiddleOutUtils.grab_count(stream, length, start_z=True)
                partition, stream = stream[:partition_size], stream[partition_size:]
                if debug:
                    print("partition size: ", partition_size, "remaining: ", remaining)
                    print("partition: ", partition); print("stream: ", stream)
                remain, stream = MiddleOut.decompress(stream, remaining, debug=debug)
                return MiddleOut.decompress_helper(partition, library, remain, debug=debug), stream

    @staticmethod
    def decompress_split_helper(stream, length, rl_iden, rl_c, debug=False):
        back_transform, stream = stream[:length], stream[length:]
        if debug: print("shift: ", back_transform)
        left_count, right_count = MiddleOutUtils.count_split(back_transform)
        if debug: print("left_count: ", left_count, ", right_count: ", right_count)
        left, stream = MiddleOut.decompress(stream, left_count, debug=debug)
        if rl_iden == '1':
            right, stream = MiddleOut.decompress(stream, rl_c, debug=debug)
            right = rld(right)
        else:
            right, stream = MiddleOut.decompress(stream, right_count, debug=debug)
        if debug: print("left: ", left); print("right: ", right)
        return MiddleOutUtils.merge_split(back_transform, left, right), stream

    @staticmethod
    def decompress_entropy_helper(stream, debug=False):
        library, stream = stream[:8], stream[8:]
        if debug: print("library: ", library)
        minbits = unaryToInt(stream); stream = stream[minbits+1:]
        num = positive_int(stream[:minbits]) + 1; stream = stream[minbits:]
        uncompressed = [positive_int(library)] * num
        return uncompressed, stream

    @staticmethod
    def decompress_helper(partition, lib, remaining, debug=False):
        if debug: print("part: ", partition, ", lib: ", lib)
        uncompressed, remaining_count = [], 0
        for i in partition:
            if i == '1':
                uncompressed.append(remaining[remaining_count])
                remaining_count += 1
            else:
                for x in range(MiddleOut.LIBRARY_SIZE):
                    uncompressed.append(lib[x])
        if debug: print("uncompressed: ", uncompressed)
        return uncompressed

    @staticmethod
    def byte_compression(values, debug=False):
        if len(values) == 0: return ''
        if debug: print("original values: ", values); print("remaining length: ", len(values))
        literal = '0'; back_transform, left, right, split, entrop = MiddleOutUtils.splitter(values)
        if len(values) <= MiddleOut.LITERAL_CUTOFF and entrop == '0': return '1' + positiveBin_list(values, bits=8)
        if debug:
            print("split:", split == '1', ", entropy:", entrop == '1')
            print("left length:", len(left), "right length:", len(right))
        lib, comp_l = '', ''
        if split == '0':
            if entrop == '1':
                lib, minbits = positive_binary(left[0], bits=8), minimum_bits(len(left) - 1)
                comp_l, left = unaryconverter(minbits) + positive_binary(len(left) - 1, bits=minbits), []
                if debug: print("library:", positiveInt_list(lib))
            else:
                l_ = MiddleOutUtils.build_library(left)
                lib = '' if l_ is None else positiveBin_list(l_, bits=8)
                comp_l, left = MiddleOut.middle_out_helper(left, l_, debug=debug)
        org, right = right, rle(right); rl = '1'; right_size = len(right)
        minbits = minimum_bits(right_size - 1)
        r_encode = unaryconverter(minbits) + positive_binary(right_size - 1, bits=minbits)
        if not (right_size < int(len(org) * MiddleOut.RUNLENGTH_CUTOFF) and len(org) > 0):
            right, rl, r_encode = org, '0', ''
        header = literal + rl + r_encode + split + entrop + back_transform + lib + comp_l
        if debug: print("header:", header)
        return header + MiddleOut.byte_compression(left, debug=debug) + \
               MiddleOut.byte_compression(right, debug=debug)

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, debug=False):
        if debug: print("partitioned stream: ", byte_stream, ", ", "library: ", compression_dict)
        count, unc_count = 0, 0
        compressed = ''; uncompressed = []
        while count < len(byte_stream):
            tup = tuple(byte_stream[count:count+MiddleOut.LIBRARY_SIZE])
            if tup == compression_dict:
                compressed += '0'; count += len(tup)
            else:
                compressed += '1'; uncompressed.append(byte_stream[count]); count += 1
        return compressed, uncompressed

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
        MiddleOut.LIBRARY_SIZE = size
        return rl + header + unary + count + MiddleOut.byte_compression(coefficients, debug=debug)

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
        MiddleOut.LIBRARY_SIZE = header
        if rl == '1':
            return rld(MiddleOut.decompress(bitstream, length, debug=debug)[0])
        return MiddleOut.decompress(bitstream, length, debug=debug)[0]
