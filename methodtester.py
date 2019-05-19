from middleOut.MiddleOut import *
from middleOut.EntropyReduction import *

import unittest

import random
import time


class TestMiddleOut:

    @staticmethod
    def check_differences(a, b):
        counter = len(a)
        if len(a) != len(b):
            print("wrong lengths")
            counter = len(a) if len(a) > len(b) else len(b)
        count = 0
        while count < counter:
            if a[count] != b[count]:
                print("error starts here: ", b[count:])
                return
            count += 1
        print("bitsets are the same")

    @staticmethod
    def generate_random_bitset(bitset_size, set_seed=False, seed=0):
        x, y = [], []
        if (set_seed):
            random.seed(seed)
        for _ in range(bitset_size):
            tem = random.randint(-128, 127)
            x.append(tem)
            y.append(tem)
        return x, y
        x = MiddleOutUtils.convertBin_list(x)
        return x, y

    @staticmethod
    def test_middleout(bitset_size, set_seed=False, seed=0):
        x = []
        # bztest = []
        if (set_seed):
            random.seed(seed)
        for _ in range(bitset_size):
            tem = random.randint(0, 30)
            x.append(tem)
            # bztest.append(tem)

        x = MiddleOutUtils.convertBin_list(x)
        comp = MiddleOut.middle_out(x)
        z = MiddleOut.decompressStream(comp)
        print("compressed bits: ", bitset_size - len(comp))
        return x, z

    @staticmethod
    def test_eight_compression(bitset):
        lib = MiddleOut.build_library(bitset, size=8)
        return MiddleOut.eight_bit_compression(bitset, lib)

    @staticmethod
    def test_eight_second_compression(unc):
        lib = MiddleOut.build_library2(unc, size=8)
        return MiddleOut.eight_bit_compression2(unc, lib)

    @staticmethod
    def test_rle(stream):
        stream = np.asarray(stream)
        return EntropyReduction.rle_encoding(stream)


if __name__ == '__main__':
    start_time = time.time()
    bitset, test_list = TestMiddleOut.generate_random_bitset(10000, set_seed=True, seed=10)
    # EntropyReduction.bz2(test_list, '/Users/johnathanchiu/Downloads/test')
    compressed, unc = TestMiddleOut.test_eight_compression(bitset)
    print(len(''.join(compressed)))
    compressed2, unc2 = TestMiddleOut.test_eight_second_compression(unc)
    # print(len(''.join(compressed2)))
    # print(len(''.join(unc2)))
    # bitseta, bitsetb = TestMiddleOut.test_middleout(100000, set_seed=True, seed=10)
    # TestMiddleOut.check_differences(bitseta, bitsetb)

    print("--- %s seconds ---" % (time.time() - start_time))

