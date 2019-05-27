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
    def build_library(byte_stream, size=2):
        count = 0
        dictionary = {}
        if len(byte_stream) < size:
            for _ in range(size - len(byte_stream)):
                temp = list([0])
                temp.append(byte_stream)
                byte_stream = temp
        while count <= len(byte_stream) - size:
            partition = tuple(byte_stream[count:count + size])
            if partition not in dictionary:
                dictionary[partition] = 1
            else:
                dictionary[partition] += 1
            count += 1
        large_occur = MiddleOutUtils.max_key(dictionary)
        print("lib", large_occur, dictionary[large_occur])
        return large_occur

    @staticmethod
    def build_library(byte_stream):
        return Counter(byte_stream)

    @staticmethod
    def build_dict(byte_lib):
        return {byte_lib: '00',
                tuple(byte_lib[:1]): '01' + format(0, '02b'),
                tuple(byte_lib[:2]): '01' + format(1, '02b'),
                tuple(byte_lib[2:]): '01' + format(2, '02b'),
                tuple(byte_lib[1:]): '01' + format(3, '02b')}

        # return {byte_lib: '00',
        #         tuple(byte_lib[:1]): '01' + format(0, '01b'),
        #         tuple(byte_lib[1:]): '01' + format(1, '01b')}


class MiddleOut:
    @staticmethod
    def decompress(compressed):
        new_lib = True
        x, count = 0, 0
        uncompressed = ''
        while x < len(compressed):
            if new_lib:
                new_lib = False
        return uncompressed

    @staticmethod
    def byte_compression(byte_stream, size=2, count_recursion=1):
        print("count_recur", count_recursion)
        count = 0
        compressed = ''
        uncompressed = []
        if len(byte_stream) == 0:
            return compressed
        compression_lib = MiddleOutUtils.build_library(byte_stream)
        compression_dict = MiddleOutUtils.build_dict(compression_lib)
        compressed_lib = MiddleOutUtils.convertBin_list(compression_lib)
        while count < len(byte_stream) - size:
            compressor = 1
            tup = tuple(byte_stream[count:count + compressor])
            while tup in compression_dict:
                compressor += 1
                tup = tuple(byte_stream[count:count + compressor])
            if tup not in compression_dict and len(tup) == 1:
                compressed += '1'
                uncompressed.append(byte_stream[count])
            else:
                tup = tuple(byte_stream[count:count + compressor - 1])
                compressed += compression_dict[tup]
            count += len(tup)
        return compressed_lib + compressed + '0001' + MiddleOut.byte_compression(uncompressed,
        size=size, count_recursion=count_recursion+1)

    # @staticmethod
    # def byte_compression(byte_stream, item_count, count_recursion=1):
    #     count = 0
    #     compressed = ''
    #     uncompressed = []
    #     length_bytes = len(byte_stream)
    #     if length_bytes == 0:
    #         return compressed
    #     compressed_lib = MiddleOutUtils.max_key(item_count)
    #     while count < length_bytes:
    #         if byte_stream[count] == compressed_lib:
    #             compressed += '0'
    #
    #         else:
    #             compressed += '1'
    #     item_count[compressed_lib] = 0
    #     return compressed_lib + compressed + MiddleOut.byte_compression(uncompressed, item_count, count_recursion=count_recursion+1)

    @staticmethod
    def middle_out(image_coefficients):
        items = MiddleOutUtils.build_library(image_coefficients)
        return MiddleOut.byte_compression(image_coefficients, items)
