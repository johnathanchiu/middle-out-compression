class MiddleOutUtils:
    @staticmethod
    def convertBin(num, bits=8):
        def bindigits(val, bits=8):
            s = bin(val & int("1" * bits, 2))[2:]
            return ("{0:0>%s}" % (bits)).format(s)
        return bindigits(num, bits=bits)

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
        for x in range(0, len(binary), 8):
            intList.append(two_complement(binary[x:x+8], bits=bits))
        return intList

    @staticmethod
    def convertInt(binary, bits=8):
        def two_complement(binary, bits=8):
            binary = int(binary, 2)
            """compute the 2's complement of int value val"""
            if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
                binary = binary - (1 << bits)  # compute negative value
            return binary  # return positive value as is
        return two_complement(binary, bits=bits)

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
            if y == typing:
                if count >= stop:
                    return count
                count += 1
            else:
                return count
        return count

    @staticmethod
    def get_literal(stream):
        return '100' + MiddleOutUtils.convertBin(len(stream) - 2, bits=2) + stream

    @staticmethod
    def get_literal_small(stream):
        return '00' + stream

    @staticmethod
    def keywithmaxval(d):
        """ a) create a list of the dict's keys and values;
            b) return the key with the max value"""
        v = list(d.values())
        k = list(d.keys())
        return k[v.index(max(v))]


class MiddleOut:
    @staticmethod
    def decompressStream(compressed):
        uncompressed, temp = '', []
        new_run = True
        x, count = 0, 0
        while x < len(compressed):
            if new_run:
                eight_lib = compressed[x:x+8]
                four_lib = compressed[x+8:x+12]
                new_run = False
                x += 8
            elif compressed[x] == '0':
                if compressed[x+1] == '1':
                    [temp.append('0') for _ in range(MiddleOutUtils.convertInt(compressed[x+1:x+4], 3))]
                    uncompressed.join(temp)
                    temp = []
                    x += 5
                else:
                    uncompressed += compressed[x + 2]
            elif compressed[x:x+2] == '10':
                if compressed[x+2] == '1':
                    uncompressed += four_lib
                    x += 3
                else:
                    num = MiddleOutUtils.convertInt(compressed[x+3:x+5], 2)
                    [temp.append(compressed[y+x+5]) for y in range(num)]
                    uncompressed.join(temp)
                    temp = []
                    x += num + x + 5
            elif compressed[x:x+3] == '110':
                [temp.append('1') for _ in range(MiddleOutUtils.convertInt(compressed[x+3:x+5], 2))]
                uncompressed.join(temp)
                temp = []
                x += 5
            elif compressed[x:x+5] == '11110':
                uncompressed += eight_lib
                x += 5
            elif compressed[x:x+4] == '1110':
                num = MiddleOutUtils.convertInt(compressed[x + 4:x + 7], bits=3)
                uncompressed += eight_lib[x:x + num]
                x += 3 + num
        return uncompressed

    @staticmethod
    def build_library(uncompressed, size=8):
        dictionary = {}
        for x in uncompressed:
            if len(x) >= size:
                for y in range(len(x) - size):
                    par = x[y:y+size]
                    if par not in dictionary:
                        dictionary[par] = 1
                    else:
                        dictionary[par] += 1
        print(dictionary)
        return MiddleOutUtils.keywithmaxval(dictionary)

    @staticmethod
    def build_dict(bit_lib):
        compression_dict = {}
        for x in range(len(bit_lib) - 1):
            compression_dict[bit_lib[:x + 1]] = '1110' + format(x, "03b")
        compression_dict[bit_lib] = '1110'
        return compression_dict

    @staticmethod
    def layer_one_compression(uncompressed):
        x = 0
        res = ''
        h = 0
        partial_decomp, uncomp_partition = [], []
        while x < len(uncompressed):
            if uncompressed[x] == '0':
                counter = MiddleOutUtils.count_rep(uncompressed[x:], typing='0', stop=13)
                if counter >= 6:
                    if res != '':
                        partial_decomp.append(0)
                        h += 1
                        uncomp_partition.append(res)
                        res = ''
                    header = MiddleOutUtils.convertBin(counter - 6, bits=3)
                    partial_decomp.append('10' + header)
                    x += counter
                else:
                    res += uncompressed[x]
                    x += 1
            else:
                counter = MiddleOutUtils.count_rep(uncompressed[x:], typing='1', stop=9)
                if counter >= 6:
                    if res != '':
                        partial_decomp.append(0)
                        h += 1
                        uncomp_partition.append(res)
                        res = ''
                    header = MiddleOutUtils.convertBin(counter - 6, bits=2)
                    partial_decomp.append('110' + header)
                    x += counter
                else:
                    res += uncompressed[x]
                    x += 1
        if res != '':
            partial_decomp.append(0)
            h += 1
            uncomp_partition.append(res)
        print('h', h)
        return partial_decomp, uncomp_partition

    @staticmethod
    def layer_two_compression(uncompressed_list, lib):
        compressed, uncompressed = [], []
        h = 0
        lib_dict = MiddleOut.build_dict(lib)
        for x in uncompressed_list:
            len_of_x = len(x)
            if len_of_x <= 5:
                compressed.append(MiddleOut.__getliteral(x))
            elif len_of_x >= 8:
                comp, unc, z = MiddleOut.filter_values(x, lib_dict)
                compressed.extend(comp)
                uncompressed.extend(unc)
                h += z
            else:
                compressed.append(0)
                h += 1
                uncompressed.append(x)
        print('h', h)
        return compressed, uncompressed

    @staticmethod
    def filter_values(bitStream, lib_dict):
        count = 0
        h = 0
        comp, unc = [], []
        tes = ''
        bitStream += ' '
        while count < len(bitStream) - 1:
            compressor = 1
            stringLength = bitStream[count:count + compressor]
            while stringLength in lib_dict:
                compressor += 1
                stringLength = bitStream[count:count + compressor]
            stringLength = bitStream[count:count + compressor - 1]
            if len(stringLength) >= 6:
                if tes != '':
                    unc.append(tes)
                    comp.append(0)
                    h += 1
                    tes = ''
                comp.append(lib_dict[stringLength])
                count += len(stringLength)
            else:
                tes += stringLength
                count += 1
        if tes != '':
            unc.append(tes)
            comp.append(0)
            h += 1
        return comp, unc, h

    @staticmethod
    def layer_three_compressed(uncompressed, lib):
        compressed = []
        for x in uncompressed:
            len_of_x = len(x)
            if x == lib:
                compressed.append('101')
            elif len_of_x <= 5:
                z = MiddleOut.__getliteral(x)
                compressed.append(z)
        return compressed

    @staticmethod
    def __getliteral(lis):
        len_of_lis = len(lis)
        if len_of_lis == 1:
            return MiddleOutUtils.get_literal_small(lis)
        elif len_of_lis <= 5:
            return MiddleOutUtils.get_literal(lis)
        else:
            return MiddleOutUtils.get_literal(lis[:5]) + MiddleOut.__getliteral(lis[5:])

    @staticmethod
    def merge_compressed(first_layer, second_layer, third_layer):
        for x in range(len(third_layer)):
            if second_layer[x] == 0:
                second_layer[x] = third_layer.pop(0)
        for x in range(len(first_layer)):
            if first_layer[x] == 0:
                first_layer[x] = second_layer.pop(0)
        return ''.join(first_layer)
