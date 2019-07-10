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
    def make_count(byte_stream):
        return Counter(byte_stream)

    @staticmethod
    def merge_split(splits, left, right):
        values = []
        left_count, right_count = 0, 0
        for i in splits:
            if i == '0':
                values.append(left[left_count])
                left_count += 1
            else:
                values.append(right[right_count])
                right_count += 1
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
    def grab_count(values, total, size=2):
        count, ent, remaining = size*8, 0, 0
        while ent < total:
            if values[count] == '0':
                ent += 2; count += 1
            else:
                ent += 1; count += 1
                remaining += 1
        return count, remaining

    @staticmethod
    def splitter(values, debug=False):
        occurence = 0
        split_set = set([])
        occurence_dict = MiddleOutUtils.make_count(values)
        while occurence / len(values) < MiddleOut.SPLIT:
            largest = MiddleOutUtils.max_key(occurence_dict)
            split_set.add(largest)
            occurence += occurence_dict[largest]
            occurence_dict[largest] = 0
        if debug: print("split set: ", split_set)
        return MiddleOutUtils.branch_tree(values, split_set)

    @staticmethod
    def branch_tree(values, left_tree_values):
        split = ''
        right, left = array.array('b', []), array.array('b', [])
        if len(left_tree_values) == 1:
            return split, values, right, '0'
        for v in values:
            if v in left_tree_values:
                split += '0'
                left.append(v)
            else:
                split += '1'
                right.append(v)
        return split, left, right, '1'


class MiddleOut:

    SPLIT = 0.3

    @staticmethod
    def decompress(stream, length, size=2, debug=False):
        if debug: print("stream: ", stream, "expected length: ", length)
        uncompressed = []
        if length == 0:
            return uncompressed, stream
        iden, stream = stream[0], stream[1:]
        if iden == '1':
            split, stream = stream[:length], stream[length:]
            if debug: print("split: ", split)
            left_count, right_count = MiddleOutUtils.count_split(split)
            if debug: print("left count: ", left_count, ", right count: ", right_count)
            left_grab, remainder = MiddleOutUtils.grab_count(stream, left_count)
            if debug: print("left grab: ", left_grab, "remainder: ", remainder)
            left_partition, left_lib, stream = stream[size*8:left_grab], \
                                               convertInt_list(stream[:size*8], bits=8), stream[left_grab:]
            if debug: print("left library: ", left_lib, ", left partition: ", left_partition)
            remaining, stream = MiddleOut.decompress(stream, remainder, size=size, debug=debug)
            left = MiddleOut.decompress_helper(left_partition, left_lib, remaining)
            if debug: print("remaining: ", remaining, ", right stream: ", stream); print("left: ", left)
            right_grab, remainder = MiddleOutUtils.grab_count(stream, right_count)
            if debug: print("right grab: ", right_grab, "remainder: ", remainder)
            right_partition, right_lib, stream = stream[size*8:right_grab], \
                                                 convertInt_list(stream[:size*8], bits=8), stream[right_grab:]
            if debug: print("right library: ", right_lib, ", right partition: ", right_partition)
            remaining, stream = MiddleOut.decompress(stream, remainder, size=size, debug=debug)
            right = MiddleOut.decompress_helper(right_partition, right_lib, remaining)
            if debug: print("right: ", right)
            uncompressed = MiddleOutUtils.merge_split(split, left, right)
            return uncompressed, stream
        else:
            lib, stream = convertInt_list(stream[:size*8], bits=8), stream[size*8:]
            partition_length, remaining_count = MiddleOutUtils.single_split(stream, length, size=size)
            split, stream = stream[:partition_length], stream[partition_length:]
            if debug: print("library: ", lib, ", split: ", split)
            remaining, stream = MiddleOut.decompress(stream, remaining_count, size=size, debug=debug)
            return MiddleOut.decompress_helper(split, lib, remaining), stream

    @staticmethod
    def decompress_helper(partition, lib, remaining, size=2):
        uncompressed = []
        remaining_count = 0
        for i in partition:
            if i == '1':
                uncompressed.append(remaining[remaining_count])
                remaining_count += 1
            else:
                for x in range(size):
                    uncompressed.append(lib[x])
        return uncompressed

    @staticmethod
    def byte_compression(values, size=2, debug=False):
        if debug: print("original values: ", values)
        if len(values) == 0:
            return ''
        if len(values) <= size:
            while len(values) % size != 0:
                values.append(0)
        split, left, right, iden = MiddleOutUtils.splitter(values, debug=debug)
        if debug: print("identify: ", iden, ", split: ", split, ", split size: ", len(split))
        l_, r_ = MiddleOutUtils.build_library(left, size=size), MiddleOutUtils.build_library(right, size=size)
        left_lib = convertBin_list(l_, bits=8) if l_ is not None else ''
        right_lib = convertBin_list(r_, bits=8) if r_ is not None else ''
        comp_l, uncomp_l = MiddleOut.middle_out_helper(left, l_, debug=debug)
        comp_r, uncomp_r = MiddleOut.middle_out_helper(right, r_, debug=debug)
        stream_l = left_lib + comp_l; stream_r = right_lib + comp_r
        if debug:
            print("left side library: ", left_lib, ", left compressed: ", comp_l, ", left uncompressed", uncomp_l)
            print("right side library: ", right_lib, ", right compressed: ", comp_r, ", right uncompressed", uncomp_r)
        return iden + split + stream_l + MiddleOut.byte_compression(uncomp_l, debug=debug) + stream_r + \
               MiddleOut.byte_compression(uncomp_r, debug=debug)

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, size=2, debug=False):
        if debug: print("partitioned stream: ", byte_stream, ", ", "library: ", compression_dict)
        count, unc_count = 0, 0
        compressed = ''; uncompressed = []
        while count < len(byte_stream):
            tup = tuple(byte_stream[count:count+size])
            if tup != compression_dict:
                compressed += '1'
                uncompressed.append(byte_stream[count])
                count += 1
            else:
                compressed += '0'
                count += len(tup)
        if debug:
            print("compressed: ", compressed); print("uncompressed: ", uncompressed)
        return compressed, uncompressed

    @staticmethod
    def middle_out(coefficients, size=2, debug=False):
        header = positive_binary(size)
        length = len(coefficients); minbits = minimum_bits(length)
        unary = unaryconverter(minbits)
        count = positive_binary(length, minbits)
        return header + unary + count + MiddleOut.byte_compression(coefficients, size=size, debug=debug)

    @staticmethod
    def middle_out_decompress(bitstream, debug=False):
        header = positive_int(bitstream[:8]); bitstream = bitstream[8:]
        count, unary_count = 0, unaryToInt(bitstream); count += unary_count + 1
        length = positive_int(bitstream[count:count+unary_count])
        bitstream = bitstream[count+unary_count:]
        if debug: print("size:", length, ",", "compressed stream:", bitstream)
        return MiddleOut.decompress(bitstream, length, size=header, debug=debug)[0]
