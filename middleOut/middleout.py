from operator import itemgetter
import lz4.frame as lz

class MiddleOutUtils:
    @staticmethod
    def convertBin(num, bits=8):
        def bindigits(val, bits=8):
            s = bin(val & int("1" * bits, 2))[2:]
            return ("{0:0>%s}" % (bits)).format(s)
        return bindigits(num, bits=bits)

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
    def rearrange_bin(compressed_values):
        compressed_ac = []
        compressed_dc = []
        for x in range(0, len(compressed_values), 2):
            compressed_dc.append(compressed_values[x])
            compressed_ac.append(compressed_values[x + 1])
        return compressed_ac, compressed_dc

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
        return '01' + MiddleOutUtils.convertBin(len(stream) - 2, bits=2) + stream

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
        x = 0
        while x < len(compressed):
            if new_run:
                eight_lib = compressed[x:x+8]
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
                    return
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
                uncompressed += eight_lib[x:x+MiddleOutUtils.convertInt(compressed[x+4:x+7], bits=3)]
                x += 4
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
        return compression_dict

    @staticmethod
    def layer_one_compression(uncompressed):
        x = 0
        res = ''
        a = len(uncompressed)
        count = 0
        count0 = 0
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
                    partial_decomp.append('10' + header)
                    x += counter
                    a -= (counter - 5)
                    count0 += 1
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
        print(a)
        print("count", count)
        print(count0)
        return partial_decomp, uncomp_partition

    @staticmethod
    def layer_two_compression(uncompressed_list, lib):
        compressed, uncompressed = [], []
        bc = ''
        a = 0
        for x in uncompressed_list:
            len_of_x = len(x)
            if len_of_x == 1:
                compressed.append(MiddleOutUtils.get_literal_small(x))
                a += 2
            elif len_of_x <= 5:
                compressed.append(MiddleOutUtils.get_literal(x))
                a += (len_of_x + 4)
            elif len_of_x >= 8:
                y = 0
                while y < len_of_x:
                    par = x[y:y+8]
                    if par == lib:
                        if bc != '':
                            compressed.append(0)
                            uncompressed.append(bc)
                            bc = ''
                        compressed.append('11110')
                        a -= 3
                        y += 8
                    else:
                        bc += x[y]
                        y += 1
                if bc != '':
                    compressed.append(0)
                    uncompressed.append(bc)
                    bc = ''
            else:
                compressed.append(0)
                uncompressed.append(x)
        print(a)
        return compressed, uncompressed

    @staticmethod
    def filter_values(bitStream, lib_dict):
        comp, tes = '', ''
        count = 0
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
                    comp += MiddleOut.__helper(tes)
                    tes = ''
                comp += lib_dict[stringLength]
                count += len(stringLength)
            else:
                tes += bitStream[count]
                count += 1
        if tes != '':
            comp += MiddleOut.__helper(tes)
        return comp

    @staticmethod
    def __helper(lis):
        len_of_lis = len(lis)
        if len_of_lis == 1:
            return MiddleOutUtils.get_literal_small(lis)
        elif len_of_lis <= 5:
            return MiddleOutUtils.get_literal(lis)
        else:
            return MiddleOutUtils.get_literal(lis[:5]) + MiddleOut.__helper(lis[5:])

    @staticmethod
    def merge_compressed(first_layer, second_layer):
        for x in range(len(first_layer)):
            if first_layer[x] == 0:
                first_layer[x] = second_layer.pop(0)
        return ''.join(first_layer)


class EntropyReduction:
    @staticmethod
    def wheeler_transform(s):
        n = len(s)
        m = sorted([s[i:n] + s[0:i] for i in range(n)])
        I = m.index(s)
        L = []
        L.extend([q[-1] for q in m])
        return I, L

    @staticmethod
    def wheeler_inverse(L, I=2):
        n = len(L)
        X = sorted([(i, x) for i, x in enumerate(L)], key=itemgetter(1))

        T = [None for i in range(n)]
        for i, y in enumerate(X):
            j, _ = y
            T[j] = i

        Tx = [I]
        for i in range(1, n):
            Tx.append(T[Tx[i - 1]])

        S = [L[i] for i in Tx]
        S.reverse()
        return S

    @staticmethod
    def lz4_compress(values):
        with lz.LZ4FrameCompressor() as compressor:
            compressed = compressor.begin()
            compressed += compressor.compress(bytes(values))
            compressed += compressor.flush()
        return list(compressed)

    @staticmethod
    def lz4_decompress(values):
        values = bytes(values)
        with lz.LZ4FrameDecompressor() as decompressor:
            decompressed = decompressor.decompress(values)
        return list(decompressed)

    @staticmethod
    def __countzero(part_stream):
        count = 0
        for y in part_stream:
            if y == 0:
                count += 1
            else:
                break
        return count

    @staticmethod
    def __countone(part_stream):
        count = 0
        for y in part_stream:
            if y == '1':
                count += 1
            else:
                break
        return count

    @staticmethod
    def rle(stream):
        run_length = []
        x = 0
        while x < len(stream):
            if stream[x] == 0:
                run_length.append(0)
                count_zero = EntropyReduction.__countzero(stream[x:])
                run_length.append(count_zero)
                x += count_zero
            else:
                run_length.append(stream[x])
                x += 1
        return run_length

    @staticmethod
    def rld(stream):
        decoded = []
        count = 0
        while count < len(stream):
            if stream[count] == 0:
                for x in range(stream[count + 1]):
                    decoded.append(0)
                count += 1
            else:
                decoded.append(stream[count])
                count += 1
            count += 1
        return decoded

    @staticmethod
    def rle_bit(stream):
        run_length = []
        x = 0
        while x < len(stream):
            if stream[x] == '0':
                run_length.append(0)
                count_zero = EntropyReduction.__countzero(stream[x:])
                run_length.append(count_zero)
                x += count_zero
            elif stream[x] == '1':
                run_length.append(1)
                count_one = EntropyReduction.__countone(stream[x:])
                run_length.append(count_one)
                x += count_one
        return run_length

    @staticmethod
    def rld_bit(stream):
        decoded = []
        count = 0
        while count < len(stream):
            if stream[count] == 0:
                for x in range(stream[count + 1]):
                    decoded.append('0')
                count += 1
            else:
                for x in range(stream[count + 1]):
                    decoded.append('1')
                count += 1
            count += 1
        return ''.join(decoded)
