from middleOut.EntropyReduction import *
from JPEG.utils import *

import numpy as np

from operator import itemgetter
import lz4.frame as lz
import bz2

import struct
import sys
import os


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

    @staticmethod
    def bz2(compressed, output_file):
        def bz2_comp(output, output_file):
            filename = output_file + ".bz2"
            with bz2.open(filename, "wb") as f:
                output = bz2.compress(output, 9)
                f.write(output)
            return os.path.getsize(filename), filename
        compressed = (struct.pack('b' * len(compressed), *compressed))
        size, filename = bz2_comp(compressed, output_file)
        return size, filename

    @staticmethod
    def bz2_unc(file_name):
        def bz2_decomp(file):
            with bz2.open(file, "rb") as f:
                f_content = f.read()
                f_content = bz2.decompress(f_content)
            return f_content

        result_bytes = bz2_decomp(file_name + '.bz2')
        fmt = "%db" % len(result_bytes)
        result_bytes = np.asarray(list(struct.unpack(fmt, result_bytes)))
        return result_bytes

    @staticmethod
    def rle_encoding(x):
        """
        x: numpy array of shape (height, width), 1 - mask, 0 - background
        Returns run length as list
        """
        dots = np.where(x.T.flatten() == 1)[0]  # .T sets Fortran order down-then-right
        run_lengths = []
        prev = -2
        for b in dots:
            if b > prev + 1:
                run_lengths.extend((b + 1, 0))
            run_lengths[-1] += 1
            prev = b
        return run_lengths