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

    # TODO: add get-literal functions
    # TODO: check literal functions
    @staticmethod
    def get_literal_long(stream):
        return '11110' + MiddleOutUtils.convertBin(len(stream), bits=6) + stream

    @staticmethod
    def get_literal(stream):
        return '100' + MiddleOutUtils.convertBin(len(stream) - 3, bits=2) + stream

    @staticmethod
    def get_literal_small(stream):
        return '00' + MiddleOutUtils.convertBin(len(stream) - 1, bits=1) + stream

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
        uncompressed = ''
        new_run = True
        x, count = 0, 0
        while x < len(compressed):
            if new_run:
                eight_lib = compressed[x:x+8]
                four_lib = compressed[x+8:x+12]
                new_run = False
                x += 12
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
                if compressed[x+2] == '1':
                    uncompressed += four_lib
                    x += 3
                else:
                    num = MiddleOutUtils.convertInt(compressed[x+3:x+5]) + 3
                    uncompressed += compressed[x + 5: x + 5 + num]
                    x += num + 5
            elif compressed[x:x+3] == '110':
                for _ in range(MiddleOutUtils.convertInt(compressed[x+3:x+5]) + 6):
                    uncompressed += '1'
                x += 5
            elif compressed[x:x+5] == '11110':
                uncompressed += eight_lib
                x += 5
            # TODO: Make sure this library is correct
            elif compressed[x:x+4] == '1110':
                uncompressed += eight_lib[x:x + MiddleOutUtils.convertInt(compressed[x + 4])]
                x += 5
            elif compressed[x:x+6] == '111110':
                new_run = True
                x += 6
        # TODO: add extra libraries for the literals
        return uncompressed

    @staticmethod
    def build_library(uncompressed, size=8):
        dictionary = {}
        if size == 8:
            for x in uncompressed:
                len_of_x = len(x)
                if len_of_x >= size:
                    for y in range(len_of_x - size + 1):
                        par = x[y:y+size]
                        if par not in dictionary:
                            dictionary[par] = 1
                        else:
                            dictionary[par] += 1
        else:
            for x in uncompressed:
                if x == 1 or x == 0:
                    continue
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
    def zero_one_filter(uncompressed):
        x = 0
        res = ''
        a = len(uncompressed)
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
                    a -= (counter - 5)
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
                    a -= (counter - 5)
                else:
                    res += uncompressed[x]
                    x += 1
        if res != '':
            partial_decomp.append(0)
            uncomp_partition.append(res)
        return partial_decomp, uncomp_partition

    @staticmethod
    def eight_bit_compression(uncompressed_list, lib):
        compressed, uncompressed = [], []
        lib_dict = MiddleOut.build_dict(lib)
        for x in uncompressed_list:
            len_of_x = len(x)
            if len_of_x <= 2:
                compressed.append(MiddleOutUtils.get_literal_small(x))
                compressed.append(0)
            elif len_of_x >= 8:
                comp, unc = MiddleOut.filter_values(x, lib_dict)
                compressed.extend(comp)
                uncompressed.extend(unc)
            else:
                compressed.append(0)
                uncompressed.append(x)
        return compressed, uncompressed

    @staticmethod
    def filter_values(bitStream, lib_dict):
        comp, unc = [], []
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
                    unc.append(res)
                    unc.append(1)
                    comp.append(1)
                    res = ''
                comp.append(lib_dict[stringLength])
                count += length_string
            else:
                res += bitStream[count]
                count += 1
        if res != '':
            unc.append(res)
            comp.append(1)
        unc.append(0)
        return comp, unc

    # # TODO: find better way to compress literals, need to use less bits
    # @staticmethod
    # def four_bit_compression(uncompressed, lib):
    #     compressed, res = [], ''
    #     for x in uncompressed:
    #         if x == 1 or x == 0:
    #             compressed.append(x)
    #             continue
    #         len_of_x = len(x)
    #         if x == lib:
    #             compressed.append('101')
    #         elif len_of_x >= 5:
    #             y = 0
    #             while y < len_of_x:
    #                 if x[y:y+4] == lib:
    #                     if res != '':
    #                         compressed.append(MiddleOut.getliteral(res) + '101')
    #                         res = ''
    #                     else:
    #                         compressed.append('101')
    #                     y += 4
    #                 else:
    #                     res += x[y]
    #                     y += 1
    #             if res != '':
    #                 compressed[len(compressed) - 1] += MiddleOut.getliteral(res)
    #         else:
    #             compressed.append(MiddleOut.getliteral(res))
    #         res = ''
    #     return compressed

    @staticmethod
    def getliteral(lis):
        len_of_lis = len(lis)
        if len_of_lis <= 2:
            return MiddleOutUtils.get_literal_small(lis)
        elif len_of_lis <= 6:
            return MiddleOutUtils.get_literal(lis)
        else:
            return MiddleOutUtils.get_literal(lis[:6]) + MiddleOut.getliteral(lis[6:])

    @staticmethod
    def merge_compression(layer_one, layer_two, layer_three):
        layer_three.append(0)
        temp = []
        count, ext, temp_count = 0, 0, 0
        print(len(layer_one), len(layer_two), len(layer_three))
        for x in range(len(layer_two) - 1):
            print(temp)
            if layer_two[x] == 0:
                print(layer_three[count])
                temp.append(layer_three[count])
                ext = layer_three[count + 1]
                count += 1
                temp_count += 1
            elif layer_two[x] == 1:
                # print("temp", temp[count-1])
                temp[temp_count - 1] += layer_three[count]
                ext = layer_three[count + 1]
                count += 1
            else:
                if ext == 1:
                    temp[temp_count - 1] += layer_two[x]
                    ext = layer_three[count + 1]
                    count += 1
                else:
                    temp.append(layer_two[x])
        count = 0
        for x in range(len(layer_one)):
            if layer_one[x] == 0:
                layer_one[x] = temp[count]
                count += 1
        return ''.join(layer_one)
