from collections import Counter


class MiddleOutUtils:
    @staticmethod
    def convertBin(num, bits=8):
        s = bin(num & int("1" * bits, 2))[2:]
        return ("{0:0>%s}" % (bits)).format(s)

    @staticmethod
    def convertInt(binary, bits=8):
        binary = int(binary, 2)
        """compute the 2's complement of int value val"""
        if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            binary = binary - (1 << bits)  # compute negative value
        return binary  # return positive value as is

    @staticmethod
    def convertBin_list(intList, bits=8):
        def bindigits(val, bits=8):
            s = bin(val & int("1" * bits, 2))[2:]
            return ("{0:0>%s}" % (bits)).format(s)
        binary = ''
        for x in intList:
            binary += bindigits(x, bits=bits)
        return binary

    @staticmethod
    def convertInt_list(binary, bits=8):
        def two_complement(binary, bits=8):
            binary = int(binary, 2)
            """compute the 2's complement of int value val"""
            if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
                binary = binary - (1 << bits)  # compute negative value
            return binary  # return positive value as is
        intList = []
        for x in range(0, len(binary), bits):
            intList.append(two_complement(binary[x:x+bits], bits=bits))
        return intList

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
    def get_count(bitset, typing='1'):
        count, bit = 0, 0
        while bit < len(bitset):
            if bitset[bit] == typing:
                count += 1; bit += 1
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
    def build_dict(byte_lib, byte_stream):
        compression_lib = MiddleOutUtils.convertBin_list(byte_lib)
        # if byte_lib[0] == byte_lib[1]:
        #     largest_values = MiddleOutUtils.make_count(byte_stream)
        #     largest_values[byte_lib[0]] = 0
        #     largest = MiddleOutUtils.max_key(largest_values)
        #     compression_lib = MiddleOutUtils.convertBin_list([byte_lib[0], largest])
        #     # print("next largest value", largest, "occurence", largest_values[largest])
        #     return {byte_lib: '00', tuple([byte_lib[0]]): '010', tuple([largest]): '011'}, '1', compression_lib
        # return {byte_lib: '00', tuple([byte_lib[0]]): '010', tuple([byte_lib[1]]): '011'}, '0', compression_lib
        return {byte_lib: '0'}, '0', compression_lib

    @staticmethod
    def build_decomp_library(iden, lib):
        if iden == '1':
            tup = tuple([lib[0], lib[0]])
            return {'00': tup, '010': lib[0], '011': lib[1]}
        return {'00': lib, '010': lib[0], '011': lib[1]}


class MiddleOut:
    @staticmethod
    def decompress(compressed, length):
        decompressed = []
        count, other_counter = 0, 0
        if len(compressed) == 0:
            return decompressed
        partition = compressed[17:length+17]
        length_other = MiddleOutUtils.get_count(partition)
        bit_library, identifier = MiddleOutUtils.convertInt_list(compressed[1:17], bits=8), compressed[0]
        decompression_library = MiddleOutUtils.build_decomp_library(identifier, bit_library)
        succeeding_values = MiddleOut.decompress(compressed[length+17:], length_other)
        while count < length:
            if partition[count] == '0':
                if partition[count + 1] == '1':
                    decompressed.append(decompression_library[partition[count:count+3]])
                    count += 3
                else:
                    decompressed.append(decompression_library[partition[count:count+2]])
                    count += 2
            else:
                decompressed.append(succeeding_values[other_counter])
                other_counter += 1
                count += 1
        return decompressed

    @staticmethod
    def byte_compression(byte_stream, size=2, count_recursion=1, debug=False):
        if debug:
            print("recursion count", count_recursion, "remaining length", len(byte_stream))
        compressed = ''
        uncompressed = []
        if len(byte_stream) == 0:
            return compressed, uncompressed
        compression_lib, occprob = MiddleOutUtils.build_library(byte_stream, debug=debug)
        compression_dict, _, compressed_lib = MiddleOutUtils.build_dict(compression_lib, byte_stream)
        if occprob / len(byte_stream) > 0.35:
            compressed, uncompressed = MiddleOut.middle_out_helper(byte_stream, compression_dict)
        else:
            return compressed, byte_stream
        comp, unc = MiddleOut.byte_compression(uncompressed, size=size, count_recursion=count_recursion+1, debug=debug)
        return compressed_lib + compressed + comp, unc

    # @staticmethod
    # def middle_out_helper(byte_stream, compression_dict, size=2):
    #     count = 0
    #     compressed = ''
    #     uncompressed = []
    #     while count < len(byte_stream) - size:
    #         compressor = 1
    #         tup = tuple(byte_stream[count:count + compressor])
    #         while tup in compression_dict:
    #             compressor += 1
    #             tup = tuple(byte_stream[count:count + compressor])
    #         if len(tup) > 1:
    #             tup = tuple(byte_stream[count:count + compressor - 1])
    #         if tup not in compression_dict:
    #             compressed += '1'
    #             uncompressed.append(byte_stream[count])
    #         else:
    #             compressed += compression_dict[tup]
    #         count += len(tup)
    #     return compressed, uncompressed

    @staticmethod
    def middle_out_helper(byte_stream, compression_dict, size=2):
        count = 0
        compressed = ''
        uncompressed = []
        while count < len(byte_stream) - size:
            tup = tuple(byte_stream[count:count + 2])
            if tup not in compression_dict:
                compressed += '1'
                uncompressed.append(byte_stream[count])
                count += 1
            else:
                compressed += compression_dict[tup]
                count += 2
        return compressed, uncompressed

    @staticmethod
    def middle_out(image_coefficients):
        return MiddleOut.byte_compression(image_coefficients, debug=True)
