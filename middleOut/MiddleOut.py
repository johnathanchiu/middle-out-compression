from collections import Counter
from middleOut.utils import *


class MiddleOutUtils:
    @staticmethod
    def count_rep(part_stream, typing='0', stop=0):
        count = 0
        for y in part_stream:
            if y != typing or count >= stop:
                return count
            count += 1
        return count

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
    def build_dict(byte_lib, byte_stream, size=2, debug=False):
        if byte_lib[0] == byte_lib[1]:
            largest_values = MiddleOutUtils.make_count(byte_stream)
            prob = largest_values[byte_lib[0]]
            largest_values[byte_lib[0]] = 0
            largest = MiddleOutUtils.max_key(largest_values)
            prob += largest_values[largest]
            largest_values[largest] = 0
            full_lib = array.array('b', [])
            [full_lib.append(byte_lib[a]) for a in range(size)]
            full_lib[1] = largest
            if debug: print("next largest value", largest, "occurrence", prob)
            return {byte_lib: '00', tuple([byte_lib[0]]): '010', tuple([largest]): '011'}, '1', \
                    full_lib, largest_values, prob
        values_count = MiddleOutUtils.make_count(byte_stream)
        prob = values_count[byte_lib[0]] + values_count[byte_lib[1]]
        values_count[byte_lib[0]], values_count[byte_lib[1]] = 0, 0
        return {byte_lib: '00', tuple([byte_lib[0]]): '010', tuple([byte_lib[1]]): '011'}, '0', \
                array.array('b', byte_lib), values_count, prob

    @staticmethod
    def build_decomp_library(iden, lib, size=2):
        if iden == '1':
            values = []
            for a in range(size):
                values.append(lib[a])
            values[1] = values[0]
            tup = tuple(values)
            return {'00': tup, '010': lib[0], '011': lib[1]}
        return {'00': lib, '010': lib[0], '011': lib[1]}

    @staticmethod
    def increase_prob(size, occur, counter_lib, occur_lib, prob=0.4):
        if occur / size >= prob:
            return occur_lib
        largest = MiddleOutUtils.max_key(counter_lib)
        occur += counter_lib[largest]
        counter_lib[largest] = 0
        occur_lib.append(largest)
        return MiddleOutUtils.increase_prob(size, occur, counter_lib, occur_lib, prob=prob)

    @staticmethod
    def right_left_count(compressed, length):
        count, right, left = 0, 0, 0
        while count < length:
            if compressed[count] == '1':
                right += 1
            else:
                left += 1
            count += 1
        return left, right

    @staticmethod
    def get_bit_count(stream, length):
        count, count_other, bit = 0, 0, 0
        while count < length:
            if stream[bit] == '1':
                count += 1; count_other += 1; bit += 1
            else:
                bit += 2
                count += 2
                if stream[bit - 1] == '1':
                    bit += 1
                    count -= 1
        return bit, count_other


class MiddleOut:

    split_prob = 0.4

    @staticmethod
    def decompress(compressed, length, end=1, size=2, debug=False):
        decompressed = []
        if compressed == '' or end == 0:
            return decompressed
        branching = compressed[0]
        if branching == '1':
            compressed = compressed[1:]
            count, unary_count = 0, unaryToInt(compressed)
            count += unary_count + 1
            start_left = positive_int(compressed[count:count+unary_count]) + 1
            compressed = compressed[count+unary_count:]
            split = compressed[:length]
            left_total, right_total = MiddleOutUtils.right_left_count(compressed, length)
            compressed = compressed[length:]
            if debug: print("left:", left_total, ",", "right:", right_total)
            left_values = MiddleOut.decompress(compressed, left_total, size=size, debug=debug)
            compressed = compressed[start_left:]
            right_values = MiddleOut.decompress(compressed, right_total, size=size, debug=debug)
            if debug: print("left values:", left_values); print("right values:", right_values)
            start, left_count, right_count = 0, 0, 0
            while start < length:
                if split[start] == '1':
                    decompressed.append(right_values[right_count])
                    right_count += 1
                else:
                    decompressed.append(left_values[left_count])
                    left_count += 1
                start += 1
            return decompressed
        else:
            iden, bit_library, compressed = compressed[1], compressed[2:size*8+2], compressed[size*8+2:]
            partition_size, length_other = MiddleOutUtils.get_bit_count(compressed, length)
            bit_library = convertInt_list(bit_library, bits=8)
            decompression_library = MiddleOutUtils.build_decomp_library(iden, bit_library, size=size)
            if debug:
                print("size of stream:", partition_size, ",", "length produced by next bitset:", length_other)
                print("decomp library:", decompression_library)
            succeeding_values = MiddleOut.decompress(compressed[partition_size:], length_other, end=length_other,
                                                     size=size, debug=debug)
            return MiddleOut.decompress_helper(compressed, succeeding_values, decompression_library, partition_size)

    @staticmethod
    def decompress_helper(partition, succeeding, decomp, part_size):
        count, succeeding_count = 0, 0
        decompressed = []
        while count < part_size:
            if partition[count] == '0':
                if partition[count + 1] == '1':
                    decompressed.append(decomp[partition[count:count+3]])
                    count += 3
                else:
                    occur = decomp[partition[count:count+2]]
                    decompressed.append(occur[0])
                    decompressed.append(occur[1])
                    count += 2
            else:
                decompressed.append(succeeding[succeeding_count])
                succeeding_count += 1
                count += 1
        return decompressed

    @staticmethod
    def byte_compression(byte_stream, count_recursion=1, size=2, debug=False):
        if debug:
            print("recursion count", count_recursion, ",", "remaining length", len(byte_stream))
            print("remaining values", byte_stream)
        if len(byte_stream) == 0:
            return ''
        compression_lib = MiddleOutUtils.build_library(byte_stream, size=size, debug=debug)
        compression_dict, identifier, compressed_lib, count_lib, occprob = MiddleOutUtils.build_dict(compression_lib,
                                                                                                     byte_stream,
                                                                                                     size=size,
                                                                                                     debug=debug)
        left_splitter, compressed_lib = compressed_lib, convertBin_list(compressed_lib)
        if debug: print("left occurrences:", left_splitter)
        if debug: print("occurrence prob:", occprob / len(byte_stream), len(byte_stream))
        if occprob / len(byte_stream) < MiddleOut.split_prob:
            left_dict = MiddleOutUtils.increase_prob(len(byte_stream), occprob, count_lib, left_splitter,
                                                     prob=MiddleOut.split_prob)
            split_stream, left, right = MiddleOut.branch_tree(byte_stream, left_dict)
            if debug: print("split:", split_stream); print("left:", left, ", ", "right:", right)
            comp_left, uncompressed = MiddleOut.middle_out_helper(left, compression_dict, debug=debug)
            comp_left = '0' + identifier + compressed_lib + comp_left
            comp_left_right = MiddleOut.byte_compression(uncompressed, count_recursion=count_recursion+1, size=size,
                                                         debug=debug)
            comp_right = MiddleOut.byte_compression(right, count_recursion=count_recursion+1, size=size,
                                                    debug=debug)
            left_size = len(comp_left) + len(comp_left_right) - 1
            minbits = minimum_bits(left_size)
            unary = unaryconverter(minbits)
            size = positive_binary(left_size, minbits)
            if debug: print("left bits size:", left_size)
            return '1' + unary + size + split_stream + comp_left + comp_left_right + comp_right
        compressed, uncompressed = MiddleOut.middle_out_helper(byte_stream, compression_dict, debug=debug)
        comp = MiddleOut.byte_compression(uncompressed, count_recursion=count_recursion+1, size=size, debug=debug)
        if debug: print("binary library", compressed_lib)
        return '0' + identifier + compressed_lib + compressed + comp

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
    def middle_out(coefficients, debug=False):
        length = len(coefficients)
        minbits = minimum_bits(length)
        unary = unaryconverter(minbits)
        size = positive_binary(length, minbits)
        if debug: print("header:", unary + size, ",", "size:", length)
        return unary + size + MiddleOut.byte_compression(coefficients, size=3, debug=debug)

    @staticmethod
    def middle_out_decompress(bitstream, debug=False):
        count, unary_count = 0, unaryToInt(bitstream)
        count += unary_count + 1
        length = positive_int(bitstream[count:count+unary_count])
        bitstream = bitstream[count+unary_count:]
        if debug: print("size:", length, ",", "compressed stream:", bitstream)
        return MiddleOut.decompress(bitstream, length, size=3, debug=debug)
