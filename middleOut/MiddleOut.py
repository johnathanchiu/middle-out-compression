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
        count = 0
        length = len(uncompressed)
        while count < length - 8:
            partition = uncompressed[count:count + 8]
            if partition not in dictionary:
                dictionary[partition] = 1
            else:
                dictionary[partition] += 1
            count += 1
        return MiddleOutUtils.keywithmaxval(dictionary)

    @staticmethod
    def build_library2(uncompressed, size=8):
        dictionary = {}
        for x in uncompressed:
            partition = uncompressed[count:count + 8]
            if partition not in dictionary:
                dictionary[partition] = 1
            else:
                dictionary[partition] += 1
            count += 1
        return MiddleOutUtils.keywithmaxval(dictionary)

    @staticmethod
    def build_dict(bit_lib, sets=0):
        if sets == 1:
            return {bit_lib: '101', bit_lib[:6]: '110' + format(0, '01b'), bit_lib[:7]: '110' + format(1, '01b')}
        return {bit_lib: '00', bit_lib[:6]: '01' + format(0, '01b'), bit_lib[:7]: '01' + format(1, '01b')}

    @staticmethod
    def decompressStream(compressed):
        uncompressed = ''
        new_run = True
        x, count = 0, 0
        while x < len(compressed):
            if new_run:
                eight_lib = compressed[x:x+8]
                eight_lib_s = compressed[x+8:x+16]
                new_run = False
                x += 16
            if compressed[x] == '0':
                if compressed[x+1] == '1':
                    uncompressed += eight_lib
                    x += 1
                else:
                    uncompressed += eight_lib_s
            # elif uncompressed[x:x+2] == '10':
            #     if uncompressed[x+2] ==  '1':
            #         uncompressed += eight_lib_s
            #         x += 3
            #     else:
            #         uncompressed += eight_lib
            # elif uncompressed[x:x+3] == '110':
            elif compressed[x:x+7] == '1111110':
                new_run = True
                x += 6
        return uncompressed

    @staticmethod
    def eight_bit_compression(uncompressed, lib):
        count = 0
        temp = ''
        compressed, unc = [], []
        uncompressed += ' '
        total_count, count = 0, 0
        compression_lib = MiddleOut.build_dict(lib)
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
                compressed.append(compression_lib[mo])
                count += length_string
            else:
                temp += uncompressed[count]
                count += 1
                total_count += 1
        if temp != '':
            unc.append(temp)
        print("total count", total_count)
        return compressed, unc

    @staticmethod
    def eight_bit_compression2(bitStream, lib_dict):
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
        middle_comp, unc = MiddleOut.eight_bit_compression(stream)
        eight_bit = MiddleOut.build_library(unc)
        outer_comp = MiddleOut.eight_bit_compression(unc, eight_bit)
        y = MiddleOut.merge_compression(middle_comp, outer_comp)
        return eight_bit + y + '1111110'
