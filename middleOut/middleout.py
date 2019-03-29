from operator import itemgetter
import lz4.frame as lz

class MiddleOutUtils:
    @staticmethod
    def convertBin(intList):
        def bindigits(val, bits=8):
            s = bin(val & int("1" * bits, 2))[2:]
            return ("{0:0>%s}" % (bits)).format(s)
        binary = ''
        for x in intList:
            binary += bindigits(x)
        return binary

    @staticmethod
    def convertInt(binary):
        def two_complement(binary, bits=8):
            binary = int(binary, 2)
            """compute the 2's complement of int value val"""
            if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
                binary = binary - (1 << bits)  # compute negative value
            return binary  # return positive value as is
        intList = []
        for x in range(0, len(binary), 8):
            intList.append(two_complement(binary[x:x+8]))
        return intList

    @staticmethod
    def convertInt_comp(binr, bits=2):
        def two_complement(binary, bits=8):
            binary = int(binary, 2)
            """compute the 2's complement of int value val"""
            if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
                binary = binary - (1 << bits)  # compute negative value
            return binary  # return positive value as is
        return two_complement(binr, bits=bits)

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
    def convert_bin(num, three=True):
        def bindigits(val, bits=3):
            s = bin(val & int("1" * bits, 2))[2:]
            return ("{0:0>%s}" % (bits)).format(s)
        if three:
            return bindigits(num)
        return bindigits(num, bits=2)


class MiddleOut:
    @staticmethod
    def compressStream(bitStream, dictionary):
        # compressed = ''
        # count = 0
        # bitStream += ' '
        # while count < len(bitStream)-1:
        #     compressor = 1
        #     stringLength = bitStream[count:count + compressor]
        #     while stringLength in dictionary:
        #         compressor += 1
        #         stringLength = bitStream[count:count + compressor]
        #     if len(stringLength) < 7:
        #         compressed += '0' + bitStream[count:count + 7]
        #         count += 7
        #     else:
        #         compressor -= 1
        #         stringLength = bitStream[count:count + compressor]
        #         compressed += dictionary[stringLength]
        #         count += compressor
        # return compressed
        return

    @staticmethod
    def decompressStream(compressed):
        uncompressed = ''
        temp = []
        x = 0
        while x < len(compressed):
            if compressed[x] == '0':
                uncompressed += compressed[x+1:x+8]
            elif compressed[x:x+1] == '10':
                [temp.append('0') for _ in range(MiddleOutUtils.convertInt_comp(compressed[x+1:x+3], 3))]
                uncompressed.join(temp)
                temp = []
            elif compressed[x:x+2] == '110':
                [temp.append('1') for _ in range(MiddleOutUtils.convertInt_comp(compressed[x+2:x+4], 2))]
                uncompressed.join(temp)
                temp = []
        return uncompressed

    @staticmethod
    def build_library(uncompressed):
        dictionary = {}
        for x in uncompressed:
            if len(x) >= 8:
                for y in range(x - 8):
                    par = x[y:y+8]
                    if par not in dictionary:
                        dictionary[par] = 1
                    else:
                        dictionary[par] += 1
        return dictionary

    @staticmethod
    def pop_zero_one(uncompressed):
        def count_zero(part_stream):
            count = 0
            for y in part_stream:
                if y == '0':
                    if count >= 13:
                        break
                    count += 1
                else:
                    break
            return count

        def count_one(part_stream):
            count = 0
            for y in part_stream:
                if y == '1':
                    if count >= 9:
                        break
                    count += 1
                else:
                    break
            return count

        x = 0
        res = ''
        partial_decomp = []
        uncomp_partition = []
        while x < len(uncompressed):
            if uncompressed[x] == '0':
                counter = count_zero(uncompressed[x:])
                if counter >= 6:
                    if res != '':
                        partial_decomp.append('0' + res)
                        uncomp_partition.append(res)
                        res = ''
                    header = MiddleOutUtils.convert_bin(counter - 6)
                    partial_decomp.append('10' + header)
                    x += counter
                else:
                    res += uncompressed[x:x+1]
                    x += 1
            elif uncompressed[x] == '1':
                counter = count_one(uncompressed[x:])
                if counter >= 6:
                    if res != '':
                        partial_decomp.append('0' + res)
                        uncomp_partition.append(res)
                        res = ''
                    header = MiddleOutUtils.convert_bin(counter - 6, three=False)
                    partial_decomp.append('110' + header)
                    x += counter
                else:
                    res += uncompressed[x:x + 1]
                    x += 1
        return ''.join(partial_decomp), uncomp_partition

    @staticmethod
    def build_dict(bit_lib):
        compression_dict = {}
        for x in range(len(bit_lib)):
            compression_dict[bit_lib[:x + 1]] = '0' + format(x, "03b")
        return compression_dict


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
    def rle_bit(stream):
        def count_zero(part_stream):
            count = 0
            for y in part_stream:
                if y == 0:
                    count += 1
                else:
                    break
            return count

        def count_one(part_stream):
            count = 0
            for y in part_stream:
                if y == '1':
                    count += 1
                else:
                    break
            return count

        run_length = []
        x = 0
        while x < len(stream):
            if stream[x] == '0':
                run_length.append(0)
                countzero = count_zero(stream[x:])
                run_length.append(countzero)
                x += countzero
            elif stream[x] == '1':
                run_length.append(1)
                countone = count_one(stream[x:])
                run_length.append(countone)
                x += countone
        return run_length

    @staticmethod
    def rle(stream):
        def count_zero(part_stream):
            count = 0
            for y in part_stream:
                if y == 0:
                    count += 1
                else:
                    break
            return count

        run_length = []
        x = 0
        while x < len(stream):
            if stream[x] == 0:
                run_length.append(0)
                countzero = count_zero(stream[x:])
                run_length.append(countzero)
                x += countzero
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
