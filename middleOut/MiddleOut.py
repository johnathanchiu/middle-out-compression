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
    def get_count(bitset, length, typing='1'):
        count, bit = 0, 0
        while bit < length:
            if bitset[bit] == typing:
                count += 1; bit += 1
            else:
                bit += 2
                if bitset[bit - 1] == '1':
                    bit += 1
        return count

    @staticmethod
    def get_count_unary(bitset, length, typing='1'):
        count, bit = 0, 0
        while bit < length:
            if bitset[bit] == typing:
                unary_count = unaryToInt(bitset[bit:])
                bit += unary_count + 1
                values_to_grab = positive_int(bitset[bit:bit+unary_count])
                bit += unary_count
                count += values_to_grab
            else:
                bit += 2
                if bitset[bit - 1] == '1':
                    bit += 1
        return count

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
            print(dictionary)
            print("lib", large_occur, prob)
        return large_occur, prob

    @staticmethod
    def make_count(byte_stream):
        return Counter(byte_stream)

    @staticmethod
    def build_dict(byte_lib, byte_stream, debug=False):
        if byte_lib[0] == byte_lib[1]:
            largest_values = MiddleOutUtils.make_count(byte_stream)
            largest_values[byte_lib[0]] = 0
            largest = MiddleOutUtils.max_key(largest_values)
            compression_lib = convertBin_list([byte_lib[0], largest])
            if debug: print("next largest value", largest, "occurence", largest_values[largest])
            return {byte_lib: '00', tuple([byte_lib[0]]): '010', tuple([largest]): '011'}, '1', compression_lib
        compression_lib = convertBin_list(byte_lib)
        return {byte_lib: '00', tuple([byte_lib[0]]): '010', tuple([byte_lib[1]]): '011'}, '0', compression_lib

    @staticmethod
    def build_decomp_library(iden, lib):
        if iden == '1':
            tup = tuple([lib[0], lib[0]])
            return {'00': tup, '010': lib[0], '011': lib[1]}
        return {'00': lib, '010': lib[0], '011': lib[1]}


class MiddleOut:
    # TODO: test decompress function
    @staticmethod
    def decompress(compressed, length):
        decompressed = []
        count, succeeding_count = 0, 0
        if len(compressed) == 0:
            return decompressed
        identifier, occiden, bit_library = compressed[0], compressed[1], compressed[2:18]
        partition = compressed[18:length+18]
        if occiden == '0':
            length_other = MiddleOutUtils.get_count(partition, length)
        else:
            length_other = MiddleOutUtils.get_count_unary(partition, length)
        bit_library = convertInt_list(bit_library, bits=8)
        decompression_library = MiddleOutUtils.build_decomp_library(identifier, bit_library)
        succeeding_values = MiddleOut.decompress(compressed[length+18:], length_other)
        while count < length:
            if partition[count] == '0':
                if partition[count + 1] == '1':
                    decompressed.append(decompression_library[partition[count:count+3]])
                    count += 3
                else:
                    decompressed.append(decompression_library[partition[count:count+2]])
                    count += 2
            else:
                if occiden == '0':
                    decompressed.append(succeeding_values[succeeding_count])
                    succeeding_count += 1
                    count += 1
                else:
                    unary_count = unaryToInt(partition[count:])
                    count += unary_count + 1
                    values_to_grab = positive_int(partition[count:count+unary_count])
                    count += unary_count
                    decompressed.append(succeeding_values[succeeding_count:succeeding_count+values_to_grab])
                    succeeding_count += values_to_grab
        return decompressed

    @staticmethod
    def byte_compression(byte_stream, size=2, count_recursion=1, debug=False):
        if debug:
            print("recursion count", count_recursion, "remaining length", len(byte_stream))
        compressed = ''
        if len(byte_stream) == 0:
            return compressed
        compression_lib, occprob = MiddleOutUtils.build_library(byte_stream, debug=debug)
        compression_dict, identifier, compressed_lib = MiddleOutUtils.build_dict(compression_lib, byte_stream, debug=debug)
        if occprob / len(byte_stream) > 0.40:
            compressed, uncompressed = MiddleOut.middle_out_helper(byte_stream, compression_dict, occ=True, debug=debug)
            occiden = '1'
        else:
            compressed, uncompressed = MiddleOut.middle_out_helper(byte_stream, compression_dict, occ=False, debug=debug)
            occiden = '0'
        comp = MiddleOut.byte_compression(uncompressed, size=size, count_recursion=count_recursion+1, debug=debug)
        return identifier + occiden + compressed_lib + compressed + comp

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, occ=False, size=2, debug=False):
        if debug: print("current length: ", len(byte_stream))
        count, unc_count = 0, 0
        compressed = ''
        uncompressed = []
        while count < len(byte_stream) - size:
            compressor = 1
            tup = tuple(byte_stream[count:count + compressor])
            while tup in compression_dict:
                compressor += 1
                tup = tuple(byte_stream[count:count + compressor])
            if len(tup) > 1:
                tup = tuple(byte_stream[count:count + compressor - 1])
            if tup not in compression_dict:
                if occ:
                    compressed += '1'
                else:
                    unc_count += 1
                uncompressed.append(byte_stream[count])
            else:
                if occ:
                    if unc_count > 0:
                        minbits = minimum_bits(unc_count-1)
                        unary_count = unaryconverter(minbits)
                        compressed += unary_count + positive_binary(unc_count-1, bits=minbits)
                        unc_count = 0
                compressed += compression_dict[tup]
            count += len(tup)
        if debug: print("bitstream length: ", len(compressed))
        return compressed, uncompressed

    @staticmethod
    def middle_out(image_coefficients):
        return MiddleOut.byte_compression(image_coefficients, debug=False)

    @staticmethod
    def middle_out_decompress(bitstream):
        count, unary_count = 0, unaryToInt(bitstream)
        count += unary_count + 1
        length = positive_int(bitstream[count:count+unary_count])
        return MiddleOut.decompress(bitstream[count+unary_count:], length)
