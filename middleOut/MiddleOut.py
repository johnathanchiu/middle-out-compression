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
    def unaryconverter(lis):
        unary = []
        for y in lis:
            [unary.append('1') for _ in range(y)]
            unary.append('0')
        return ''.join(unary)

    @staticmethod
    def count_rep(part_stream, typing='0', stop=0):
        count = 0
        for y in part_stream:
            if y != typing or count >= stop:
                return count
            count += 1
        return count

    @staticmethod
    def keywithmaxval(d):
        v = list(d.values())
        k = list(d.keys())
        return k[v.index(max(v))]

    # TODO: add get-literal functions
    @staticmethod
    def get_literal_long(stream):
        return '101' + MiddleOutUtils.convertBin(len(stream) - 7, bits=4) + stream

    @staticmethod
    def get_literal(stream):
        return '100' + MiddleOutUtils.convertBin(len(stream) - 3, bits=2) + stream

    @staticmethod
    def get_literal_small(stream):
        return '00' + MiddleOutUtils.convertBin(len(stream) - 1, bits=1) + stream

    @staticmethod
    def get_literal_large(stream):
        return '111110' + MiddleOutUtils.convertBin(len(stream) - 23, bits=6) + stream


class MiddleOut:
    @staticmethod
    def build_library(uncompressed, size=8):
        dictionary = {}
        for x in uncompressed:
            len_of_x = len(x)
            if len_of_x >= size:
                for y in range(len_of_x - size + 1):
                    par = x[y:y+size]
                    if par not in dictionary:
                        dictionary[par] = 1
                    else:
                        dictionary[par] += 1
        return MiddleOutUtils.keywithmaxval(dictionary)

    @staticmethod
    def build_dict(bit_lib):
        return {bit_lib: '11110', bit_lib[:6]: '1110' + format(0, '01b'), bit_lib[:7]: '1110' + format(1, '01b')}

    @staticmethod
    def decompressStream(compressed):
        uncompressed = ''
        new_run = True
        x, count = 0, 0
        while x < len(compressed):
            if new_run:
                eight_lib = compressed[x:x+8]
                new_run = False
                x += 8
            elif compressed[x] == '0':
                if compressed[x+1] == '1':
                    for _ in range(MiddleOutUtils.convertInt(compressed[x + 2:x + 5]) + 6):
                        uncompressed += '0'
                    x += 5
                else:
                    num = MiddleOutUtils.convertInt(compressed[x+2]) + 1
                    uncompressed += compressed[x+3:x+3+num]
                    x += 3 + num
            elif compressed[x:x+2] == '10':
                if compressed[x+2] == '0':
                    num = MiddleOutUtils.convertInt(compressed[x+3:x+5]) + 3
                    uncompressed += compressed[x + 5: x + 5 + num]
                    x += num + 5
                else:
                    num = MiddleOutUtils.convertInt(compressed[x+3:x+7]) + 7
                    uncompressed += compressed[x+7:x+7+num]
                    x += num + 7
            elif compressed[x:x+3] == '110':
                for _ in range(MiddleOutUtils.convertInt(compressed[x+3:x+5]) + 6):
                    uncompressed += '1'
                x += 5
            elif compressed[x:x+5] == '11110':
                uncompressed += eight_lib
                x += 5
            elif compressed[x:x+4] == '1110':
                uncompressed += eight_lib[:6 + MiddleOutUtils.convertInt(compressed[x + 4])]
                x += 5
            elif compressed[x:x+6] == '111110':
                num = MiddleOutUtils.convertInt(compressed[x+6:x+12]) + 23
                uncompressed += compressed[x+12:x+12+num]
                x += num + 12
            elif compressed[x:x+7] == '1111110':
                new_run = True
                x += 6
        # TODO: add extra libraries for the literals
        return uncompressed

    @staticmethod
    def zero_one_filter(uncompressed):
        x = 0
        res = ''
        # a = len(uncompressed)
        partial_decomp, uncomp_partition = [], []
        while x < len(uncompressed):
            if uncompressed[x] == '0':
                counter = MiddleOutUtils.count_rep(uncompressed[x:], typing='0', stop=13)
                if counter >= 6:
                    if res != '':
                        partial_decomp.append(0)
                        uncomp_partition.append(res)
                        res = ''
                    header = MiddleOutUtils.convertBin(counter - 6, bits=3)
                    partial_decomp.append('01' + header)
                    x += counter
                    # a -= (counter - 5)
                else:
                    res += uncompressed[x]
                    x += 1
            else:
                counter = MiddleOutUtils.count_rep(uncompressed[x:], typing='1', stop=9)
                if counter >= 6:
                    if res != '':
                        partial_decomp.append(0)
                        uncomp_partition.append(res)
                        res = ''
                    header = MiddleOutUtils.convertBin(counter - 6, bits=2)
                    partial_decomp.append('110' + header)
                    x += counter
                    # a -= (counter - 5)
                else:
                    res += uncompressed[x]
                    x += 1
        if res != '':
            partial_decomp.append(0)
            uncomp_partition.append(res)
        # print(a)
        return partial_decomp, uncomp_partition

    @staticmethod
    def eight_bit_compression(uncompressed_list, lib):
        compressed = []
        lib_dict = MiddleOut.build_dict(lib)
        for x in uncompressed_list:
            len_of_x = len(x)
            if len_of_x <= 2:
                compressed.append(MiddleOutUtils.get_literal_small(x))
            elif len_of_x >= 8:
                comp = MiddleOut.filter_values(x, lib_dict)
                compressed.extend(comp)
            else:
                compressed.append(MiddleOut.getliteral(x))
        return compressed

    @staticmethod
    def filter_values(bitStream, lib_dict):
        comp = []
        res = ''
        bitStream += ' '
        count = 0
        while count < len(bitStream) - 1:
            compressor = 6
            stringLength = bitStream[count:count + compressor]
            while stringLength in lib_dict:
                compressor += 1
                stringLength = bitStream[count:count + compressor]
            stringLength = stringLength[:-1]
            length_string = len(stringLength)
            if length_string >= 6:
                if res != '':
                    if len(comp) > 0:
                        comp[0] += MiddleOut.getliteral(res) + lib_dict[stringLength]
                        res = ''
                    else:
                        comp.append(MiddleOut.getliteral(res) + lib_dict[stringLength])
                        res = ''
                else:
                    if len(comp) > 0:
                        comp[0] += lib_dict[stringLength]
                    else:
                        comp.append(lib_dict[stringLength])
                count += length_string
            else:
                res += bitStream[count]
                count += 1
        if res != '':
            if len(comp) == 0:
                return [MiddleOut.getliteral(res)]
            comp[0] += MiddleOut.getliteral(res)
        return comp

    @staticmethod
    def getliteral(lis):
        len_of_lis = len(lis)
        if len_of_lis <= 2:
            return MiddleOutUtils.get_literal_small(lis)
        elif len_of_lis <= 6:
            return MiddleOutUtils.get_literal(lis)
        elif len_of_lis <= 22:
            return MiddleOutUtils.get_literal_long(lis)
        elif len_of_lis <= 86:
            return MiddleOutUtils.get_literal_large(lis)
        return MiddleOutUtils.get_literal_large(lis[:86]) + MiddleOut.getliteral(lis[86:])

    @staticmethod
    def merge_compression(layer_one, layer_two):
        count = 0
        for x in range(len(layer_one)):
            if layer_one[x] == 0:
                layer_one[x] = layer_two[count]
                count += 1
        return ''.join(layer_one)

    @staticmethod
    def middle_out(stream):
        middle_comp, unc = MiddleOut.zero_one_filter(stream)
        eight_bit = MiddleOut.build_library(unc)
        outer_comp = MiddleOut.eight_bit_compression(unc, eight_bit)
        y = MiddleOut.merge_compression(middle_comp, outer_comp)
        return eight_bit + y + '1111110'
