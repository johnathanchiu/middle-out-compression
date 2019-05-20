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
    def get_literal_size(stream):
        if len(stream) <= 2:
            return '00' + MiddleOutUtils.convertBin(len(stream) - 1, bits=1)  # get small literals
        elif len(stream) <= 6:
            return '01' + MiddleOutUtils.convertBin(len(stream) - 3, bits=2)  # medium literals
        elif len(stream) <= 22:
            return '1101' + MiddleOutUtils.convertBin(len(stream) - 7, bits=4)  # larger literals
        elif len(stream) <= 86:
            return '1110' + MiddleOutUtils.convertBin(len(stream) - 23, bits=6)  # largest literals
        return '1110' + MiddleOutUtils.convertBin(len(stream[:86]) - 23, bits=6) + \
               MiddleOutUtils.get_literal_size(stream[86:])

    @staticmethod
    def build_library(uncompressed, size=8):
        dictionary = {}
        count = 0
        length = len(uncompressed)
        while count < length - size:
            partition = str(uncompressed[count:count + size])
            if partition not in dictionary:
                dictionary[partition] = 1
            else:
                dictionary[partition] += 1
            count += 1
        largest = MiddleOutUtils.max_key(dictionary)
        print(largest, dictionary[largest])
        return largest

    @staticmethod
    def build_dict(bit_lib):
        return {bit_lib: '10', bit_lib[:6]: '11' + format(0, '01b'), bit_lib[:7]: '11' + format(1, '01b')}

class MiddleOut:
    @staticmethod
    def decompressStream(compressed):
        uncompressed = ''
        new_run = True
        x, count = 0, 0
        while x < len(compressed):
            if new_run:
                eight_lib = compressed[x:x+8]
                new_run = False
                x += 16
            elif compressed[x:x+7] == '1111110':
                new_run = True
                x += 6
        return uncompressed

    @staticmethod
    def eight_bit_compression(uncompressed, lib):
        temp = ''
        compressed, unc = [], []
        total_count, count = len(uncompressed), 0
        uncompressed += ' '
        compression_lib = MiddleOutUtils.build_dict(lib)
        while count < len(uncompressed) - 1:
            compressor = 6
            mo = uncompressed[count:count + compressor]
            while mo in compression_lib:
                compressor += 1
                mo = uncompressed[count:count + compressor]
            mo = mo[:-1]
            length_string = len(mo)
            if length_string >= 6:
                if temp != '':
                    unc.append(temp)
                    compressed.append(MiddleOutUtils.get_literal_size(temp))
                    temp = ''
                compressed.append(compression_lib[mo])
                count += length_string
            else:
                temp += uncompressed[count]
                count += 1
        if temp != '':
            unc.append(temp)
            compressed.append(MiddleOutUtils.get_literal_size(temp))
        return compressed, unc

    # @staticmethod
    # def middle_out(stream):
    #     middle_comp, unc = MiddleOut.eight_bit_compression(stream)
    #     eight_bit = MiddleOut.build_library(unc, size=8)
    #     outer_comp = MiddleOut.eight_bit_compression(unc, eight_bit)
    #     y = MiddleOut.merge_compression(middle_comp, outer_comp)
    #     return eight_bit + y + '1111110'
