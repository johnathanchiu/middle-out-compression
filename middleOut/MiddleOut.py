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
        prob = dictionary[large_occur]
        if debug:
            print("largest occurring:", large_occur, ", ", "occurrence:", prob, ", ",
                  "size of byte stream:", len(byte_stream))
        return large_occur

    @staticmethod
    def make_count(byte_stream):
        return Counter(byte_stream)

    @staticmethod
    def build_dict(byte_lib, byte_stream, debug=False):
        if byte_lib[0] == byte_lib[1]:
            largest_values = MiddleOutUtils.make_count(byte_stream)
            prob = largest_values[byte_lib[0]]
            largest_values[byte_lib[0]] = 0
            largest = MiddleOutUtils.max_key(largest_values)
            compression_lib = convertBin_list([byte_lib[0], largest])
            prob += largest_values[largest]
            if debug: print("next largest value", largest, "occurrence", prob)
            return {byte_lib: '00', tuple([byte_lib[0]]): '010', tuple([largest]): '011'}, '1', compression_lib, prob
        values_count = MiddleOutUtils.make_count(byte_stream)
        compression_lib = convertBin_list(byte_lib)
        prob = values_count[byte_lib[0]] + values_count[byte_lib[1]]
        return {byte_lib: '00', tuple([byte_lib[0]]): '010', tuple([byte_lib[1]]): '011'}, '0', compression_lib, prob

    @staticmethod
    def build_decomp_library(iden, lib):
        if iden == '1':
            tup = tuple([lib[0], lib[0]])
            return {'00': tup, '010': lib[0], '011': lib[1]}
        return {'00': lib, '010': lib[0], '011': lib[1]}

    @staticmethod
    def get_bit_count(stream, length, unary='1'):
        count, count_other, bit = 0, 0, 0
        while count < length:
            if stream[bit] == '1':
                if unary == '0':
                    unary_count = unaryToInt(stream[bit:])
                    bit += unary_count + 1
                    values_to_grab = positive_int(stream[bit:bit+unary_count]) + 1
                    bit += unary_count
                    count += values_to_grab; count_other += values_to_grab
                else:
                    count += 1; count_other += 1; bit += 1
            else:
                bit += 2
                count += 2
                if stream[bit - 1] == '1':
                    bit += 1
                    count -= 1
        return bit, count_other


class MiddleOut:
    @staticmethod
    def decompress(compressed, length, debug=False):
        decompressed = []
        count, succeeding_count = 0, 0
        if len(compressed) == 0:
            return decompressed
        identifier, occiden, bit_library = compressed[0], compressed[1], compressed[2:18]
        if debug: print("iden:", identifier, ",", "occurrence:", occiden, ",", "library:", bit_library)
        partition_size, length_other = MiddleOutUtils.get_bit_count(compressed[18:], length=length, unary=occiden)
        partition = compressed[18:partition_size+18]
        bit_library = convertInt_list(bit_library, bits=8)
        decompression_library = MiddleOutUtils.build_decomp_library(identifier, bit_library)
        if debug:
            print("size of stream:", partition_size, "length of next bitset:", length_other)
            print("decomp library:", decompression_library)
        succeeding_values = MiddleOut.decompress(compressed[partition_size+18:], length_other, debug=debug)
        while count < partition_size:
            if partition[count] == '0':
                if partition[count + 1] == '1':
                    decompressed.append(decompression_library[partition[count:count+3]])
                    count += 3
                else:
                    occur = decompression_library[partition[count:count+2]]
                    decompressed.append(occur[0])
                    decompressed.append(occur[1])
                    count += 2
            else:
                if occiden == '1':
                    decompressed.append(succeeding_values[succeeding_count])
                    succeeding_count += 1
                    count += 1
                else:
                    unary_count = unaryToInt(partition[count:])
                    count += unary_count + 1
                    values_to_grab = positive_int(partition[count:count+unary_count]) + 1
                    count += unary_count
                    occur = succeeding_values[succeeding_count:succeeding_count+values_to_grab]
                    [decompressed.append(i) for i in occur]
                    succeeding_count += values_to_grab
        return decompressed

    @staticmethod
    def byte_compression(byte_stream, size=2, count_recursion=1, debug=False):
        if debug:
            print("recursion count", count_recursion, ",", "remaining length", len(byte_stream))
            print("remaining values", byte_stream)
        compressed = ''
        if len(byte_stream) == 0:
            return compressed
        compression_lib = MiddleOutUtils.build_library(byte_stream, debug=debug)
        compression_dict, identifier, compressed_lib, occprob = MiddleOutUtils.build_dict(compression_lib,
                                                                                          byte_stream, debug=debug)
        if debug: print("occurrence prob:", occprob / len(byte_stream), len(byte_stream))
        if occprob / len(byte_stream) > 0.35:
            compressed, uncompressed = MiddleOut.middle_out_helper(byte_stream, compression_dict, occ=True, debug=debug)
            occiden = '1'
        else:
            compressed, uncompressed = MiddleOut.middle_out_helper(byte_stream, compression_dict, occ=False, debug=debug)
            occiden = '0'
        comp = MiddleOut.byte_compression(uncompressed, size=size, count_recursion=count_recursion+1, debug=debug)
        if debug: print("binary library", compressed_lib)
        return identifier + occiden + compressed_lib + compressed + comp

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, occ=False, size=2, debug=False):
        if debug: print("current length:", len(byte_stream), ",", "unary:", occ)
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
                if occ:
                    compressed += '1'
                else:
                    unc_count += 1
                uncompressed.append(byte_stream[count])
            else:
                if not occ:
                    if unc_count > 0:
                        minbits = minimum_bits(unc_count-1)
                        unary_count = unaryconverter(minbits)
                        compressed += unary_count + positive_binary(unc_count-1, bits=minbits)
                        unc_count = 0
                compressed += compression_dict[tup]
            count += len(tup)
        if not occ:
            if unc_count > 0:
                minbits = minimum_bits(unc_count-1)
                unary_count = unaryconverter(minbits)
                compressed += unary_count + positive_binary(unc_count-1, bits=minbits)
        if debug: print("bitstream length:", len(compressed), compressed)
        return compressed, uncompressed

    @staticmethod
    def middle_out(coefficients, debug=False):
        length = len(coefficients)
        minbits = minimum_bits(length)
        unary = unaryconverter(minbits)
        size = positive_binary(length, minbits)
        if debug: print("header:", unary + size, ",", "size:", length)
        return unary + size + MiddleOut.byte_compression(coefficients, debug=debug)

    @staticmethod
    def middle_out_decompress(bitstream, debug=False):
        count, unary_count = 0, unaryToInt(bitstream)
        count += unary_count + 1
        length = positive_int(bitstream[count:count+unary_count])
        bitstream = bitstream[count+unary_count:]
        if debug: print("size:", length, ",", "compressed stream:", bitstream)
        return MiddleOut.decompress(bitstream, length, debug=debug)
