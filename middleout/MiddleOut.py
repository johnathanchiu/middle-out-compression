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
    def build_library(byte_stream, size=2):
        if len(byte_stream) == 0:
            return None
        if len(byte_stream) < size:
            while len(byte_stream) % size != 0:
                byte_stream.append(0)
        count = 0
        dictionary = {}
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
            if i == '1':
                r_c += 1
            else:
                l_c += 1
        return l_c, r_c

    @staticmethod
    def single_split(values, total, size=2):
        count, tracer, right = 0, 0, 0
        while count < total:
            if values[tracer] == '1':
                count += 1; right += 1
            else:
                count += size
            tracer += 1
        return tracer, right

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
    def splitter(values, debug=False):
        occurence = 0
        split_set = set([])
        occurence_dict = Counter(values)
        if len(occurence_dict) == 1: return '', values, [], '0', '1'
        while occurence / len(values) < MiddleOut.SPLIT:
            largest = MiddleOutUtils.max_key(occurence_dict)
            split_set.add(largest)
            occurence += occurence_dict[largest]
            occurence_dict[largest] = 0
        return MiddleOutUtils.branch_tree(values, split_set)

    @staticmethod
    def branch_tree(values, left_tree_values):
        split = ''
        right, left = array.array('B', []), array.array('B', [])
        if len(values) <= MiddleOut.UPPER_THRESH: return '', values, right, '0', '0'
        for v in values:
            if v in left_tree_values: split += '0'; left.append(v)
            else: split += '1'; right.append(v)
        return split, left, right, '1', '0'


class MiddleOut:

    SPLIT = 0.5
    LOWER_THRESH = 8
    UPPER_THRESH = 40
    LITERAL_CUTOFF = 40

    @staticmethod
    def decompress(stream, length, size=2, debug=False):
        if debug: print("length: ", length, ", stream: ", stream)
        uncompressed = []
        if len(stream) == 0 or length == 0: return uncompressed, stream
        literal, stream = stream[0], stream[1:]
        if literal == '1': return positiveInt_list(stream[:length*8]), stream[length*8:]
        rl = stream[0]; stream = stream[1:]
        split, entropy, stream = stream[0], stream[1], stream[2:]
        if debug: print("split: ", split, "entropy: ", entropy)
        if split == '1':
            back_transform, stream = stream[:length], stream[length:]
            if debug: print("shift: ", back_transform)
            left_count, right_count = MiddleOutUtils.count_split(back_transform)
            if debug: print("left_count: ", left_count, ", right_count: ", right_count)
            left, stream = MiddleOut.decompress(stream, left_count, size=size, debug=debug)
            right, stream = MiddleOut.decompress(stream, right_count, size=size, debug=debug)
            if debug: print("left: ", left); print("right: ", right)
            return MiddleOutUtils.merge_split(back_transform, left, right), stream
        else:
            if entropy == '1':
                library, stream = stream[:8], stream[8:]
                if debug: print("library: ", library); print("remaining stream: ", stream)
                minbits = unaryToInt(stream); stream = stream[minbits+1:]
                num = positive_int(stream[:minbits]) + 1; stream = stream[minbits:]
                uncompressed = [positive_int(library)] * num
            else:
                library, stream = positiveInt_list(stream[:8*size]), stream[8*size:]
                if debug: print("library: ", library)
                partition_size, remaining = MiddleOutUtils.grab_count(stream, length, size=size, start_z=True)
                partition, stream = stream[:partition_size], stream[partition_size:]
                if debug:
                    print("partition size: ", partition_size, "remaining: ", remaining)
                    print("partition: ", partition); print("stream: ", stream)
                rg = length if length < size else size
                remain, stream = MiddleOut.decompress(stream, remaining, size=size, debug=debug)
                uncompressed = MiddleOut.decompress_helper(partition, library, remain, size=rg, debug=debug)
            return uncompressed, stream

    @staticmethod
    def decompress_helper(partition, lib, remaining, size=2, debug=False):
        if debug: print("part: ", partition, ", lib: ", lib, ", remaining: ", remaining, "size: ", size)
        uncompressed = []
        remaining_count = 0
        for i in partition:
            if i == '1':
                uncompressed.append(remaining[remaining_count])
                remaining_count += 1
            else:
                for x in range(size):
                    uncompressed.append(lib[x])
        if debug: print("uncompressed: ", uncompressed)
        return uncompressed

    @staticmethod
    def byte_compression(values, size=2, debug=False):
        if debug: print("original values: ", values); print("remaining length: ", len(values))
        if len(values) == 0: return ''
        if len(values) <= size:
            while len(values) % size != 0: values.append(0)
        literal = '0'; split, left, right, split_iden, entropy = MiddleOutUtils.splitter(values, debug=debug)
        if len(values) <= MiddleOut.LITERAL_CUTOFF and entropy == '0': return '1' + positiveBin_list(values, bits=8)
        if debug: print("split size: ", len(split), ", entropy: ", entropy, ", split: ", split_iden)
        lib, comp_l, uncomp_l = '', '', left
        if split_iden == '0':
            if entropy == '1':
                lib, minbits = positive_binary(left[0], bits=8), minimum_bits(len(left) - 1)
                comp_l, uncomp_l = unaryconverter(minbits) + positive_binary(len(left) - 1, bits=minbits), []
            else:
                l_ = MiddleOutUtils.build_library(left, size=size)
                lib = '' if l_ is None else positiveBin_list(l_, bits=8)
                comp_l, uncomp_l = MiddleOut.middle_out_helper(left, l_, size=size, debug=debug)
        if debug: print("library:", positiveInt_list(lib))
        rl, r_encode = '0', ''
        header = literal + rl + r_encode + split_iden + entropy + split + lib + comp_l
        return header + MiddleOut.byte_compression(uncomp_l, size=size, debug=debug) + \
               MiddleOut.byte_compression(right, size=size, debug=debug)

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, size=2, debug=False):
        if debug: print("partitioned stream: ", byte_stream, ", ", "library: ", compression_dict)
        count, unc_count = 0, 0
        compressed = ''; uncompressed = []
        if compression_dict is None:
            return compressed, byte_stream
        while count < len(byte_stream):
            tup = tuple(byte_stream[count:count+size])
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
        if debug: print("size:", length, ",", "compressed stream:", bitstream)
        if rl == '1':
            return rld(MiddleOut.decompress(bitstream, length, size=header, debug=debug)[0])
        return MiddleOut.decompress(bitstream, length, size=header, debug=debug)[0]
