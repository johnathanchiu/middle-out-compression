from middleOut.MiddleOut import *
from middleOut.EntropyReduction import *

import unittest

import random
import time


class TestMiddleOut:

    @staticmethod
    def check_differences(a, b, array=True):
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
        if array:
            print("arrays are the same")
        else:
            print("bitsets are the same")

    @staticmethod
    def generate_random_bitset(bitset_size, set_seed=False, seed=0):
        x, y = [], []
        if (set_seed):
            random.seed(seed)
        for _ in range(bitset_size):
            tem = random.randint(0, 50)
            x.append(tem)
            y.append(tem)
        return MiddleOutUtils.convertBin_list(x), y

    @staticmethod
    def test_random_mo(bitset_size, set_seed=False, seed=0):
        x = []
        if (set_seed):
            random.seed(seed)
        for _ in range(bitset_size):
            tem = random.randint(0, 30)
            x.append(tem)
        return MiddleOut.middle_out(x)

    @staticmethod
    def run_middleout(bytes):
        return MiddleOut.middle_out(bytes, size=3, debug=True)

    @staticmethod
    def run_middelout_decomp(bits):
        return MiddleOut.middle_out_decompress(bits, debug=True)

if __name__ == '__main__':
    start_time = time.time()
    # test = [1, 2, 1, 2, 4, 5, 6, 7, 8, 9, 10]
    test = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 2, 1, 1, 2, 2, 2]
    # test = [255, 216, 255, 224, 0, 16, 74, 70, 73, 70]
    # test[:] = [b-128 for b in test]
    print("size before middleout", len(test), "(bytes)", ", ", len(test) * 8, "(bits)")
    c = TestMiddleOut.run_middleout(test)
    print("size of middleout", len(c))
    de = TestMiddleOut.run_middelout_decomp(c)
    print("decompressed", de, "original", test)
    TestMiddleOut.check_differences(test, de)
    print("--- %s seconds ---" % (time.time() - start_time))

